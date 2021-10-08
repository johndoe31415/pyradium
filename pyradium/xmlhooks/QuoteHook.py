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
class QuoteHook(BaseHook):
	_TAG_NAME = "enq"

	@classmethod
	def handle(cls, rendered_presentation, node):
		text = XMLTools.inner_text(node).strip()
		style = {
			"fr":	"«»",
			"de":	"„“",
			"sgl":	"‘’",
		}.get(node.getAttribute("type"), "“”")
		replacement_text = style[0] + text + style[1]
		replacement_node = node.ownerDocument.createTextNode(replacement_text)
		return replacement_node
