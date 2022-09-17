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

import io
import logging
import tempfile
import mimetypes
import subprocess
from pyradium.CmdlineEscape import CmdlineEscape
from pyradium.Tools import ImageTools, HashTools
from pyradium.Exceptions import UsageException, ImageRenderingException
from pyradium.SVGTransformation import SVGTransformation
from .BaseRenderer import BaseRenderer

_log = logging.getLogger(__spec__.name)

@BaseRenderer.register
class ImageRenderer(BaseRenderer):
	_NAME = "img"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def _render_raw_svg(self, content, max_dimension, svg_transform = None):
		with tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = ".svg", mode = "wb") as input_file, tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = ".png") as output_file:
			input_file.write(content)
			input_file.flush()

			svg_info = ImageTools.get_image_info(input_file.name)
			if svg_info["image"]["geometry"]["width"] > svg_info["image"]["geometry"]["height"]:
				scale_param = "-w"
			else:
				scale_param = "-h"
			cmd = [ "inkscape", "-o", output_file.name, scale_param, str(max_dimension), input_file.name ]
			_log.debug("Rendering SVG: %s", CmdlineEscape().cmdline(cmd))
			subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)
			extension = "png"
			img_data = output_file.read()
		return (extension, img_data)

	def _render_svg(self, content, max_dimension, svg_transform = None):
		if svg_transform is None:
			return self._render_raw_svg(content, max_dimension)
		else:
			# Transform SVG before rendering it
			with tempfile.NamedTemporaryFile(prefix = "pyradium_svg_", suffix = ".svg", mode = "wb") as svg_file:
				# First write the unmodified file to the tempfile
				svg_file.write(content)
				svg_file.flush()

				# Then perform the transformation and write it back
				transformed_svg = io.StringIO()
				svg = SVGTransformation(svg_file.name)
				svg.apply_all(svg_transform)
				svg.write(transformed_svg)

				transformed_content = transformed_svg.getvalue().encode("utf-8")
				return self._render_raw_svg(transformed_content, max_dimension)

	def _render_raster_bitmap(self, content, mimetype, max_dimension):
		# Resize using ImageMagick
		extension = "jpg" if (mimetype == "image/jpeg") else "png"

		with tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = mimetypes.guess_extension(mimetype)) as input_file, tempfile.NamedTemporaryFile(prefix = "pyradium_img_", suffix = "." + extension) as output_file:
			input_file.write(content)
			input_file.flush()

			cmd = [ "convert", "-geometry", ">%dx%d" % (max_dimension, max_dimension), input_file.name, output_file.name ]
			_log.debug("Rendering raster image: %s", CmdlineEscape().cmdline(cmd))
			try:
				subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)
			except subprocess.CalledProcessError as e:
				raise ImageRenderingException(f"Failed to render {input_file.name} while trying to execute: {CmdlineEscape().cmdline(cmd)}") from e
			img_data = output_file.read()
		return (extension, img_data)

	def rendering_key(self, property_dict):
		if "src" in property_dict:
			# Specification as filename
			srchash = HashTools.hash_file(property_dict["src"])
		else:
			# Literal specification as data
			srchash = HashTools.hash_data(property_dict["value"])
		return {
			"srchash":		srchash,
		}

	def _determine_mimetype(self, property_dict):
		if "filetype" in property_dict:
			filename = f"x.{property_dict['filetype']}"
			return mimetypes.guess_type(filename)[0]
		else:
			return mimetypes.guess_type(property_dict["src"])[0]

	def render(self, property_dict):
		max_dimension = property_dict["max_dimension"]
		mimetype = self._determine_mimetype(property_dict)

		if "src" in property_dict:
			with open(property_dict["src"], "rb") as f:
				content = f.read()
		else:
			# Literal content specitication
			content = property_dict["value"]
			assert(isinstance(content, bytes))

		if mimetype == "image/svg+xml":
			(extension, img_data) = self._render_svg(content, max_dimension, svg_transform = property_dict.get("svg_transform"))
		else:
			if "svg_transform" in property_dict:
				raise UsageException(f"SVG transformation requested, but source file does not have SVG mimetype: {mimetype} / {str(property_dict)}")
			(extension, img_data) = self._render_raster_bitmap(content, mimetype, max_dimension)

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
