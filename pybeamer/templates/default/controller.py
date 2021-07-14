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

class TOCController(BaseController):
	_TOC_ITEMS_PER_SLIDE = 8

	def render(self):
		toc = self.rendered_presentation.frozen_toc
		if toc is not None:
			start_at = self.slide.get_xml_slide_var("start_at")
			end_before = self.slide.get_xml_slide_var("end_before")
			toc_item_count = toc.count_toc_items(start_at = start_at, end_before = end_before)


			toc_slide_count = (toc_item_count + self._TOC_ITEMS_PER_SLIDE - 1) // self._TOC_ITEMS_PER_SLIDE
			for toc_slide_index in range(toc_slide_count):
				subset = list(toc.subset(start_at = start_at, end_before = end_before, max_items = self._TOC_ITEMS_PER_SLIDE))
				start_at = subset[-1].index + 1
				additional_slide_vars = {
					"partial_toc":	toc.emit_commands(subset),
				}
				yield from self.slide.emit_slide(self.rendered_presentation, self.content_containers, additional_slide_vars)

class AcronymController(BaseController):
	_ACRONYMS_PER_SLIDE = 8

	def render(self):
		acronyms = self.rendered_presentation.renderer.get_custom_renderer("acronym")
		used_acronyms = list(acronyms.get_all_used_acronyms())
		pages = (len(used_acronyms) + self._ACRONYMS_PER_SLIDE - 1) // self._ACRONYMS_PER_SLIDE
		for page in range(pages):
			page_content = used_acronyms[page * self._ACRONYMS_PER_SLIDE : (page + 1) * self._ACRONYMS_PER_SLIDE]
			yield from self.slide.emit_slide(self.rendered_presentation, self.content_containers, { "acronyms": page_content })
