#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
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


from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry, ReplacementFragment
from pyradium.Tools import XMLTools
from pyradium.Exceptions import NoSuchVariableException, CodeExecutionFailedException

@XMLHookRegistry.register_hook
class VariableSubstitutionHook(BaseHook):
	_TAG_NAME = "sub"

	@classmethod
	def handle(cls, rendered_presentation, node):
		if node.hasAttribute("name"):
			# Direct variable
			varname = node.getAttribute("name")
			if varname not in rendered_presentation.renderer.presentation.variables:
				raise NoSuchVariableException(f"No such variable to substitute in s:sub: {varname}")
			value = rendered_presentation.renderer.presentation.variables[varname]
		else:
			code = XMLTools.inner_text(node)
			try:
				exec_globals = {
					"v":	rendered_presentation.renderer.presentation.variables,
				}
				value = eval(code, exec_globals)
			except Exception as e:
				raise CodeExecutionFailedException(f"Code execution failed in in s:sub \"{code}\" with {e.__class__.__name__}: {str(e)}") from e

		value = str(value)
		replacement_node = node.ownerDocument.createTextNode(value)
		return ReplacementFragment(replacement = replacement_node)
