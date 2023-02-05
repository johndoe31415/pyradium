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

import contextlib
from .SVGStyle import SVGStyle
from .Vector2D import Vector2D

class SVGPath():
	def __init__(self, path_node):
		self._node = path_node
		self._style = SVGStyle.from_node(self._node, auto_sync = True).default_path()
		self._cmds = [ ]
		self._pos = Vector2D()

	@property
	def pos(self):
		return self._pos

	@property
	def style(self):
		return self._style

	@contextlib.contextmanager
	def returnto(self):
		prev = self._pos
		yield
		self.move_to(prev.x, prev.y)

	def _append(self, *cmds):
		self._cmds += cmds
		self._node.setAttribute("d", " ".join(self._cmds))

	def move_to(self, x, y):
		self._append("M", f"{x},{y}")
		self._pos = Vector2D(x, y)
		return self

	def move_rel(self, x, y):
		self._append("m", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def line_to(self, x, y):
		self._append("L", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def line_rel(self, x, y):
		self._append("l", f"{x},{y}")
		self._pos += Vector2D(x, y)
		return self

	def horiz_rel(self, x):
		self._append("h", f"{x}")
		self._pos += Vector2D(x, 0)
		return self

	def vert_rel(self, y):
		self._append("v", f"{y}")
		self._pos += Vector2D(0, y)
		return self
