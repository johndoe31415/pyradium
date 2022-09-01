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
from pyradium.Agenda import Agenda
from pyradium.Exceptions import IllegalAgendaSyntaxException, UndefinedAgendaTimeException, UnresolvableWeightedEntryException, AgendaTimeMismatchException

class AgendaTests(unittest.TestCase):
	def test_simple1(self):
		agenda = Agenda.parse("""
		14:00
		+1:00	Presentation
		""")
		self.assertEqual(len(agenda), 1)
		self.assertEqual(agenda[0].start_time, "14:00")
		self.assertEqual(agenda[0].end_time, "15:00")
		self.assertEqual(agenda[0].text, "Presentation")

	def test_simple2(self):
		agenda = Agenda.parse("""
		14:00
		+1:00	Presentation
		+0:45	XYZ
		+0:45	ABC
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "14:00")
		self.assertEqual(agenda[0].end_time, "15:00")
		self.assertEqual(agenda[0].text, "Presentation")
		self.assertEqual(agenda[1].start_time, "15:00")
		self.assertEqual(agenda[1].end_time, "15:45")
		self.assertEqual(agenda[1].text, "XYZ")
		self.assertEqual(agenda[2].start_time, "15:45")
		self.assertEqual(agenda[2].end_time, "16:30")
		self.assertEqual(agenda[2].text, "ABC")

	def test_variable_simple3(self):
		agenda = Agenda.parse("""
		13:00
		14:00	A
		15:15	B
		16:20	C
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "14:00")
		self.assertEqual(agenda[1].start_time, "14:00")
		self.assertEqual(agenda[1].end_time, "15:15")
		self.assertEqual(agenda[2].start_time, "15:15")
		self.assertEqual(agenda[2].end_time, "16:20")

	def test_marker(self):
		agenda = Agenda.parse("""
		14:00
		:Beg
		+1:00	Presentation
		:First
		+0:45	XYZ
		+0:45	ABC
		:End
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "14:00")
		self.assertEqual(agenda[0].end_time, "15:00")
		self.assertEqual(agenda[0].text, "Presentation")
		self.assertEqual(agenda[1].start_time, "15:00")
		self.assertEqual(agenda[1].end_time, "15:45")
		self.assertEqual(agenda[1].text, "XYZ")
		self.assertEqual(agenda[2].start_time, "15:45")
		self.assertEqual(agenda[2].end_time, "16:30")
		self.assertEqual(agenda[2].text, "ABC")
		self.assertEqual(list(agenda.markers), [ ("Beg", "14:00"), ("First", "15:00"), ("End", "16:30") ])

	def test_backwards1(self):
		agenda = Agenda.parse("""
		+0:15	A
		+0:30	B
		+1:00	C
		14:00
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "12:15")
		self.assertEqual(agenda[0].end_time, "12:30")
		self.assertEqual(agenda[1].start_time, "12:30")
		self.assertEqual(agenda[1].end_time, "13:00")
		self.assertEqual(agenda[2].start_time, "13:00")
		self.assertEqual(agenda[2].end_time, "14:00")

	def test_backwards2(self):
		agenda = Agenda.parse("""
		+0:15	A
		+0:30	B
		+1:00	C
		14:00
		*		D
		14:15
		""")
		self.assertEqual(len(agenda), 4)
		self.assertEqual(agenda[0].start_time, "12:15")
		self.assertEqual(agenda[0].end_time, "12:30")
		self.assertEqual(agenda[1].start_time, "12:30")
		self.assertEqual(agenda[1].end_time, "13:00")
		self.assertEqual(agenda[2].start_time, "13:00")
		self.assertEqual(agenda[2].end_time, "14:00")
		self.assertEqual(agenda[3].start_time, "14:00")
		self.assertEqual(agenda[3].end_time, "14:15")

	def test_variable_gap(self):
		agenda = Agenda.parse("""
		13:00
		14:00	A
		15:00
		16:00	B
		""")
		self.assertEqual(len(agenda), 2)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "14:00")
		self.assertEqual(agenda[1].start_time, "15:00")
		self.assertEqual(agenda[1].end_time, "16:00")

	def test_past_midnight1(self):
		agenda = Agenda.parse("""
		23:00
		+2:00	Presentation
		""")
		self.assertEqual(len(agenda), 1)
		self.assertEqual(agenda[0].start_time, "23:00")
		self.assertEqual(agenda[0].end_time, "1:00")
		self.assertEqual(agenda[0].text, "Presentation")

	def test_past_midnight2(self):
		agenda = Agenda.parse("""
		23:00
		1+1:00	A
		3:00	B
		""")
		self.assertEqual(len(agenda), 2)
		self.assertEqual(agenda[0].start_time, "23:00")
		self.assertEqual(agenda[0].end_time, "1:00")
		self.assertEqual(agenda[0].duration, "2:00")
		self.assertEqual(agenda[0].text, "A")
		self.assertEqual(agenda[1].start_time, "1:00")
		self.assertEqual(agenda[1].end_time, "3:00")
		self.assertEqual(agenda[1].duration, "2:00")
		self.assertEqual(agenda[1].text, "B")

	def test_variable_simple1(self):
		agenda = Agenda.parse("""
		13:00
		*		A
		14:00
		""")
		self.assertEqual(len(agenda), 1)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "14:00")

	def test_variable_simple2(self):
		agenda = Agenda.parse("""
		13:00
		*		A
		*		B
		14:00
		""")
		self.assertEqual(len(agenda), 2)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "13:30")
		self.assertEqual(agenda[1].start_time, "13:30")
		self.assertEqual(agenda[1].end_time, "14:00")

	def test_variable_complex1(self):
		agenda = Agenda.parse("""
		13:00
		*		A
		+0:30	B
		*		C
		14:00
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "13:15")
		self.assertEqual(agenda[1].start_time, "13:15")
		self.assertEqual(agenda[1].end_time, "13:45")
		self.assertEqual(agenda[2].start_time, "13:45")
		self.assertEqual(agenda[2].end_time, "14:00")

	def test_variable_complex2(self):
		agenda = Agenda.parse("""
		13:00
		*		A
		+0:30	B
		*2		C
		14:00
		""")
		self.assertEqual(len(agenda), 3)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "13:10")
		self.assertEqual(agenda[1].start_time, "13:10")
		self.assertEqual(agenda[1].end_time, "13:40")
		self.assertEqual(agenda[2].start_time, "13:40")
		self.assertEqual(agenda[2].end_time, "14:00")

	def test_variable_complex3(self):
		agenda = Agenda.parse("""
		13:00
		*		A
		+0:30	B
		*2		C
		+0:10	D
		*		E
		14:00
		""")
		self.assertEqual(len(agenda), 5)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "13:05")
		self.assertEqual(agenda[1].start_time, "13:05")
		self.assertEqual(agenda[1].end_time, "13:35")
		self.assertEqual(agenda[2].start_time, "13:35")
		self.assertEqual(agenda[2].end_time, "13:45")
		self.assertEqual(agenda[3].start_time, "13:45")
		self.assertEqual(agenda[3].end_time, "13:55")
		self.assertEqual(agenda[4].start_time, "13:55")
		self.assertEqual(agenda[4].end_time, "14:00")

	def test_rounding(self):
		agenda = Agenda.parse("""
		13:01
		14:02	A
		15:03	B
		""", granularity_minutes = 5)
		self.assertEqual(len(agenda), 2)
		self.assertEqual(agenda[0].start_time, "13:00")
		self.assertEqual(agenda[0].end_time, "14:00")
		self.assertEqual(agenda[1].start_time, "14:00")
		self.assertEqual(agenda[1].end_time, "15:05")

	def test_divisor(self):
		agenda = Agenda.parse("""
		14:00
		+1:00/2		A
		+1:00/4		B
		""")
		self.assertEqual(len(agenda), 2)
		self.assertEqual(agenda[0].start_time, "14:00")
		self.assertEqual(agenda[0].end_time, "14:30")
		self.assertEqual(agenda[1].start_time, "14:30")
		self.assertEqual(agenda[1].end_time, "14:45")

	def test_error_syntax1(self):
		with self.assertRaises(IllegalAgendaSyntaxException):
			Agenda.parse("foo")

	def test_error_syntax2(self):
		with self.assertRaises(IllegalAgendaSyntaxException):
			Agenda.parse("1:00/2	A")

	def test_error_underspecified(self):
		with self.assertRaises(UndefinedAgendaTimeException):
			Agenda.parse("+1:00	A")

	def test_error_weights_zero(self):
		with self.assertRaises(UnresolvableWeightedEntryException):
			Agenda.parse("""
			13:00
			*0	foo
			14:00
			""")

	def test_error_weighted_out_of_time(self):
		with self.assertRaises(UnresolvableWeightedEntryException):
			Agenda.parse("""
			13:00
			+1:05	foo
			*	blah
			14:00
			""")

	def test_error_weighted_at_beginning(self):
		with self.assertRaises(UnresolvableWeightedEntryException):
			Agenda.parse("""
			*	blah
			14:00
			""")

	def test_error_weighted_at_end(self):
		with self.assertRaises(UnresolvableWeightedEntryException):
			Agenda.parse("""
			14:00
			*	blah
			""")

	def test_error_marker_first(self):
		with self.assertRaises(IllegalAgendaSyntaxException):
			Agenda.parse("""
			:Start
			14:00
			*	blah
			15:00
			""")

	def test_error_relative_out_of_time(self):
		with self.assertRaises(AgendaTimeMismatchException):
			Agenda.parse("""
			13:00
			+1:05	foo
			14:00
			""")

	def test_empty(self):
		agenda = Agenda.parse("")
		self.assertEqual(len(agenda), 0)
