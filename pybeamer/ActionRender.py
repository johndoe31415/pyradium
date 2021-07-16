#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import sys
from .BaseAction import BaseAction
from .Presentation import Presentation
from .RenderingParameters import RenderingParameters
from .PresentationRenderer import PresentationRenderer

class ActionRender(BaseAction):
	def run(self):
		if (not self._args.force) and os.path.exists(self._args.outdir):
			print("Refusing to overwrite: %s" % (self._args.outdir))
			return 1

		presentation = Presentation.load_from_file(self._args.infile)
		rendering_parameters = RenderingParameters(
				template_style = self._args.template_style,
				honor_pauses = not self._args.remove_pauses,
				presentation_mode = self._args.presentation_mode,
				extra_template_dirs = self._args.template_dir,
				include_dirs = [ os.path.dirname(self._args.infile) ] + self._args.include_dir,
				index_filename = self._args.index_filename,
				geometry = self._args.geometry,
				image_max_dimension = self._args.image_max_dimension)
		renderer = PresentationRenderer(presentation, rendering_parameters)
		rendered_presentation = renderer.render(deploy_directory = self._args.outdir)
