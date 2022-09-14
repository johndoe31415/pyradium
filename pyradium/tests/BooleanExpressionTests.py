#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2022 Johannes Bauer
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
from pyradium.BooleanExpression import BooleanExpressionParser, TexBooleanExpressionPrinter
from pyradium.Exceptions import InvalidBooleanExpressionException

class BooleanExpressionTests(unittest.TestCase):
	def setUp(self):
		self._tex_default = TexBooleanExpressionPrinter()
		self._tex_no_overline = TexBooleanExpressionPrinter(invert_by_overline = False)

	def test_parse_short_literal(self):
		BooleanExpressionParser("A B C").parse()

	def test_parse_long_literal(self):
		BooleanExpressionParser("[ABC][DEF]").parse()

	def test_parse_invert(self):
		BooleanExpressionParser("A!B!C").parse()

	def test_parse_special(self):
		BooleanExpressionParser("A & B | C").parse()

	def test_parse_complete(self):
		BooleanExpressionParser("X = (A!B!C) | !(ABC) | ![ABC] & X!YZ | (A & (B | !C))").parse()

	def test_parse_error_open_parenthesis(self):
		with self.assertRaises(InvalidBooleanExpressionException):
			BooleanExpressionParser("X = (A!B!C").parse()

	def test_parse_error_inverted(self):
		with self.assertRaises(InvalidBooleanExpressionException):
			BooleanExpressionParser("X = !").parse()

	def test_parse_error_empty(self):
		with self.assertRaises(InvalidBooleanExpressionException):
			BooleanExpressionParser("X = ()").parse()

	def test_parse_error_trailiing(self):
		with self.assertRaises(InvalidBooleanExpressionException):
			BooleanExpressionParser("X#").parse()

	def test_tex_default_simple(self):
		tree = BooleanExpressionParser("XYZ").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{X}\textnormal{Y}\textnormal{Z}")

	def test_tex_default_long_literal(self):
		tree = BooleanExpressionParser("[XYZ]").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{XYZ}")

	def test_tex_default_inv_long_literal(self):
		tree = BooleanExpressionParser("![XYZ]").parse()
		self.assertEqual(self._tex_default.print(tree), r"\overline{\textnormal{XYZ}}")

	def test_tex_default_inverted_literal(self):
		tree = BooleanExpressionParser("X!Y!Z").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{X}\overline{\textnormal{Y}}\overline{\textnormal{Z}}")

	def test_tex_default_logical_or(self):
		tree = BooleanExpressionParser("X | Y").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{X} \vee \textnormal{Y}")

	def test_tex_default_logical_and(self):
		tree = BooleanExpressionParser("X & Y").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{X} \wedge \textnormal{Y}")

	def test_tex_default_complex(self):
		tree = BooleanExpressionParser("X = (A!B!C) | !(ABC) | ![ABC] & X!YZ | (A & (B | !C))").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{X} = (\textnormal{A}\overline{\textnormal{B}}\overline{\textnormal{C}}) \vee \overline{\textnormal{A}\textnormal{B}\textnormal{C}} \vee \overline{\textnormal{ABC}} \wedge \textnormal{X}\overline{\textnormal{Y}}\textnormal{Z} \vee (\textnormal{A} \wedge (\textnormal{B} \vee \overline{\textnormal{C}}))")

	def test_tex_default_realworld_1(self):
		tree = BooleanExpressionParser("[CLK] = 1").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{CLK} = 1")

	def test_tex_default_realworld_2(self):
		tree = BooleanExpressionParser("!Q = 1").parse()
		self.assertEqual(self._tex_default.print(tree), r"\overline{\textnormal{Q}} = 1")

	def test_tex_default_realworld_3(self):
		tree = BooleanExpressionParser("Z = !(!A!B!C | ![foo])").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{Z} = \overline{\overline{\textnormal{A}}\overline{\textnormal{B}}\overline{\textnormal{C}} \vee \overline{\textnormal{foo}}}")

	def test_tex_default_realworld_4(self):
		tree = BooleanExpressionParser("[CLK] = AB!C!D | A!B!D & (A | BD) | !(A | BC)").parse()
		self.assertEqual(self._tex_default.print(tree), r"\textnormal{CLK} = \textnormal{A}\textnormal{B}\overline{\textnormal{C}}\overline{\textnormal{D}} \vee \textnormal{A}\overline{\textnormal{B}}\overline{\textnormal{D}} \wedge (\textnormal{A} \vee \textnormal{B}\textnormal{D}) \vee \overline{\textnormal{A} \vee \textnormal{B}\textnormal{C}}")

	def test_tex_no_overline_realworld_4(self):
		tree = BooleanExpressionParser("[CLK] = AB!C!D | A!B!D & (A | BD) | !(A | BC)").parse()
		self.assertEqual(self._tex_no_overline.print(tree), r"\textnormal{CLK} = \textnormal{A}\textnormal{B}\neg \textnormal{C}\neg \textnormal{D} \vee \textnormal{A}\neg \textnormal{B}\neg \textnormal{D} \wedge (\textnormal{A} \vee \textnormal{B}\textnormal{D}) \vee \neg (\textnormal{A} \vee \textnormal{B}\textnormal{C})")
