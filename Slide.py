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

class UndefinedContentException(Exception): pass

class Slide():
	def __init__(self, xmlnode, presentation):
		assert(xmlnode.tag == "slide")
		self._xml = xmlnode
		self._presentation = presentation
		if self.slide_type is None:
			self._xml.attrib["type"] = "default"

	def clone(self):
		xmlnode = XMLTools.clone_element(self._xml)
		return Slide(xmlnode = xmlnode, presentation = self.presentation)

	@property
	def presentation(self):
		return self._presentation

	@property
	def slide_type(self):
		return self._xml.attrib.get("type")

	def __getattr__(self, key):
		return self._xml.attrib.get(key)

	def content(self, content_name = None):
		if content_name is None:
			# All inner
			return XMLTools.dump_innerxml(self._xml)
		else:
			for child in self._xml.findall("{http://github.com/johndoe31415/pybeamer}content"):
				if child.attrib.get("name") == content_name:
					return XMLTools.dump_innerxml(child)
			else:
				raise UndefinedContentException("Template tried to access content named '%s', but no such content defined in slide." % (content_name))

	def dump(self):
		print("Slide<%s>" % (self.slide_type))

	def __repr__(self):
		return "Slide<%s>" % (self.slide_type)
