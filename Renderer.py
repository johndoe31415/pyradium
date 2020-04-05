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

import os
import json
import shutil
import math
import mako.lookup

class PresentationRenderingError(Exception): pass

class Renderer():
	def __init__(self, template_dir, template_name, aspect_ratio):
		self._aspect_ratio = aspect_ratio
		self._template_dir = template_dir
		self._template_name = template_name
		self._lookup = mako.lookup.TemplateLookup(self._template_dir, input_encoding = "utf-8", strict_undefined = True)
		self._slide_template = self._lookup.get_template(self._template_name + "/template.html")
		with open(self._template_dir + "/" + self._template_name + "/template.json") as f:
			self._slide_template_definitions = json.load(f)
		self._geometry = self._calculate_geometry(self._aspect_ratio)

	@property
	def geometry(self):
		return self._geometry

	@staticmethod
	def _calculate_geometry(aspect):
		"""Keep the area in pixels constant and calculate width/height in
		pixels given a specific aspect ratio."""
		baseline_geometry_at_16_9 = (1280, 720)
		baseline_area = baseline_geometry_at_16_9[0] * baseline_geometry_at_16_9[1]
		height = round(math.sqrt(baseline_area / aspect))
		width = round(aspect * height)
		return (width, height)

	@property
	def css_filenames(self):
		return [ os.path.basename(filename) for filename in self._slide_template_definitions.get("css", [ ]) ]

	@property
	def slide_template(self):
		return self._slide_template

	def render_slide(self, slide, presentation):
		def error_fnc(msg):
			raise PresentationRenderingError(msg)
		return self._slide_template.render(renderer = self, slide = slide, presentation = presentation, meta = presentation.meta, error = error_fnc)

	def render(self, presentation, output_dir):
		presentation.process_slides()
		self._render_static_file(presentation, "base/master_presentation.html", output_dir + "/index.html")
		self._render_static_file(presentation, "base/pybeamer.css", output_dir + "/pybeamer.css")

	def _render_static_file(self, presentation, input_filename, output_filename):
		master = self._lookup.get_template(input_filename)
		rendered = master.render(renderer = self, presentation = presentation)
		with open(output_filename, "w") as f:
			f.write(rendered)

	def _copy_static_style_file(self, subdir, filename, output_dir):
		src_filename = self._template_dir + "/" + subdir + "/" + filename
		dst_filename = output_dir + "/" + os.path.basename(filename)
		shutil.copy(src_filename, dst_filename)

	def copy_style_files(self, output_dir):
		self._copy_static_style_file("base", "pybeamer.js", output_dir)
		for css_filename in self._slide_template_definitions.get("css", [ ]):
			self._copy_static_style_file(self._template_name, css_filename, output_dir)
		for static_filename in self._slide_template_definitions.get("static", [ ]):
			self._copy_static_style_file(self._template_name, static_filename, output_dir)
