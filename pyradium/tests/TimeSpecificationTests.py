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
from pyradium.Schedule import TimeSpecificationType, TimeSpecification, TimeRange, TimeRanges, PresentationSchedule
from pyradium.Exceptions import TimeSpecificationError

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

	def test_timerange_simple(self):
		tr = TimeRange.parse("11:12 - 22:23")
		self.assertEqual(tr.range_begin, (11 * 60) + 12)
		self.assertEqual(tr.range_end, (22 * 60) + 23)
		self.assertEqual(tr.begin_time, (11, 12))
		self.assertEqual(tr.end_time, (22, 23))
		self.assertEqual(tr.duration_mins, 48 + (60 * 10) + 23)

	def test_timerange_crossover(self):
		tr = TimeRange.parse(" 23:45-0:15 ")
		self.assertEqual(tr.range_begin, (23 * 60) + 45)
		self.assertEqual(tr.range_end, 1440 + (0 * 60) + 15)
		self.assertEqual(tr.begin_time, (23, 45))
		self.assertEqual(tr.end_time, (0, 15))
		self.assertEqual(tr.duration_mins, 30)

	def test_timerange_noparse(self):
		with self.assertRaises(TimeSpecificationError):
			TimeRange.parse("0 : 10 - 10:12")
		with self.assertRaises(TimeSpecificationError):
			TimeRange.parse(" 23:23 - 24:12")
		with self.assertRaises(TimeSpecificationError):
			TimeRange.parse(" 23:23 - 24:12")
		with self.assertRaises(TimeSpecificationError):
			TimeRange.parse(" 23:23 - 22:x2")

	def test_timeranges_simple(self):
		trs = TimeRanges.parse("10:00-10:15 10:20-10:30")
		self.assertEqual(trs.duration_mins, 15 + 10)

	def test_presentation_schedule_simple(self):
		ps = PresentationSchedule(active_presentation_time_minutes = 45)
		ps.set_slide_no(1, TimeSpecification.parse(abs_string = "2 min"))
		ps.set_slide_no(5, TimeSpecification.parse(rel_string = "2"))
		ps.have_slide(15)
#		for x in ps:
#			print(x)
