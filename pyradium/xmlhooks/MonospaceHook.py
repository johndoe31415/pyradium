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

@XMLHookRegistry.register_hook
class MonospaceHook(BaseHook):
	_TAG_NAME = "tt"

	@classmethod
	def handle(cls, rendered_presentation, node):
		replacement_node = node.ownerDocument.createElement("span")
		replacement_node.setAttribute("class", "tt")

		# Need the copy of the child dictionary here otherwise we'll miss
		# children
		for child in list(node.childNodes):
			replacement_node.appendChild(child)

		return replacement_node
