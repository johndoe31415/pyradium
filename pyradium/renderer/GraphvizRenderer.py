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

import logging
import subprocess
from pyradium.Tools import HashTools
from .BaseRenderer import BaseRenderer

_log = logging.getLogger(__spec__.name)

@BaseRenderer.register
class GraphvizRenderer(BaseRenderer):
	_NAME = "graphviz"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def _render_plot_png(self, src, scale):
		with open(src) as f:
			source = f.read()
		dpi = round(250 * scale)
		png_data = subprocess.check_output([ "dot", "-Tpng", f"-Gdpi={dpi}" ], input = source.encode("utf-8"), stderr = _log.subproc_target)
		return png_data

	def rendering_key(self, property_dict):
		src = property_dict["src"]
		return {
			"srchash":		HashTools.hash_file(src),
		}

	def render(self, property_dict):
		src = property_dict["src"]
		scale = float(property_dict.get("scale", "1"))
		img_data = self._render_plot_png(src, scale)
		image = {
			"extension":	"png",
			"img_data":		img_data,
		}
		return image

if __name__ == "__main__":
	from pyradium.RendererCache import RendererCache
	renderer = RendererCache(GraphvizRenderer())
	output = renderer.render({
		"src":	"/tmp/x.dot"
	})
	print(output)
	with open("/tmp/x.png", "wb") as f:
		f.write(output.data["img_data"])
