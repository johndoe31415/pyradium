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

class OrderedSet():
	def __init__(self):
		self._set = set()
		self._list = [ ]

	def add(self, item):
		if item in self._set:
			return
		self._set.add(item)
		self._list.append(item)

	def __or__(self, itemlist):
		for item in itemlist:
			self.add(item)
		return self

	def __repr__(self):
		return "OrderedSet" + str(self._list)

	def __iter__(self):
		return iter(self._list)
