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
from pyradium.Tools import XMLTools

@XMLHookRegistry.register_hook
class NthHook(BaseHook):
	_TAG_NAME = "nth"

	@classmethod
	def handle(cls, rendered_presentation, node):
		value = int(XMLTools.inner_text(node))
		last_digit = value % 10
		if last_digit == 1:
			suffix = "st"
		elif last_digit == 2:
			suffix = "nd"
		elif last_digit == 3:
			suffix = "rd"
		else:
			suffix = "th"


		replacement_nodes = [
			node.ownerDocument.createTextNode(str(value)),
			node.ownerDocument.createElement("sup"),
		]
		replacement_nodes[1].appendChild(node.ownerDocument.createTextNode(suffix))
		return replacement_nodes
