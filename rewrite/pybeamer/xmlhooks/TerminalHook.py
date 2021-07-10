#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

import textwrap
from pybeamer.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pybeamer.Tools import XMLTools

@XMLHookRegistry.register_hook
class TerminalHook(BaseHook):
	_TAG_NAME = "term"

	@classmethod
	def handle(cls, rendered_presentation, node):
		if node.hasAttribute("src"):
			with open(rendered_presentation.renderer.get_include(node.getAttribute("src"))) as f:
				term_text = f.read()
		else:
			term_text = XMLTools.inner_text(node)


		term_text = term_text.strip("\n")
		term_text = textwrap.dedent(term_text)
		term_text = term_text.strip("\n")

		replacement_node = node.ownerDocument.createElement("pre")
		replacement_node.setAttribute("class", "terminal")
		replacement_node.appendChild(node.ownerDocument.createTextNode(term_text))

		return replacement_node
