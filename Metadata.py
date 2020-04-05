#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2020 Johannes Bauer
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

from Tools import XMLTools

class Metadata():
	def __init__(self, metadata):
		self._data = metadata

	def has(self, key):
		return key in self._data

	def get(self, key, default_value = None):
		return self._data.get(key, default_value)

	def __getattr__(self, key):
		if not self.has(key):
			raise AttributeError("No such attribute: %s" % (key))
		return self.get(key)

	@classmethod
	def from_xmlnode(cls, node):
		metadata = { }
		if node is not None:
			for child in node.childNodes:
				if child.nodeType == child.ELEMENT_NODE:
					metadata[child.tagName] = XMLTools.inner_text(child)
		return cls(metadata)
