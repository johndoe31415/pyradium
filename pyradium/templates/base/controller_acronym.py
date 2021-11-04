#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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

from pyradium.Controller import BaseController

class AcronymController(BaseController):
	@property
	def acronyms_per_slide(self):
		return self._options["acronyms_per_slide"]

	@property
	def chars_per_line(self):
		return self._options.get("chars_per_line", 45)

	def render(self):
		acronyms = self.rendered_presentation.renderer.get_custom_renderer("acronym")
		used_acronyms = list(acronyms.get_all_used_acronyms())
		pages = (len(used_acronyms) + self.acronyms_per_slide - 1) // self.acronyms_per_slide
		additional_slide_var_list = [ ]

		current_page = [ ]
		used_lines = 0
		for acronym in used_acronyms:
			acronym_len = len(acronym.acronym) + 2 + len(acronym.text)
			lines = (acronym_len + self.chars_per_line - 1) // self.chars_per_line
			if (used_lines > 0) and (used_lines + lines > self.acronyms_per_slide):
				# Emit a new page
				used_lines = 0
				additional_slide_var_list.append({ "acronyms": current_page })
				current_page = [ ]
			used_lines += lines
			current_page.append(acronym)

		if len(current_page) > 0:
			# Emit the last page
			additional_slide_var_list.append({ "acronyms": current_page })

		yield from self.slide.emit_nocontent_slide(self.rendered_presentation, self.content_containers, additional_slide_var_list)
