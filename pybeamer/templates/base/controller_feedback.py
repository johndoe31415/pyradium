#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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

import json
import pybeamer
from pybeamer.Controller import BaseController

class FeedbackController(BaseController):
	def render(self):
		slide_info = {
			"source":	self.rendered_presentation.renderer.presentation.version_information,
			"renderer":	pybeamer.VERSION,
		}
		additional_slide_vars = {
			"json_slide_info": json.dumps(slide_info),
		}
		yield from self._slide.emit_nocontent_slide(self.rendered_presentation, additional_slide_vars)
