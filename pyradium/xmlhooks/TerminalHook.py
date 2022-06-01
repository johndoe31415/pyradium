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

from pyradium.xmlhooks.XMLHookRegistry import InnerTextHook, XMLHookRegistry

@XMLHookRegistry.register_hook
class TerminalHook(InnerTextHook):
	_TAG_NAME = "term"

	@classmethod
	def handle_text(cls, text, rendered_presentation, node):
		replacement_node = node.ownerDocument.createElement("pre")
		replacement_node.setAttribute("class", "terminal")
		if node.hasAttribute("prompt"):
			prompt = node.getAttribute("prompt")
			lines = text.splitlines(keepends = True)
			while len(lines) > 0:
				line = lines.pop(0)
				if not line.startswith(prompt):
					replacement_node.appendChild(node.ownerDocument.createTextNode(line))
					continue
				command = line[len(prompt) : ]
				replacement_node.appendChild(node.ownerDocument.createTextNode(prompt))
				while line.strip().endswith("\\"):
					line = lines.pop(0)
					command += line

				# If there is a trailing newline, we do not want this inside
				# the <span> or otherwise the pasted output on the terminal
				# will contain it too
				has_trailing_nl = command.endswith("\n")
				command = command.rstrip("\n")
				command_node = node.ownerDocument.createElement("span")
				command_node.setAttribute("class", "command")
				command_node.appendChild(node.ownerDocument.createTextNode(command))
				replacement_node.appendChild(command_node)

				if has_trailing_nl:
					# In this case we need to insert the newline back into the
					# "normal" (non-copied) text.
					replacement_node.appendChild(node.ownerDocument.createTextNode("\n"))
		else:
			replacement_node.appendChild(node.ownerDocument.createTextNode(text))

		if node.hasAttribute("height"):
			replacement_node.setAttribute("style", "height: %s" % (node.getAttribute("height")))
		return replacement_node
