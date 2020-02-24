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

class Slide():
	def __init__(self, xmlnode, presentation):
		assert(xmlnode.tag == "slide")
		self._xml = xmlnode
		self._presentation = presentation
		self._slide_type = self._xml.attrib.get("type", "default")

	@property
	def presentation(self):
		return self._presentation

	@property
	def slide_type(self):
		return self._slide_type

	def dump(self):
		print("Slide<%s>" % (self.slide_type))

	def __repr__(self):
		return "Slide<%s>" % (self.slide_type)
