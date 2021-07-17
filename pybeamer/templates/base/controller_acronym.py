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

from pybeamer.Controller import BaseController

class AcronymController(BaseController):
	@property
	def acronyms_per_slide(self):
		return self._options["acronyms_per_slide"]

	def render(self):
		acronyms = self.rendered_presentation.renderer.get_custom_renderer("acronym")
		used_acronyms = list(acronyms.get_all_used_acronyms())
		pages = (len(used_acronyms) + self.acronyms_per_slide - 1) // self.acronyms_per_slide
		for page in range(pages):
			page_content = used_acronyms[page * self.acronyms_per_slide : (page + 1) * self.acronyms_per_slide]
			yield from self.slide.emit_slide(self.rendered_presentation, self.content_containers, { "acronyms": page_content })
