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

import unittest
import xml.dom.minidom
from pyradium.xmlhooks.XMLHookRegistry import XMLHookRegistry

class XMLHookTests(unittest.TestCase):
	def _parse(self, xmltext):
		doc = xml.dom.minidom.parseString(f"<?xml version=\"1.0\"?><slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">{xmltext}</slide>")
		slide = doc.childNodes[0]
		return slide

	def test_simple_enq(self):
		node = self._parse("<s:enq type=\"bkt\">foo</s:enq>")
		XMLHookRegistry.mangle(rendered_presentation = None, root_node = node)
		self.assertEqual(node.toxml(), "<slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">[foo]</slide>")

	def test_text_replace(self):
		node = self._parse("- -- ---")
		XMLHookRegistry.mangle(rendered_presentation = None, root_node = node)
		self.assertEqual(node.toxml(), "<slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">- – —</slide>")

	def test_text_replace_not_in_verb(self):
		node = self._parse("<s:verb>- -- ---</s:verb>")
		XMLHookRegistry.mangle(rendered_presentation = None, root_node = node)
		self.assertEqual(node.toxml(), "<slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">- -- ---</slide>")

	def test_text_replace_not_in_verb(self):
		node = self._parse("<s:enq type=\"bkt\"><s:verb>- -- ---</s:verb></s:enq>")
		XMLHookRegistry.mangle(rendered_presentation = None, root_node = node)
		self.assertEqual(node.toxml(), "<slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">[- -- ---]</slide>")

	def test_comment_replace(self):
		node = self._parse("foo <!-- comment -->bar")
		XMLHookRegistry.mangle(rendered_presentation = None, root_node = node)
		self.assertEqual(node.toxml(), "<slide xmlns:s=\"https://github.com/johndoe31415/pyradium\">foo bar</slide>")
