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

from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Tools import XMLTools
from pyradium.Exceptions import NoAgendaException

@XMLHookRegistry.register_hook
class AgendaHook(BaseHook):
	_TAG_NAME = "agenda"

	@classmethod
	def handle(cls, rendered_presentation, node):
		meta = rendered_presentation.renderer.presentation.meta
		agenda = meta.get("agenda")
		if agenda is None:
			raise NoAgendaException("s:agenda requested but no agenda defined in metadata.")
		replacement_node = node.ownerDocument.createElement("ul")
		for item in agenda:
			li_node = replacement_node.appendChild(node.ownerDocument.createElement("li"))
			li_node.appendChild(node.ownerDocument.createElement("b")).appendChild(node.ownerDocument.createTextNode(f"{item.start_time} - {item.end_time}"))
			li_node.appendChild(node.ownerDocument.createTextNode(f": {item.text}"))
		replacement_node.setAttribute("class", "agenda")
		return replacement_node
