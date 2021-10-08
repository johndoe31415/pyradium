#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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

from .Tools import XMLTools

class RenderableSlide():
	def __init__(self, slide_type, content_containers, slide_vars):
		self._slide_type = slide_type
		self._content_containers = content_containers
		self._slide_vars = slide_vars

	@property
	def slide_type(self):
		return self._slide_type

	def var(self, name, default_value = None):
		return self._slide_vars.get(name, default_value)

	def has(self, name):
		return name in self._slide_vars

	def content(self, key = None):
		if key is None:
			key = "default"
		return XMLTools.inner_toxml(self._content_containers.get(key))
