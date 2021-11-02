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

from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Schedule import TimeSpecification

@XMLHookRegistry.register_hook
class TimeHook(BaseHook):
	_TAG_NAME = "time"

	@classmethod
	def handle(cls, rendered_presentation, node):
		abs_string = node.getAttribute("abs") if node.hasAttribute("abs") else None
		rel_string = node.getAttribute("rel") if node.hasAttribute("rel") else None
		time_spec = TimeSpecification.parse(abs_string = abs_string, rel_string = rel_string)
		if rendered_presentation.schedule is not None:
			rendered_presentation.schedule.set_slide_no(rendered_presentation.current_slide_number, time_spec)
		return node
