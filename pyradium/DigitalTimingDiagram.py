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

class DigitalTimingType(enum.Enum):
	Low = "0"
	High = "1"
	LowHigh = ":"
	LowHighTransition = "!"
	HighZ = "Z"
	Marker = "|"
	Empty = " "

@dataclasses.dataclass
class DigitalTimingCmd():
	cmdtype: DigitalTimingType
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
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.Low)
				case "1":
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.High)
				case ":":
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.LowHigh)
				case "!":
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.LowHighTransition)
				case "Z":
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.HighZ)
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
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.Marker, argument = marker_label)
				case "_":
					cmd = DigitalTimingCmd(cmdtype = DigitalTimingType.Empty)
				case " ":
					continue
				case _:
					raise NotImplementedError(f"Unknown character in sequence diagram: {char}")
			sequence.append(cmd)
		return sequence

class DigitalTimingDiagram():
	_Marker = collections.namedtuple("Marker", [ "x", "label" ])

	def __init__(self, xdiv = 10, height = 30, vertical_distance = 10, marker_extend = 20, clock_ticks = True):
		self._xdiv = xdiv
		self._height = height
		self._vertical_distance = vertical_distance
		self._marker_extend = marker_extend
		self._clock_ticks = clock_ticks
		self._risefall = height / 8
		self._svg = SVGWriter()
		self._path = None
		self._plot_count = 0
		self._clock_ticks = 0
		if clock_ticks is True:
			self._svg.group("clock_ticks")
		self._markers = [ ]

	@property
	def svg(self):
		return self._svg

	@property
	def base_height(self):
		return ((self._height + self._vertical_distance) * self._plot_count) - self._vertical_distance

	def _transition_middle(self, y, transition_scale = 1):
		transition_width = transition_scale * self._risefall * (abs(y) / self._height)
		lead = (self._xdiv - transition_width) / 2
		self._path.horiz_rel(lead)
		self._path.line_rel(transition_width, y)
		self._path.horiz_rel(lead)

	def _render_signal_sequence(self, signal_name, x, y, cmds):
		prev = None
		self._plot_count += 1
		abs_y_mid = y + (self._height / 2)
		self._path = self._svg.new_path(x, abs_y_mid, group_name = "signal")

		text_width = 50
		svg_text = self._svg.new_text_span(x - text_width, abs_y_mid - 6, text_width, 30, signal_name.lstrip("!"), group_name = "signal")
		svg_text.style["text-align"] = "right"
		if signal_name.startswith("!"):
			svg_text.style["text-decoration"] = "overline"
		svg_text.style["font-family"] = "'Latin Modern Roman'"

		for cur in cmds:
			if prev is None:
				prev = cur
				if prev.cmdtype in [ DigitalTimingType.Low, DigitalTimingType.LowHigh, DigitalTimingType.LowHighTransition ]:
					self._path.move_rel(0, self._height / 2)
				elif prev.cmdtype in [ DigitalTimingType.High ]:
					self._path.move_rel(0, -self._height / 2)

			match (prev.cmdtype, cur.cmdtype):
				case (DigitalTimingType.Low, DigitalTimingType.Low) | (DigitalTimingType.High, DigitalTimingType.High) | (DigitalTimingType.HighZ, DigitalTimingType.HighZ):
					self._path.horiz_rel(self._xdiv)

				case (DigitalTimingType.Low, DigitalTimingType.High):
					self._transition_middle(-self._height)

				case (DigitalTimingType.High, DigitalTimingType.Low):
					self._transition_middle(self._height)

				case (DigitalTimingType.Low, DigitalTimingType.HighZ) | (DigitalTimingType.HighZ, DigitalTimingType.High):
					self._transition_middle(-self._height / 2)

				case (DigitalTimingType.High, DigitalTimingType.HighZ) | (DigitalTimingType.HighZ, DigitalTimingType.Low):
					self._transition_middle(self._height / 2)

				case (DigitalTimingType.LowHigh, DigitalTimingType.LowHigh) | (DigitalTimingType.LowHighTransition, DigitalTimingType.LowHigh):
					with self._path.returnto():
						# High to high
						self._path.move_rel(0, -self._height)
						self._path.horiz_rel(self._xdiv)
					# Low to low
					self._path.horiz_rel(self._xdiv)

				case (DigitalTimingType.High, DigitalTimingType.LowHigh):
					with self._path.returnto():
						# High to high
						self._path.horiz_rel(self._xdiv)
					# High to low
					self._transition_middle(self._height)

				case (DigitalTimingType.Low, DigitalTimingType.LowHigh):
					with self._path.returnto():
						# Low to high
						self._transition_middle(-self._height)
					# Low to low
					self._path.horiz_rel(self._xdiv)


				case (DigitalTimingType.LowHigh, DigitalTimingType.High):
					with self._path.returnto():
						# High to high
						self._path.move_rel(0, -self._height)
						self._path.horiz_rel(self._xdiv)
					# Low to low
					self._transition_middle(-self._height)

				case (DigitalTimingType.LowHigh, DigitalTimingType.Low):
					with self._path.returnto():
						# High to low
						self._path.move_rel(0, -self._height)
						self._transition_middle(self._height)
					# Low to low
					self._path.horiz_rel(self._xdiv)

				case (DigitalTimingType.HighZ, DigitalTimingType.LowHigh):
					with self._path.returnto():
						# HighZ to High
						self._transition_middle(-self._height / 2)
					# HighZ to Low
					self._transition_middle(self._height / 2)

				case (DigitalTimingType.LowHigh, DigitalTimingType.HighZ):
					with self._path.returnto():
						# Low to HighZ
						self._transition_middle(-self._height / 2)
					# High to HighZ
					self._path.move_rel(0, -self._height)
					self._transition_middle(self._height / 2)

				case (DigitalTimingType.LowHigh, DigitalTimingType.LowHighTransition) | (DigitalTimingType.LowHighTransition, DigitalTimingType.LowHighTransition):
					with self._path.returnto():
						self._transition_middle(-self._height, transition_scale = 2)
					self._path.move_rel(0, -self._height)
					self._transition_middle(self._height, transition_scale = 2)

				case (_, DigitalTimingType.Empty):
					self._path.move_to(self._path.pos.x, abs_y_mid)
					prev = None
					continue

				case (_, DigitalTimingType.Marker):
					mid_x = self._path.pos.x
					self._markers.append(self._Marker(x = mid_x + self._xdiv / 2, label = cur.argument))
					continue

				case _ as transition:
					raise NotImplementedError(f"Unsupported digital sequence diagram transition: {transition}")
			prev = cur
		self._clock_ticks = max(self._clock_ticks, round(self._path.pos.x / self._xdiv))

	def _render_markers(self):
		for marker in self._markers:
			have_label = (marker.label is not None) and (marker.label != "")
			marker_length = self.base_height if (not have_label) else (self.base_height + self._marker_extend)

			path = self._svg.new_path(marker.x, 0, group_name = "marker")
			path.vert_rel(marker_length)
			path.style["stroke-width"] = 0.5

			if have_label:
				text_width = 100
				text_height = 50

				svg_text = self._svg.new_text_span(marker.x - (text_width / 2), marker_length, text_width, text_height, marker.label, group_name = "marker")
				svg_text.style["text-align"] = "center"

	def _render_clock_ticks(self):
		for tick in range(self._clock_ticks):
			x = (tick * self._xdiv) + self._xdiv / 2
			path = self._svg.new_path(x, 0, group_name = "clock_ticks")
			path.vert_rel(self.base_height)
			path.style["stroke-width"] = 0.25
			path.style["stroke"] = "#95a5a6"
			path.style["stroke-miterlimit"] = 4
			path.style["stroke-dasharray"] = "0.75,0.25"
			path.style["stroke-dashoffset"] = 0

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
			cmds = DigitalTimingCmd.parse_sequence(sequence)
			self._render_signal_sequence(varname, 0, (self._height + self._vertical_distance) * varno, cmds)
			varno += 1
		self._render_markers()
		self._render_clock_ticks()
