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

import xml.dom.minidom
import pygments
from pyradium.xmlhooks.XMLHookRegistry import InnerTextHook, XMLHookRegistry
from pyradium.Enums import PresentationFeature
from pyradium.Exceptions import CodeHighlightingException

@XMLHookRegistry.register_hook
class CodeHook(InnerTextHook):
	_TAG_NAME = "code"

	@classmethod
	def handle_text(cls, text, rendered_presentation, node):
		lang = node.getAttribute("lang")
		try:
			lexer = pygments.lexers.get_lexer_by_name(lang)
		except pygments.util.ClassNotFound as e:
			raise CodeHighlightingException(f"Cannot find lexer to syntax highlight code in language '{lang}'.") from e
		highlighted_code = pygments.highlight(text, lexer, pygments.formatters.HtmlFormatter(cssclass = "code_highlight"))

		replacement_node = xml.dom.minidom.parseString(highlighted_code).firstChild
		if node.hasAttribute("height"):
			replacement_node.setAttribute("style", "height: %s" % (node.getAttribute("height")))
		rendered_presentation.add_feature(PresentationFeature.Pygments)
		return replacement_node
