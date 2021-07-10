#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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
import contextlib
from .RendererCache import RendererCache
from .TOC import TOC
from pybeamer.renderer.LatexFormulaRenderer import LatexFormulaRenderer
import mako.lookup

class RenderedPresentation():
	def __init__(self, renderer, deploy_directory):
		self._renderer = renderer
		self._rendered_slides = [ ]
		self._css = set()
		self._toc = TOC()
		self._deploy_directory = deploy_directory
		self._added_files = set()

	@property
	def renderer(self):
		return self._renderer

	@property
	def rendered_slides(self):
		return iter(self._rendered_slides)

	@property
	def css(self):
		return iter(self._css)

	def add_css(self, filename):
		return self._css.add(filename)

	@property
	def toc(self):
		return self._toc

	def append_slide(self, rendered_slide):
		self._rendered_slides.append(rendered_slide)

	def add_file(self, destination_relpath, content):
		if destination_relpath in self._added_files:
			return
		self._added_files.add(destination_relpath)
		filename = self._deploy_directory + "/" + destination_relpath
		dirname = os.path.dirname(filename)
		with contextlib.suppress(FileExistsError):
			os.makedirs(dirname)
		with open(filename, "w" if isinstance(content, str) else "wb") as f:
			f.write(content)

	def copy_file(self, source_filename, destination_relpath):
		if destination_relpath in self._added_files:
			return
		with open(source_filename, "rb") as f:
			self.add_file(destination_relpath, f.read())

class PresentationRenderer():
	def __init__(self, presentation, rendering_params):
		self._rendered_slides = [ ]
		self._presentation = presentation
		self._rendering_params = rendering_params
		self._custom_renderers = {
			"latex":	RendererCache(LatexFormulaRenderer()),
		}
		self._template_directory = os.path.dirname(os.path.realpath(__file__)) + "/templates"
		self._lookup = mako.lookup.TemplateLookup([ self._template_directory, self._template_directory + "/" + self._rendering_params.template_style ], strict_undefined = True, input_encoding = "utf-8")
		with open(self._template_directory + "/" + self._rendering_params.template_style + "/configuration.json") as f:
			self._template_config = json.load(f)

	@property
	def rendering_params(self):
		return self._rendering_params

	def get_custom_renderer(self, name):
		return self._custom_renderers[name]

	def get_include(self, filename):
		# TODO FIXME
		return "examples/" + filename

	def _compute_renderable_slides(self, rendered_presentation):
		renderable_slides = [ ]
		for directive in self._presentation:
			generator = directive.render(rendered_presentation)
			if generator is not None:
				renderable_slides += generator
		return renderable_slides

	def render(self, deploy_directory):
		rendered_presentation = RenderedPresentation(self, deploy_directory = deploy_directory)
		rendered_presentation.copy_file(self._template_directory + "/base/pybeamer.js", "pybeamer.js")

		for filename in self._template_config.get("files", { }).get("static", [ ]):
			rendered_presentation.copy_file("%s/%s/%s" % (self._template_directory, self._rendering_params.template_style, filename), filename)

		for filename in self._template_config.get("files", { }).get("css", [ ]):
			rendered_presentation.copy_file("%s/%s/%s" % (self._template_directory, self._rendering_params.template_style, filename), filename)
			rendered_presentation.add_css(filename)

		template_args = {
			"renderer":					self,
			"presentation":				self._presentation,
			"rendered_presentation":	rendered_presentation,
		}

		for renderable_slide in self._compute_renderable_slides(rendered_presentation):
			args = dict(template_args)
			args.update({
				"slide":			renderable_slide,
			})
			template = self._lookup.get_template("slide_%s.html" % (renderable_slide.slide_type))
			result = template.render(**args)
			rendered_presentation.append_slide(result)

		for (template_filename, target_filename) in [ ("base/master.html", "index.html"), ("base/pybeamer.css", "pybeamer.css") ]:
			template = self._lookup.get_template(template_filename)
			result = template.render(**template_args)
			rendered_presentation.add_file(target_filename, result)
