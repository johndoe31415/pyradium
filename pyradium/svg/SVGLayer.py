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

from .SVGStyle import SVGStyle

class SVGLayer():
	def __init__(self, group_node):
		self._node = group_node

	@property
	def label(self):
		return self._node.getAttribute("inkscape:label")

	@property
	def layer_id(self):
		return self._node.getAttribute("id")

	@property
	def is_visible(self):
		return SVGStyle.from_node(self._node).is_visible

	def modify_style(self, callback):
		style = SVGStyle.from_node(self._node)
		callback(style)
		style.sync_to_node()

	def hide(self):
		def _callback(style):
			style["display"] = "none"
		self.modify_style(_callback)

	def show(self):
		def _callback(style):
			style["display"] = "inline"
		self.modify_style(_callback)
