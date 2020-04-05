#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2020 Johannes Bauer
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

import json
import base64
import tempfile
import hashlib
import subprocess

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

class RenderedLatexFormula():
	def __init__(self, formula, png_data, baseline, rendering_parameters):
		self._formula = formula
		self._png_data = png_data
		self._baseline = baseline
		self._rendering_parameters = rendering_parameters

	@classmethod
	def calculate_cachekey(cls, formula, rendering_parameters):
		input_data = formula + " || " + str(sorted(rendering_parameters.items()))
		return hashlib.md5(input_data.encode("utf-8")).hexdigest()

	@property
	def cachekey(self):
		return self.calculate_cachekey(self._formula, self._rendering_parameters)

	@property
	def baseline(self):
		return self._baseline

	@classmethod
	def read_jsonfile(cls, filename):
		with open(filename) as f:
			json_data = json.load(f)
		assert(json_data["object"] == "formula")
		return cls(formula = json_data["formula"], png_data = base64.b64decode(json_data["image"]), baseline = json_data["baseline"], rendering_parameters = json_data["rendering_parameters"])

	def write_jsonfile(self, filename):
		json_data = {
			"object":					"formula",
			"formula":					self._formula,
			"rendering_parameters":		self._rendering_parameters,
			"baseline":					self._baseline,
			"image":					base64.b64encode(self._png_data).decode("ascii"),
		}
		with open(filename, "w") as f:
			json.dump(json_data, f)

	def write_png(self, filename):
		with open(filename, "wb") as f:
			f.write(self._png_data)

class LatexFormula():
	def __init__(self, formula):
		self._formula = formula

	@property
	def formula(self):
		return self._formula

	def _find_baseline(self, png_filename, xoffset):
		crop_output = subprocess.check_output([ "convert", "%s[1x+%d+0]" % (png_filename, xoffset), "-trim", "info:-" ])
		crop_output = crop_output.decode().split()
		cropped_size = crop_output[2].split("x")
		(image_geometry, image_offset) = crop_output[3].split("+", maxsplit = 1)
		image_geometry = image_geometry.split("x")
		image_offset = image_offset.split("+")
		cropped_height = int(cropped_size[1])
		cropped_yoffset = int(image_offset[1])
		image_height = int(image_geometry[1])
		baseline_y = cropped_height + cropped_yoffset
		baseline_y_from_bottom = image_height - baseline_y
		return baseline_y_from_bottom

	def _do_render(self, rendering_parameters):
		with tempfile.TemporaryDirectory(prefix = "pybeamer_formula_") as tex_dir:
			# Formula to PDF first using pdflatex
			tex_filename = tex_dir + "/formula.tex"
			pdf_filename = tex_dir + "/formula.pdf"
			png_filename = tex_dir + "/formula.png"

			# Crop 3mm off the left side (1mm baseline bar + 2mm space)
			baseline = r"\rule{1mm}{1pt} \hspace{2mm}"
			left_crop_pixel = round((3 / 25.4) * rendering_parameters["rendering_dpi"])
			left_crop_pixel_safe = round((2 / 25.4) * rendering_parameters["rendering_dpi"])
			eval_baseline_at_x = round((0.5 / 25.4) * rendering_parameters["rendering_dpi"])

			if rendering_parameters["short"]:
				content = r"$" + baseline + self._formula + r"$"
			else:
				content = r"\[" + baseline + self._formula + r" \]"
			with open(tex_filename, "w") as tex_file:
				tex_file.write(_TEX_TEMPLATE % { "content": content })
			subprocess.check_call([ "pdflatex", "-output-directory=%s" % (tex_dir), tex_filename ])

			# Then render the PDF to PNG
			subprocess.check_call([ "convert", "-define", "profile:skip=ICC", "-density", str(rendering_parameters["rendering_dpi"]), "-trim", "+repage", pdf_filename, png_filename ])

#			print("Crop on left side: %d (choosing %d to be on safe side); evaluating baseline at x = %d; filename %s" % (left_crop_pixel, left_crop_pixel_safe, eval_baseline_at_x, png_filename))
			baseline_y = self._find_baseline(png_filename, eval_baseline_at_x)

#			print("Determined baseline y-offset at %d pixels (measured from bottom)" % (baseline_y))

			# Then crop the image finally
			png_data = subprocess.check_output([ "convert", "-crop", "+%d+0" % (left_crop_pixel_safe), "-trim", "+repage", png_filename, "png:-" ])

			# Return an image object
			return RenderedLatexFormula(formula = self.formula, png_data = png_data, baseline = baseline_y, rendering_parameters = rendering_parameters)

	def render(self, rendering_dpi = 600, short = False, cache_dir = None):
		rendering_parameters = {
			"rendering_dpi":	round(rendering_dpi),
			"short":			short,
		}
		if cache_dir is not None:
			cachekey = RenderedLatexFormula.calculate_cachekey(self.formula, rendering_parameters)
			cachefile = cache_dir + "/latex_" + cachekey + ".json"
			try:
				rendered = RenderedLatexFormula.read_jsonfile(cachefile)
				return rendered
			except FileNotFoundError:
				pass

		rendered = self._do_render(rendering_parameters)
		if cache_dir is not None:
			rendered.write_jsonfile(cachefile)

		return rendered

	def __str__(self):
		return "LaTeX(%s)" % (self.formula)

if __name__ == "__main__":
	tex = LatexFormula("y^2 = x^3 + ax + b")
	tex.render(cache_dir = "foo/").write_png("formula_long.png")
	tex.render(cache_dir = "foo/", short = True).write_png("formula_short.png")
