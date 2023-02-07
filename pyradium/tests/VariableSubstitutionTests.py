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
from pyradium.VariableSubstitution import VariableSubstitutionContainer
from pyradium.Exceptions import InvalidFStringExpressionException

class VariableSubstitutionTests(unittest.TestCase):
	def test_merge_dicts_overwrite(self):
		dict_a = { "foo": "bar" }
		dict_b = { "foo": "moo" }
		self.assertEqual(VariableSubstitutionContainer.merge_dicts(dict_a, dict_b), { "foo": "moo" })

	def test_merge_dicts_merge(self):
		dict_a = { "foo": "bar" }
		dict_b = { "bar": "moo" }
		self.assertEqual(VariableSubstitutionContainer.merge_dicts(dict_a, dict_b), { "foo": "bar", "bar": "moo" })

	def test_merge_dicts_merge_recursive(self):
		dict_a = { "foo": { "x": 1 } }
		dict_b = { "foo": { "y": 2 } }
		self.assertEqual(VariableSubstitutionContainer.merge_dicts(dict_a, dict_b), { "foo": { "x": 1, "y": 2 } })

	def test_dict_lookup_no_substitution(self):
		sub_dict = VariableSubstitutionContainer({
			"foo": 3,
			"bar": "three",
			"sub": {
				"moo":	"koo",
			},
		})
		self.assertEqual(sub_dict["foo"], 3)
		self.assertEqual(sub_dict["bar"], "three")
		self.assertEqual(sub_dict["sub"]["moo"], "koo")

	def test_dict_lookup_simple_substitution(self):
		sub_dict = VariableSubstitutionContainer({
			"foo": 3,
			"bar": "{v['foo'] + 1:02d}",
		})
		self.assertEqual(sub_dict["foo"], 3)
		self.assertEqual(sub_dict["bar"], "04")

	def test_dict_lookup_nested_substitution1(self):
		sub_dict = VariableSubstitutionContainer({
			"char": "~",
			"foo": "{v['char'] * 3}",
			"bar": "{v['foo']:>5s} XYZ {v['foo']:<5s}",
		})
		self.assertEqual(sub_dict["foo"], "~~~")
		self.assertEqual(sub_dict["bar"], "  ~~~ XYZ ~~~  ")

	def test_dict_lookup_nested_substitution2(self):
		sub_dict = VariableSubstitutionContainer({
			"time": {
				"hrs": 23,
				"min": 55,
				"total_min": "{v['time']['hrs'] * 60 + v['time']['min']}",
				"remaining_min": "{int(v['time']['total_min']) - 1234}",
			},
			"remaining_time": "{int(v['time']['remaining_min']) // 60:02d}:{int(v['time']['remaining_min']) % 60:02d}",
		}, {
			"int":	int,
		})
		self.assertEqual(sub_dict["time"]["total_min"], "1435")
		self.assertEqual(sub_dict["time"]["remaining_min"], "201")
		self.assertEqual(sub_dict["remaining_time"], "03:21")

	def test_dict_infinite_loop(self):
		sub_dict = VariableSubstitutionContainer({
			"a": "{v['b']}",
			"b": "{v['a']}",
		})
		with self.assertRaises(InvalidFStringExpressionException):
			sub_dict["a"]

	def test_illegal_expression(self):
		sub_dict = VariableSubstitutionContainer({
			"a": "\"\"\"",
		})
		with self.assertRaises(InvalidFStringExpressionException):
			sub_dict["a"]

	def test_evaluate_all(self):
		sub_dict = VariableSubstitutionContainer({
			"time": {
				"hrs": 23,
				"min": 55,
				"total_min": "{v['time']['hrs'] * 60 + v['time']['min']}",
				"remaining_min": "{int(v['time']['total_min']) - 1234}",
			},
			"x": [ "{1+3}", "9", [ "{9-3}" ] ],
			"remaining_time": "{int(v['time']['remaining_min']) // 60:02d}:{int(v['time']['remaining_min']) % 60:02d}",
		}, {
			"int":	int,
		})
		self.assertEqual(sub_dict.evaluate_all(), {
			"time": {
				"hrs": 23,
				"min": 55,
				"total_min": "1435",
				"remaining_min": "201",
			},
			"x": [ "4", "9", [ "6" ] ],
			"remaining_time": "03:21"
		})
