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

import tempfile
from pyradium.Tools import ImageTools
from pyradium.DigitalTimingDiagram import DigitalTimingDiagram
from .BaseRenderer import BaseRenderer

@BaseRenderer.register
class DigitalTimingDiagramRenderer(BaseRenderer):
	_NAME = "dtg"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def render(self, property_dict):
		# Render to SVG first

		constructor_args_names = [ "xdiv", "height", "vertical_distance", "marker_extend", "clock_ticks" ]
		constructor_args = { }
		for arg_name in constructor_args:
			if arg_name in property_dict:
				constructor_args[arg_name] = property_dict[arg_name]

		dtg = DigitalTimingDiagram(**constructor_args)
		dtg.parse_and_write(property_dict["data"])

		with tempfile.NamedTemporaryFile(prefix = "digital_timing_", suffix = ".svg", mode = "w") as svg_file:
			dtg.svg.write(svg_file)
			svg_file.flush()

			# Postprocess in Inkscape to fit the canvas size
			ImageTools.svg_canvas_size_to_object(svg_file.name)

			with open(svg_file.name) as f:
				svg_data = f.read()

		result = {
			"svg":			svg_data,
		}
		return result
