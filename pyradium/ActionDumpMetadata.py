#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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
import json
import logging
from .BaseAction import BaseAction
from .RenderingParameters import RenderingParameters
from .Presentation import Presentation

_log = logging.getLogger(__spec__.name)

class ActionDumpMetadata(BaseAction):
	def run(self):
		if self._args.inject_metadata is None:
			injected_metadata = None
		else:
			with open(self._args.inject_metadata) as f:
				injected_metadata = json.load(f)
				_log.debug("Injected metadata: %s", str(injected_metadata))

		rendering_parameters = RenderingParameters(
				include_dirs = [ os.path.dirname(self._args.infile) or "." ] + self._args.include_dir,
				injected_metadata = injected_metadata)
		presentation = Presentation.load_from_file(self._args.infile, rendering_parameters)

		if self._args.pretty_print:
			print(json.dumps(presentation.meta, indent = 4, sort_keys = True))
		else:
			print(json.dumps(presentation.meta, separators = (",", ":")))
