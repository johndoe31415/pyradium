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

	def test_past_midnight(self):
		agenda = Agenda.parse("""
		23:00
		+2:00	Presentation
		""")
		self.assertEqual(len(agenda), 1)
		self.assertEqual(agenda[0].start_time, "23:00")
		self.assertEqual(agenda[0].end_time, "1:00")
		self.assertEqual(agenda[0].text, "Presentation")

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
