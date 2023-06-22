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

import os
import logging
from pyradium.DigitalTimingDiagram import DigitalTimingDiagram
from pyradium.Tools import ImageTools
from .BaseStandaloneCommand import BaseStandaloneCommand

_log = logging.getLogger(__spec__.name)

@BaseStandaloneCommand.register
class DigitalTimingDiagramRenderer(BaseStandaloneCommand):
	_NAME = "dtd"
	_DESCRIPTION = "Render digital timing diagram"

	@classmethod
	def _gen_parser(cls, parser):
		parser.add_argument("-H", "--low-high-lines", action = "store_true", help = "Render LOW/HIGH horizontal lines.")
		parser.add_argument("-x", "--xdiv-size", metavar = "pixels", type = float, default = 10, help = "Defines the size of the X division in pixels. Defaults to %(default).1f.")
		parser.add_argument("-y", "--height", metavar = "pixels", type = float, default = 30, help = "Defines the bar height in pixels. Defaults to %(default).1f.")
		parser.add_argument("-n", "--no-clock-ticks", action = "store_true", help = "Do not draw clock tick marks.")
		parser.add_argument("-f", "--force", action = "store_true", help = "Overwrite output file if it already exists.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increases verbosity. Can be specified multiple times to increase.")
		parser.add_argument("infile", help = "Input text representation of the digital timing diagram.")
		parser.add_argument("outfile_svg", help = "Output SVG file of the rendered digital timing diagram.")

	def run(self):
		if (not self._args.force) and os.path.exists(self._args.outfile_svg):
			print(f"Refusing to overwrite: {self._args.outfile_svg}")
			return 1

		with open(self._args.infile) as f:
			dtd_text = f.read()

		dtd = DigitalTimingDiagram(xdiv = self._args.xdiv_size, height = self._args.height, clock_ticks = not self._args.no_clock_ticks, low_high_lines = self._args.low_high_lines)
		dtd.parse_and_write(dtd_text)
		dtd.svg.writefile(self._args.outfile_svg)
		ImageTools.svg_canvas_size_to_object(self._args.outfile_svg)
		return 0
