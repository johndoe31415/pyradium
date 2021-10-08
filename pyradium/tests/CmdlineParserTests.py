#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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
from pyradium.CmdlineParser import CmdlineParser, TrailingEscapeCharException, InvalidEscapeCharException

class CmdlineParserTests(unittest.TestCase):
	def test_end_meta(self):
		with self.assertRaises(TrailingEscapeCharException):
			CmdlineParser().parse("foo bar\\")
		CmdlineParser().parse("foo bar\\\\")

	def test_invalid_escape(self):
		with self.assertRaises(InvalidEscapeCharException):
			CmdlineParser().parse("foo \\x foo")

	def test_valid_escape(self):
		CmdlineParser().parse("foo \\\\ bar")
		CmdlineParser().parse("foo \\\\ bar\\\\")
		CmdlineParser().parse("foo \\  bar")
		CmdlineParser().parse("foo \\\"  bar")

	def test_simple_parse(self):
		self.assertEqual(CmdlineParser().parse("foo bar moo"), [ "foo", "bar", "moo" ])
		self.assertEqual(CmdlineParser().parse("foo bar   moo"), [ "foo", "bar", "moo" ])
		self.assertEqual(CmdlineParser().parse("foo          bar   moo"), [ "foo", "bar", "moo" ])

	def test_trailing_space(self):
		self.assertEqual(CmdlineParser().parse("foo bar moo "), [ "foo", "bar", "moo" ])
		self.assertEqual(CmdlineParser().parse("foo bar moo            "), [ "foo", "bar", "moo" ])

	def test_leading_space(self):
		self.assertEqual(CmdlineParser().parse(" foo bar moo"), [ "foo", "bar", "moo" ])
		self.assertEqual(CmdlineParser().parse("            foo bar moo"), [ "foo", "bar", "moo" ])

	def test_quotation_1(self):
		self.assertEqual(CmdlineParser().parse("foo \"bar koo\" moo"), [ "foo", "bar koo", "moo" ])
		self.assertEqual(CmdlineParser().parse("foo \"bar ' koo\" moo"), [ "foo", "bar ' koo", "moo" ])

	def test_quotation_2(self):
		self.assertEqual(CmdlineParser().parse("foo 'bar koo' moo"), [ "foo", "bar koo", "moo" ])
		self.assertEqual(CmdlineParser().parse("foo 'bar \" koo' moo"), [ "foo", "bar \" koo", "moo" ])

	def test_quotation_3(self):
		self.assertEqual(CmdlineParser().parse("foo ''bar\"\"\"moo\"'koo' moo"), [ "foo", "barmookoo", "moo" ])
