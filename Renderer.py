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
import contextlib
import mako.lookup
import pygments
import textwrap
import xml.dom.minidom
from Tools import XMLTools
from LatexFormula import LatexFormula

class PresentationRenderingError(Exception): pass

class Renderer():
	def __init__(self, template_dir, template_name, aspect_ratio, output_dir, rendering_mode = "presentation"):
		self._template_dir = template_dir
		self._template_name = template_name
		self._aspect_ratio = aspect_ratio
		self._output_dir = output_dir
		self._rendering_mode = rendering_mode
		self._lookup = mako.lookup.TemplateLookup(self._template_dir, input_encoding = "utf-8", strict_undefined = True)
		self._slide_template = self._lookup.get_template(self._template_name + "/template.html")
		with open(self._template_dir + "/" + self._template_name + "/template.json") as f:
			self._slide_template_definitions = json.load(f)
		self._geometry = self._calculate_geometry(self._aspect_ratio)
		self._cache_dir = os.path.expanduser("~/.cache/pybeamer")
		with contextlib.suppress(FileExistsError):
			os.makedirs(self._cache_dir)

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

	def render_slide(self, slide, meta):
		def error_fnc(msg):
			raise PresentationRenderingError(msg)
		return self._slide_template.render(renderer = self, slide = slide, meta = meta, error = error_fnc)

	def _render_tag_content(self, node): pass
	def _render_tag_pause(self, node): pass

	def _render_tag_debug(self, node):
		print("Debugging tag encountered: %s" % (node))
		XMLTools.remove_node(node)

	def _render_tag_tex(self, node):
		formula = LatexFormula(XMLTools.inner_text(node))
		rendered = formula.render(cache_dir = self._cache_dir)
		local_filename = "latex_%s.png" % (rendered.cachekey)
		rendered.write_png(self._output_dir + "/" + local_filename)
		img = node.ownerDocument.createElement("img")
		img.setAttribute("src", local_filename)
		XMLTools.replace_node(node, img)
		print("LaTeX formula: %s" % (formula))

	def _render_tag_code(self, node):
		lexer = pygments.lexers.get_lexer_by_name(node.getAttribute("lang"))
		code = XMLTools.inner_text(node).rstrip()
		if code.startswith("\n"):
			code = code[1:]
		code = textwrap.dedent(code)
		highlighted_code = pygments.highlight(code, lexer, pygments.formatters.HtmlFormatter())
		div_node = xml.dom.minidom.parseString(highlighted_code).firstChild
		XMLTools.replace_node(node, div_node)

	def _render_tag_term(self, node):
		# TODO implement me
		pass

	def _render_tag_emo(self, node):
		# TODO implement me
		pass

	def _render_tag_enq(self, node):
		return self._render_tag_enquote(node)

	def _render_tag_enquote(self, node):
		# TODO typographic
		text = "\"" + XMLTools.inner_text(node) + "\""
		text_node = node.ownerDocument.createText(text)
		XMLTools.replace_node(node, text_node)

	def _transform_slide_substitutions(self, dom):
		def visit(node):
			if node.namespaceURI == "http://github.com/johndoe31415/pybeamer":
				(ns, tag_name) = XMLTools.get_ns_tag(node)
				handler_name = "_render_tag_" + tag_name
				handler = getattr(self, handler_name, None)
				if handler is None:
					raise PresentationRenderingError("Unrecognized tag '%s' found in XML source." % (tag_name))
				handler(node)
		XMLTools.walk_elements(dom, visit)

	def _apply_slide_pauses(self, slide):
		resulting_slides = [ ]
		pause_tags = slide.dom.getElementsByTagNameNS("http://github.com/johndoe31415/pybeamer", "pause")
		for (pause_index, pause_tag) in enumerate(pause_tags):
			partial_slide = slide.clone()
			resulting_slides.append(partial_slide)

			pause_tags = partial_slide.dom.getElementsByTagNameNS("http://github.com/johndoe31415/pybeamer", "pause")
			last_pause = pause_tags[pause_index]
			XMLTools.remove_siblings_after(last_pause)
			for tag in pause_tags:
				XMLTools.remove_node(tag)
		resulting_slides.append(slide)
		return resulting_slides

	def _transform_slide(self, slide):
		self._transform_slide_substitutions(slide.dom)
		slides = self._apply_slide_pauses(slide)
		return slides

	def _transform_presentation(self, presentation):
		transformed_slides = [ ]
		for slide in presentation:
			transformed_slides += self._transform_slide(slide)
		return transformed_slides

	def render(self, presentation):
		slides = self._transform_presentation(presentation)
		self._render_static_file(slides, presentation.meta, "base/master_presentation.html", self._output_dir + "/index.html")
		self._render_static_file(slides, presentation.meta, "base/pybeamer.css", self._output_dir + "/pybeamer.css")

	def _render_static_file(self, slides, meta, input_filename, output_filename):
		master = self._lookup.get_template(input_filename)
		rendered = master.render(renderer = self, slides = slides, meta = meta)
		with open(output_filename, "w") as f:
			f.write(rendered)

	def _copy_static_style_file(self, subdir, filename):
		src_filename = self._template_dir + "/" + subdir + "/" + filename
		dst_filename = self._output_dir + "/" + os.path.basename(filename)
		shutil.copy(src_filename, dst_filename)

	def copy_style_files(self):
		self._copy_static_style_file("base", "pybeamer.js")
		for css_filename in self._slide_template_definitions.get("css", [ ]):
			self._copy_static_style_file(self._template_name, css_filename)
		for static_filename in self._slide_template_definitions.get("static", [ ]):
			self._copy_static_style_file(self._template_name, static_filename)
