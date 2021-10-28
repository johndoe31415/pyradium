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

import logging
import tempfile
import subprocess
from pyradium.CmdlineEscape import CmdlineEscape
from pyradium.Tools import ImageTools, HashTools
from pyradium.RendererCache import BaseRenderer
from pyradium.Exceptions import UsageException
from pyradium.SVGTransformation import SVGTransformation

_log = logging.getLogger(__spec__.name)

class ImageRenderer(BaseRenderer):
	def __init__(self):
		super().__init__()

	@property
	def name(self):
		return "img"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def _render_raw_svg(self, src, max_dimension, svg_transform = None):
		with tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = ".png") as output_file:
			svg_info = ImageTools.get_image_info(src)
			if svg_info["image"]["geometry"]["width"] > svg_info["image"]["geometry"]["height"]:
				scale_param = "-w"
			else:
				scale_param = "-h"
			cmd = [ "inkscape", "-o", output_file.name, scale_param, str(max_dimension), src ]
			_log.debug("Rendering SVG: %s", CmdlineEscape().cmdline(cmd))
			subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)
			extension = "png"
			img_data = output_file.read()
		return (extension, img_data)

	def _render_svg(self, src, max_dimension, svg_transform = None):
		if svg_transform is None:
			return self._render_raw_svg(src, max_dimension)
		else:
			# Transform SVG before rendering it
			svg = SVGTransformation(src)
			svg.apply_all(svg_transform)
			with tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = ".svg", mode = "w") as transformed_svg:
				svg.write(transformed_svg)
				transformed_svg.flush()
				return self._render_raw_svg(transformed_svg.name, max_dimension)

	def _render_raster_bitmap(self, src, max_dimension):
		# Resize using ImageMagick
		if src.lower().endswith(".jpg") or src.lower().endswith(".jpeg"):
			extension = "jpg"
		else:
			extension = "png"

		with tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = "." + extension) as output_file:
			cmd = [ "convert", "-geometry", ">%dx%d" % (max_dimension, max_dimension), src, output_file.name ]
			_log.debug("Rendering raster image: %s", CmdlineEscape().cmdline(cmd))
			subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)
			img_data = output_file.read()
		return (extension, img_data)

	def rendering_key(self, property_dict):
		src = property_dict["src"]
		return {
			"srchash":		HashTools.hash_file(src),
		}

	def render(self, property_dict):
		src = property_dict["src"]
		max_dimension = property_dict["max_dimension"]

		if src.lower().endswith(".svg"):
			(extension, img_data) = self._render_svg(src, max_dimension, svg_transform = property_dict.get("svg_transform"))
		else:
			if "svg_transform" in property_dict:
				raise UsageException("SVG transformation requested, but source file is not in SVG format: %s / %s" % (src, str(property_dict)))
			(extension, img_data) = self._render_raster_bitmap(src, max_dimension)

		image = {
			"extension":	extension,
			"img_data":		img_data,
		}
		return image

if __name__ == "__main__":
	from pyradium.RendererCache import RendererCache
	renderer = RendererCache(ImageRenderer())
	print(renderer.render({
		"max_dimension": 100,
		"src":	"test.svg",
	}))
