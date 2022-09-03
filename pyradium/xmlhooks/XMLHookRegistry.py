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

import logging
import textwrap
from pyradium.Exceptions import XMLHookRegistryException
from pyradium.Tools import XMLTools

_log = logging.getLogger(__spec__.name)

class XMLHookRegistry():
	_HOOKS = { }
	_SPECIAL = set([ "var", "pause", "content", "param", "format" ])
	_BREAK_DESCENT_ON = set([ "s:verb", "s:term", "s:code" ])

	@classmethod
	def register_hook(cls, hook_class):
		if hook_class._TAG_NAME is None:
			raise XMLHookRegistryException("Hook name is not set in hook class: %s" % (hook_class))
		if hook_class._TAG_NAME in cls._HOOKS:
			raise XMLHookRegistryException("Duplicate hook name: %s" % (hook_class))
		cls._HOOKS[hook_class._TAG_NAME] = hook_class
		return hook_class

	@classmethod
	def _replace_text(cls, text):
		text = text.replace("---", "—")
		text = text.replace("--", "–")
		return text

	@classmethod
	def mangle(cls, rendered_presentation, root_node):
		def callback(node):
			if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName.startswith("s:")):
				hook_name = node.nodeName[2:]
				if hook_name not in cls._SPECIAL:
					if hook_name in cls._HOOKS:
						hook_class = cls._HOOKS[hook_name]
						replace_by = hook_class.handle(rendered_presentation, node)
						if replace_by is None:
							# Delete node
							XMLTools.remove_node(node)
						elif replace_by is node:
							# Keep node
							pass
						else:
							XMLTools.replace_node(node, replace_by)
							continue_descent_with_replaced_elements = node.nodeName not in cls._BREAK_DESCENT_ON
							if continue_descent_with_replaced_elements:
								if not isinstance(replace_by, list):
									XMLTools.walk(replace_by, callback)
								else:
									for new_child in replace_by:
										XMLTools.walk(new_child, callback)
					else:
						_log.warning("Unknown hook '%s' used in source document.", hook_name)
			elif node.nodeType == node.TEXT_NODE:
				text = node.wholeText
				new_text = cls._replace_text(text)
				if text != new_text:
					node.replaceWholeText(new_text)
		XMLTools.walk(root_node, callback)

class BaseHook():
	_TAG_NAME = None

	@classmethod
	def handle(cls, rendered_presentation, node):
		raise NotImplementedError("%s.handle" % (cls.__name__))

class ReplacementHook(BaseHook):
	_REPLACEMENTS = None
	_SPAN_ATTRIBUTES = None

	@classmethod
	def handle(cls, rendered_presentation, node):
		text = XMLTools.inner_text(node).strip()
		if text not in cls._REPLACEMENTS:
			_log.warning("%s(%s) not available. Ignored the sequence.", cls._TAG_NAME, text)
			return None
		else:
			replacement_text = cls._REPLACEMENTS[text]

			text_node = node.ownerDocument.createTextNode(replacement_text)
			if cls._SPAN_ATTRIBUTES is None:
				replacement_node = text_node
			else:
				replacement_node = node.ownerDocument.createElement("span")
				for (key, value) in cls._SPAN_ATTRIBUTES.items():
					replacement_node.setAttribute(key, value)
				replacement_node.appendChild(text_node)

			return replacement_node

class InnerTextHook(BaseHook):
	@classmethod
	def handle_text(cls, text, rendered_presentation, node):
		raise NotImplementedError("%s.handle_text" % (cls.__name__))

	@classmethod
	def handle(cls, rendered_presentation, node):
		if node.hasAttribute("src"):
			with open(rendered_presentation.renderer.lookup_include(node.getAttribute("src"))) as f:
				text = f.read()
		else:
			text = XMLTools.inner_text(node)

		text = text.strip("\n")
		text = textwrap.dedent(text)
		text = text.strip("\n")
		text = text.expandtabs(4)

		return cls.handle_text(text, rendered_presentation, node)
