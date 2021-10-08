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

import json
import tempfile
import subprocess
from pyradium.RendererCache import BaseRenderer

_TEX_TEMPLATE = r"""
\documentclass[preview,border=1mm,varwidth=true]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath}
\usepackage{amssymb}
\begin{document}
%(content)s
\end{document}
"""

class LatexFormulaRenderer(BaseRenderer):
	def __init__(self, rendering_dpi = 600):
		super().__init__()
		self._rendering_dpi = rendering_dpi

	@property
	def name(self):
		return "latex"

	@property
	def properties(self):
		return {
			"version":			1,
			"rendering_dpi":	self._rendering_dpi,
		}

	def _get_image_info(self, png_filename, xoffset):
		# Need 2 pixel wide sample so that ImageMagick does not return an empty image
		crop_info = json.loads(subprocess.check_output([ "convert", "%s[2x+%d+0]" % (png_filename, xoffset), "-trim", "json:-" ]))

		image_width = crop_info[0]["image"]["pageGeometry"]["width"]
		image_height = crop_info[0]["image"]["pageGeometry"]["height"]
		upper_baseline_y_from_top = crop_info[0]["image"]["pageGeometry"]["y"]
		lower_baseline_y_from_top = upper_baseline_y_from_top + crop_info[0]["image"]["geometry"]["height"]
		baseline_y_from_top = round((upper_baseline_y_from_top + lower_baseline_y_from_top) / 2)
		baseline_y_from_bottom = image_height - baseline_y_from_top

		image_info = {
			"width":		image_width,
			"height":		image_height,
			"baseline":		baseline_y_from_bottom,
		}
		return image_info

	def render(self, property_dict):
		with tempfile.TemporaryDirectory(prefix = "pyradium_formula_") as tex_dir:
			# Formula to PDF first using pdflatex
			tex_filename = tex_dir + "/formula.tex"
			pdf_filename = tex_dir + "/formula.pdf"
			png_filename = tex_dir + "/formula.png"

			# Crop 3mm off the left side (1mm baseline bar + 2mm space)
			baseline = r"\rule{1mm}{1pt} \hspace{2mm}"
			left_crop_pixel = round((3 / 25.4) * self._rendering_dpi)
			left_crop_pixel_safe = round((2 / 25.4) * self._rendering_dpi)
			eval_baseline_at_x = round((0.5 / 25.4) * self._rendering_dpi)

			if property_dict.get("long", False):
				content = r"\[" + baseline + property_dict["formula"] + r" \]"
			else:
				content = r"$" + baseline + property_dict["formula"] + r"$"
			with open(tex_filename, "w") as tex_file:
				tex_file.write(_TEX_TEMPLATE % { "content": content })
			subprocess.check_call([ "pdflatex", "-output-directory=%s" % (tex_dir), tex_filename ])

			# Then render the PDF to PNG
			subprocess.check_call([ "convert", "-define", "profile:skip=ICC", "-density", str(self._rendering_dpi), "-trim", "+repage", pdf_filename, png_filename ])

#			print("Crop on left side: %d (choosing %d to be on safe side); evaluating baseline at x = %d; filename %s" % (left_crop_pixel, left_crop_pixel_safe, eval_baseline_at_x, png_filename))
			image_info = self._get_image_info(png_filename, eval_baseline_at_x)

#			print("Determined baseline y-offset at %d pixels (measured from bottom)" % (image_info["baseline"]))

			# Then crop the image finally
			png_data = subprocess.check_output([ "convert", "-crop", "+%d+0" % (left_crop_pixel_safe), "-trim", "+repage", png_filename, "png:-" ])

			# Return an image object
			image = {
				"png_data":	png_data,
				"info":		image_info,
			}
			return image

if __name__ == "__main__":
	from pyradium.RendererCache import RendererCache
	renderer = RendererCache(LatexFormulaRenderer())
	print(renderer.render({ "formula": "y^2 = x^3 + ax + b" }))
