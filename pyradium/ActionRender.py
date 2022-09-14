#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2022 Johannes Bauer
#
#	This file is part of pyradium.
#
#	pyradium is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pyradium is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pyradium; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import sys
import time
import subprocess
import json
import logging
import traceback
from .BaseAction import BaseAction
from .Presentation import Presentation
from .RenderingParameters import RenderingParameters
from .Renderer import Renderer
from .Exceptions import XMLFileNotFoundException, CallingProcessException, PyRadiumException
from .Enums import PresentationFeature

_log = logging.getLogger(__spec__.name)

class ActionRender(BaseAction):
	_DEFAULT_PRESENTATION_FEATURES = set([ PresentationFeature.Interactive, PresentationFeature.Timer ])

	def _wait_for_change(self, renderer):
		cmd = [ "inotifywait" ]
		cmd += [ "-q", "-r" ]
		cmd += [ "--exclude", r"\..*\.sw[a-z]" ]
		cmd += [ "-e", "modify", "-e", "close_write", "-e", "create" ]

		sources = [ ]
		sources += renderer.presentation.sources
		sources += renderer.rendering_params.template_dirs
		sources += renderer.rendering_params.include_dirs
		sources += self._args.re_render_watch
		sources = [ source for source in sources if os.path.exists(source) ]
		cmd += sources
		proc = subprocess.run(cmd, check = False)
		if proc.returncode not in [ 0, 1 ]:
			raise CallingProcessException("inotifywait returned with returncode %d." % (proc.returncode))

	def _get_presentation_features(self):
		presentation_features = set(self._DEFAULT_PRESENTATION_FEATURES)
		enabled_features = set(PresentationFeature(x) for x in self._args.enable_presentation_feature)
		disabled_features = set(PresentationFeature(x) for x in self._args.disable_presentation_feature)
		overlap = enabled_features & disabled_features
		if len(overlap) > 0:
			print("Presentation feature can not be enabled and disabled at the same time: %s" % (", ".join(sorted(value.name for value in overlap))), file = sys.stderr)
			return None
		presentation_features |= enabled_features
		presentation_features -= disabled_features

		if (PresentationFeature.Timer in presentation_features) and (PresentationFeature.Interactive not in presentation_features):
			_log.warning("The 'timer' feature implies the 'interactive' feature, which has been selected as well.")
			presentation_features.add(PresentationFeature.Interactive)
		return presentation_features

	def run(self):
		presentation_features = self._get_presentation_features()
		if presentation_features is None:
			return 1

		if len(presentation_features) == 0:
			_log.debug("Rendering without any presentation features.")
		else:
			_log.debug("Rendering with features: %s", ", ".join(sorted(value.name for value in presentation_features)))

		if (not self._args.force) and os.path.exists(self._args.outdir):
			print("Refusing to overwrite: %s" % (self._args.outdir), file = sys.stderr)
			return 1

		if self._args.inject_metadata is None:
			injected_metadata = None
		else:
			with open(self._args.inject_metadata) as f:
				injected_metadata = json.load(f)
				_log.debug("Injected metadata: %s", str(injected_metadata))

		if self._args.resource_dir is not None:
			(resource_dir, resource_uri) = self._args.resource_dir
		else:
			(resource_dir, resource_uri) = (self._args.outdir, "")

		renderer = None
		render_success = True
		while True:
			force_wait_secs = None
			try:
				t0 = time.time()
				rendering_parameters = RenderingParameters(
						template_style = self._args.template_style,
						template_style_opts = self._args.style_option,
						honor_pauses = not self._args.remove_pauses,
						collapse_animation = self._args.collapse_animation,
						extra_template_dirs = self._args.template_dir,
						include_dirs = [ os.path.dirname(self._args.infile) or "." ] + self._args.include_dir,
						index_filename = self._args.index_filename,
						resource_uri = resource_uri,
						geometry = self._args.geometry,
						image_max_dimension = self._args.image_max_dimension,
						presentation_features = presentation_features,
						injected_metadata = injected_metadata)
				presentation = Presentation.load_from_file(self._args.infile, rendering_parameters)
				renderer = Renderer(presentation, rendering_parameters)
				rendered_presentation = renderer.render(resource_directory = resource_dir, deploy_directory = self._args.outdir)
				t1 = time.time()
				_log.info("Successfully rendered presentation into directory \"%s\", took %.1f seconds", self._args.outdir, t1 - t0)
			except XMLFileNotFoundException as e:
				# This can happen when we save an XML file in VIM and inotify
				# notifies pyradium too quickly (while the file is still not
				# existent). Then we want to re-render quickly to remedy the issue.
				render_success = False
				_log.error("Rendering failed: [%s] %s", e.__class__.__name__, str(e))
				force_wait_secs = 1
			except PyRadiumException as e:
				render_success = False
				_log.error("Rendering failed: [%s] %s", e.__class__.__name__, str(e))
				if _log.isEnabledFor(logging.DEBUG):
					print(traceback.format_exc())
			if not self._args.re_render_loop:
				break
			if (renderer is None) or (force_wait_secs is not None):
				sleep_duration_secs = force_wait_secs or 5
				_log.warning("Unable to watch files for change since parsing the source was impossible; sleeping for %d seconds instead.", sleep_duration_secs)
				time.sleep(sleep_duration_secs)
			else:
				self._wait_for_change(renderer)
		return 0 if render_success else 1
