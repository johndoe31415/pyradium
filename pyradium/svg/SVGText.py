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

from pyradium.Tools import XMLTools
from .SVGStyle import SVGStyle

class SVGText():
	def __init__(self, text_node):
		self._node = text_node
		self._node.setAttribute("xml:space", "preserve")
		self._textdata_node = None
		try:
			self._tspan_node = XMLTools.findfirst(self._node, "tspan")
			try:
				self._textdata_node = next(XMLTools.findall_text(self._tspan_node))
			except StopIteration:
				pass
		except StopIteration:
			self._tspan_node = self._node.appendChild(self._node.ownerDocument.createElement("tspan"))
		if self._textdata_node is None:
			self._textdata_node = self._tspan_node.appendChild(self._node.ownerDocument.createTextNode(""))
		self._style = SVGStyle.from_node(self._node, auto_sync = True).default_text()
		self._tspan_style = SVGStyle.from_node(self._tspan_node, auto_sync = True)

	@property
	def text(self):
		return self._textdata_node.wholeText

	@text.setter
	def text(self, value):
		self._textdata_node.replaceWholeText(value)

	@property
	def style(self):
		return self._style

	@property
	def tspan_style(self):
		return self._tspan_style

	@property
	def font(self):
		return self.tspan_style["font-family"]

	@font.setter
	def font(self, value):
		self.tspan_style["font-family"] = value
