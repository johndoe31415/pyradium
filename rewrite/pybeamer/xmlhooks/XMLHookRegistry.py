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

from pybeamer.Exceptions import XMLHookRegistryException
from pybeamer.Tools import XMLTools


class XMLHookRegistry():
	_HOOKS = { }
	_SPECIAL = set([ "var", "pause", "content" ])

	@classmethod
	def register_hook(cls, hook_class):
		if hook_class._TAG_NAME is None:
			raise XMLHookRegistryException("Hook name is not set in hook class: %s" % (hook_class))
		if hook_class._TAG_NAME in cls._HOOKS:
			raise XMLHookRegistryException("Duplicate hook name: %s" % (hook_class))
		cls._HOOKS[hook_class._TAG_NAME] = hook_class
		return hook_class

	@classmethod
	def mangle(cls, root_node):
		def callback(node):
			if (node.nodeType == node.ELEMENT_NODE) and (node.nodeName.startswith("s:")):
				hook_name = node.nodeName[2:]
				if hook_name not in cls._SPECIAL:
					if hook_name in cls._HOOKS:
						hook_class = cls._HOOKS[hook_name]
						replace_by = hook_class.handle(node)
						if replace_by is None:
							# Delete node
							XMLTools.remove_node(node)
						else:
							XMLTools.replace_node(node, replace_by)
					else:
						print("Warning: Unknown hook '%s' used in source document." % (hook_name))
		XMLTools.walk(root_node, callback)

class BaseHook():
	_TAG_NAME = None

	@classmethod
	def handle(cls, node):
		raise NotImplementedError(__class__.__name__)

class ReplacementHook(BaseHook):
	_REPLACEMENTS = None

	@classmethod
	def handle(cls, node):
		text = XMLTools.inner_text(node).strip()
		if text not in cls._REPLACEMENTS:
			print("Warning: %s(%s) not available. Ignored the sequence." % (cls._TAG_NAME, text))
			return None
		else:
			replacement_text = cls._REPLACEMENTS[text]
			replacement_node = node.ownerDocument.createTextNode(replacement_text)
			return replacement_node

