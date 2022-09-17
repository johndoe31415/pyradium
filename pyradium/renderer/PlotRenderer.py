#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2022 Johannes Bauer
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

import re
import logging
import subprocess
from pyradium.Tools import HashTools
from .BaseRenderer import BaseRenderer

_log = logging.getLogger(__spec__.name)

@BaseRenderer.register
class PlotRenderer(BaseRenderer):
	_NAME = "plot"
	_SET_TERMINAL_RE = re.compile(r"^\s*set\s+terminal.*$", flags = re.MULTILINE)

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def _render_plot_png(self, src, width, height):
		with open(src) as f:
			source = f.read()
		source = self._SET_TERMINAL_RE.sub("", source)
		source = "set terminal pngcairo size %d,%d enhanced font 'Latin Modern Sans,24'\n" % (width, height) + source
		png_data = subprocess.check_output([ "gnuplot" ], input = source.encode("utf-8"), stderr = _log.subproc_target)
		return png_data

	def rendering_key(self, property_dict):
		src = property_dict["src"]
		return {
			"srchash":		HashTools.hash_file(src),
		}

	def render(self, property_dict):
		src = property_dict["src"]
		aspect = property_dict.get("aspect", 16 / 9)
		max_dimension = property_dict["max_dimension"]

		if aspect >= 1:
			width = max_dimension
			height = max_dimension / aspect
		else:
			width = max_dimension * aspect
			height = max_dimension

		img_data = self._render_plot_png(src, width, height)
		image = {
			"extension":	"png",
			"img_data":		img_data,
		}
		return image

if __name__ == "__main__":
	from pyradium.RendererCache import RendererCache
	renderer = RendererCache(PlotRenderer())
	print(renderer.render({
		"src":	"/tmp/x.gnuplot",
		"max_dimension": 1920,
	}))
