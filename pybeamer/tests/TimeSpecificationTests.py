#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

import unittest
from pybeamer.Schedule import TimeSpecificationType, TimeSpecification
from pybeamer.Exceptions import TimeSpecificationError

class TimeSpecificationTests(unittest.TestCase):
	def test_must_supply_value(self):
		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse()

	def test_may_not_supply_two_values(self):
		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(abs_string = "1 min", rel_string = "1")

	def test_rel_value(self):
		tspec = TimeSpecification.parse(rel_string = "1.234")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Relative)
		self.assertAlmostEqual(tspec.value, 1.234)

	def test_rel_value_noparse(self):
		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(rel_string = "")

		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(rel_string = "ABC")

	def test_abs_value_secs(self):
		tspec = TimeSpecification.parse(abs_string = "10 sec")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 10)

		tspec = TimeSpecification.parse(abs_string = "123s")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 123)

	def test_abs_value_min(self):
		tspec = TimeSpecification.parse(abs_string = "1min")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 60)

		tspec = TimeSpecification.parse(abs_string = "1.5m")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 90)

	def test_abs_value_colon(self):
		tspec = TimeSpecification.parse(abs_string = "2:30")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 150)

		tspec = TimeSpecification.parse(abs_string = "0:12")
		self.assertEqual(tspec.spec_type, TimeSpecificationType.Absolute)
		self.assertAlmostEqual(tspec.value, 12)

	def test_abs_value_noparse(self):
		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(abs_string = "")

		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(abs_string = ":12")

		with self.assertRaises(TimeSpecificationError):
			TimeSpecification.parse(abs_string = "1.234:30 min")
