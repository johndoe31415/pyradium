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

@XMLHookRegistry.register_hook
class DigitalTimingDiagramHook(BaseHook):
	_TAG_NAME = "dtg"

	@classmethod
	def handle(cls, rendered_presentation, node):
#		if not node.hasAttribute("cmd"):
#			raise MalformedXMLInputException("An s:exec node must have a 'cmd' attribute.")

		properties = {
			"data":	XMLTools.inner_text(node),
		}
		dtg_renderer = rendered_presentation.renderer.get_custom_renderer("dtg")
		result = dtg_renderer.render(properties)

		replacement_node = node.ownerDocument.createElement("s:img")
		replacement_node.setAttribute("value", result.data["svg"])
		replacement_node.setAttribute("filetype", "svg")
		return replacement_node
