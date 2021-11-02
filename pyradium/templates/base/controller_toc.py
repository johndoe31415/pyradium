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

class TOCController(BaseController):
	@property
	def toc_items_per_slide(self):
		return self._options["toc_items_per_slide"]

	def render(self):
		toc = self.rendered_presentation.frozen_toc
		if toc is not None:
			start_at = self.slide.get_xml_slide_var("start_at")
			end_before = self.slide.get_xml_slide_var("end_before")
			toc_item_count = toc.count_toc_items(start_at = start_at, end_before = end_before)
			toc_slide_count = (toc_item_count + self.toc_items_per_slide - 1) // self.toc_items_per_slide

			additional_slide_var_list = [ ]
			for toc_slide_index in range(toc_slide_count):
				subset = list(toc.subset(start_at = start_at, end_before = end_before, max_items = self.toc_items_per_slide))
				start_at = subset[-1].index + 1
				additional_slide_vars = {
					"partial_toc":	toc.emit_commands(subset),
				}
				additional_slide_var_list.append(additional_slide_vars)
			yield from self.slide.emit_nocontent_slide(self.rendered_presentation, self.content_containers, additional_slide_var_list)
