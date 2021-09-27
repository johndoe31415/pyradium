#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import tempfile
import hashlib
import subprocess
from pybeamer.Tools import ImageTools
from pybeamer.RendererCache import BaseRenderer
from pybeamer.Exceptions import UsageException
from pybeamer.SVGTransformation import SVGTransformation

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

	def _filehash(self, filename):
		with open(filename, "rb") as f:
			return hashlib.md5(f.read()).hexdigest()

	def _render_raw_svg(self, src, max_dimension, svg_transform = None):
		with tempfile.NamedTemporaryFile(prefix = "pybeamer_img_", suffix = ".png") as output_file:
			svg_info = ImageTools.get_image_info(src)
			if svg_info["image"]["geometry"]["width"] > svg_info["image"]["geometry"]["height"]:
				scale_param = "-w"
			else:
				scale_param = "-h"
			cmd = [ "inkscape", "-o", output_file.name, scale_param, str(max_dimension), src ]
			subprocess.check_call(cmd)
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
			with tempfile.NamedTemporaryFile(prefix = "pybeamer_img_", suffix = ".svg", mode = "w") as transformed_svg:
				svg.write(transformed_svg)
				transformed_svg.flush()
				return self._render_raw_svg(transformed_svg.name, max_dimension)

	def _render_raster_bitmap(self, src, max_dimension):
		# Resize using ImageMagick
		if src.lower().endswith(".jpg") or src.lower().endswith(".jpeg"):
			extension = "jpg"
		else:
			extension = "png"

		with tempfile.NamedTemporaryFile(prefix = "pybeamer_img_", suffix = "." + extension) as output_file:
			cmd = [ "convert", "-geometry", ">%dx%d" % (max_dimension, max_dimension), src, output_file.name ]
			subprocess.check_call(cmd)
			img_data = output_file.read()
		return (extension, img_data)

	def render(self, property_dict):
		src = property_dict["src"]
		srchash = self._filehash(src)
		max_dimension = property_dict["max_dimension"]

		if src.lower().endswith(".svg"):
			(extension, img_data) = self._render_svg(src, max_dimension, svg_transform = property_dict.get("svg_transform"))
		else:
			if "svg_transform" in property_dict:
				raise UsageException("SVG transformation requested, but source file is not in SVG format: %s / %s" % (src, str(property_dict)))
			(extension, img_data) = self._render_raster_bitmap(src, max_dimension)

		image = {
			"srchash":		srchash,
			"extension":	extension,
			"img_data":		img_data,
		}
		return image

if __name__ == "__main__":
	from pybeamer.RendererCache import RendererCache
	renderer = RendererCache(ImageRenderer())
	print(renderer.render({
		"src":	"examples/3dbox.svg",
	}))
