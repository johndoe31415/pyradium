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

import enum
import collections
import dataclasses
from pyradium.SVGWriter import SVGWriter

class DigitalSignalType(enum.Enum):
	Low = "0"
	High = "1"
	LowHigh = ":"
	LowHighTransition = "!"
	HighZ = "Z"
	Marker = "|"
	Empty = " "

@dataclasses.dataclass
class DigitalSignalCmd():
	cmdtype: DigitalSignalType
	argument: "typing.Any" = None

	@classmethod
	def parse_sequence(cls, text):
		sequence = [ ]
		index = 0
		while index < len(text):
			char = text[index]
			index += 1
			match char:
				case "0":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.Low)
				case "1":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.High)
				case ":":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.LowHigh)
				case "!":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.LowHighTransition)
				case "Z":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.HighZ)
				case "|":
					marker_label = None
					if (index < len(text)) and (text[index] == "'"):
						# Label is present
						marker_label = ""
						index += 1
						while index < len(text):
							if text[index] == "'":
								break
							else:
								marker_label += text[index]
							index += 1
						index += 1
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.Marker, argument = marker_label)
				case "_":
					cmd = DigitalSignalCmd(cmdtype = DigitalSignalType.Empty)
				case " ":
					continue
				case _:
					raise NotImplementedError(f"Unknown character in sequence diagram: {char}")
			sequence.append(cmd)
		return sequence

class DigitalSignalDiagram():
	_Marker = collections.namedtuple("Marker", [ "x", "label" ])

	def __init__(self, xdiv = 10, height = 30, vertical_distance = 10):
		self._risefall = height / 8
		self._height = height
		self._vertical_distance = vertical_distance
		self._xdiv = xdiv
		self._svg = SVGWriter()
		self._path = None
		self._markers = [ ]

	@property
	def svg(self):
		return self._svg

	def _transition_middle(self, y, transition_scale = 1):
		transition_width = transition_scale * self._risefall * (abs(y) / self._height)
		lead = (self._xdiv - transition_width) / 2
		self._path.horiz_rel(lead)
		self._path.line_rel(transition_width, y)
		self._path.horiz_rel(lead)

	def write_signal_sequence(self, x, y, cmds):
		prev = None
		abs_y_mid = y + (self._height / 2)
		self._path = self._svg.new_path(x, abs_y_mid)

		for cur in cmds:
			if prev is None:
				prev = cur
				if prev.cmdtype in [ DigitalSignalType.Low, DigitalSignalType.LowHigh, DigitalSignalType.LowHighTransition ]:
					self._path.move_rel(0, self._height / 2)
				elif prev.cmdtype in [ DigitalSignalType.High ]:
					self._path.move_rel(0, -self._height / 2)

			match (prev.cmdtype, cur.cmdtype):
				case (DigitalSignalType.Low, DigitalSignalType.Low) | (DigitalSignalType.High, DigitalSignalType.High) | (DigitalSignalType.HighZ, DigitalSignalType.HighZ):
					self._path.horiz_rel(self._xdiv)

				case (DigitalSignalType.Low, DigitalSignalType.High):
					self._transition_middle(-self._height)

				case (DigitalSignalType.High, DigitalSignalType.Low):
					self._transition_middle(self._height)

				case (DigitalSignalType.Low, DigitalSignalType.HighZ) | (DigitalSignalType.HighZ, DigitalSignalType.High):
					self._transition_middle(-self._height / 2)

				case (DigitalSignalType.High, DigitalSignalType.HighZ) | (DigitalSignalType.HighZ, DigitalSignalType.Low):
					self._transition_middle(self._height / 2)

				case (DigitalSignalType.LowHigh, DigitalSignalType.LowHigh) | (DigitalSignalType.LowHighTransition, DigitalSignalType.LowHigh):
					with self._path.returnto():
						# High to high
						self._path.move_rel(0, -self._height)
						self._path.horiz_rel(self._xdiv)
					# Low to low
					self._path.horiz_rel(self._xdiv)

				case (DigitalSignalType.High, DigitalSignalType.LowHigh):
					with self._path.returnto():
						# High to high
						self._path.horiz_rel(self._xdiv)
					# High to low
					self._transition_middle(self._height)

				case (DigitalSignalType.Low, DigitalSignalType.LowHigh):
					with self._path.returnto():
						# Low to high
						self._transition_middle(-self._height)
					# Low to low
					self._path.horiz_rel(self._xdiv)


				case (DigitalSignalType.LowHigh, DigitalSignalType.High):
					with self._path.returnto():
						# High to high
						self._path.move_rel(0, -self._height)
						self._path.horiz_rel(self._xdiv)
					# Low to low
					self._transition_middle(-self._height)

				case (DigitalSignalType.LowHigh, DigitalSignalType.Low):
					with self._path.returnto():
						# High to low
						self._path.move_rel(0, -self._height)
						self._transition_middle(self._height)
					# Low to low
					self._path.horiz_rel(self._xdiv)

				case (DigitalSignalType.HighZ, DigitalSignalType.LowHigh):
					with self._path.returnto():
						# HighZ to High
						self._transition_middle(-self._height / 2)
					# HighZ to Low
					self._transition_middle(self._height / 2)

				case (DigitalSignalType.LowHigh, DigitalSignalType.HighZ):
					with self._path.returnto():
						# Low to HighZ
						self._transition_middle(-self._height / 2)
					# High to HighZ
					self._path.move_rel(0, -self._height)
					self._transition_middle(self._height / 2)

				case (DigitalSignalType.LowHigh, DigitalSignalType.LowHighTransition) | (DigitalSignalType.LowHighTransition, DigitalSignalType.LowHighTransition):
					with self._path.returnto():
						self._transition_middle(-self._height, transition_scale = 2)
					self._path.move_rel(0, -self._height)
					self._transition_middle(self._height, transition_scale = 2)

				case (_, DigitalSignalType.Empty):
					self._path.move_to(self._path.pos.x, abs_y_mid)
					prev = None
					continue

				case (_, DigitalSignalType.Marker):
					mid_x = self._path.pos.x
					self._markers.append(self._Marker(x = mid_x + self._xdiv / 2, label = cur.argument))
					continue

				case _ as transition:
					raise NotImplementedError(f"Unsupported digital sequence diagram transition: {transition}")
			prev = cur

	def write_markers(self):
		for marker in self._markers:
			path = self._svg.new_path(marker.x, 0)
			path.line_to(marker.x, 100)
			path.style["stroke-width"] = 0.5

			if marker.label != "":
				svg_text = self._svg.new_text_span(marker.x - 50, 100, 100, 100, marker.label)
				svg_text.style["text-align"] = "center"


	def parse_and_write(self, text):
		text = text.strip("\r\n")
		varno = 0
		for line in text.split("\n"):
			line = line.strip("\r\n \t")
			if line == "":
				continue
			(varname, sequence) = line.split("=", maxsplit = 1)
			varname = varname.strip("\t ")
			sequence = sequence.strip("\t ")
			cmds = DigitalSignalCmd.parse_sequence(sequence)
			self.write_signal_sequence(0, 50 * varno, cmds)
			varno += 1
		self.write_markers()
