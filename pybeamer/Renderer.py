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
import mako.lookup
import pybeamer
from pybeamer.Controller import ControllerManager
from pybeamer.renderer.LatexFormulaRenderer import LatexFormulaRenderer
from pybeamer.renderer.ImageRenderer import ImageRenderer
from .Acronyms import Acronyms
from .RendererCache import RendererCache
from .RenderedPresentation import RenderedPresentation
from .Enums import PresentationMode
from .Exceptions import TemplateErrorException

class Renderer():
	def __init__(self, presentation, rendering_params):
		self._rendered_slides = [ ]
		self._presentation = presentation
		self._rendering_params = rendering_params
		self._custom_renderers = {
			"latex":	RendererCache(LatexFormulaRenderer()),
			"img":		RendererCache(ImageRenderer()),
			"acronym":	Acronyms(),
		}
		self._lookup = mako.lookup.TemplateLookup(list(self._get_mako_lookup_directories()), strict_undefined = True, input_encoding = "utf-8", default_filters = [ "h" ])
		with open(self.lookup_styled_template_file("configuration.json")) as f:
			self._template_config = json.load(f)
		self._ctrlr_mgr = ControllerManager(self)

	@property
	def presentation(self):
		return self._presentation

	def _get_mako_lookup_directories(self):
		for dirname in self._rendering_params.template_dirs:
			yield dirname
			yield dirname + "/" + self._rendering_params.template_style

	@property
	def rendering_params(self):
		return self._rendering_params

	@property
	def template_config(self):
		return self._template_config

	@property
	def controllers(self):
		return self._ctrlr_mgr

	def get_custom_renderer(self, name):
		return self._custom_renderers[name]

	def lookup_template_file(self, filename):
		return self._rendering_params.template_dirs.lookup(filename)

	def lookup_styled_template_file(self, filename):
		return self._rendering_params.template_dirs.lookup(self._rendering_params.template_style + "/" + filename)

	def lookup_include(self, filename):
		return self._rendering_params.include_dirs.lookup(filename)

	def _compute_renderable_slides(self, rendered_presentation):
		renderable_slides = [ ]
		for directive in self._presentation:
			generator = directive.render(rendered_presentation)
			if generator is not None:
				renderable_slides += generator
		return renderable_slides

	def _render_file(self, template_filename, rendered_presentation, template_args, target_filename = None):
		if target_filename is None:
			target_filename = os.path.basename(template_filename)
		template = self._lookup.get_template(template_filename)
		result = template.render(**template_args)
		rendered_presentation.add_file(target_filename, result)
		if target_filename.endswith(".css"):
			rendered_presentation.add_css(target_filename)

	def render(self, deploy_directory):
		def _template_error(text):
			raise TemplateErrorException(text)

		rendered_presentation = RenderedPresentation(self, deploy_directory = deploy_directory)
		template_args = {
			"pybeamer_version":			pybeamer.VERSION,
			"renderer":					self,
			"presentation":				self._presentation,
			"rendered_presentation":	rendered_presentation,
			"template_error":			_template_error,
		}

		rendered_presentation.copy_template_file("base/pybeamer.js")
		self._render_file("base/pybeamer.css", rendered_presentation, template_args)
		if self.rendering_params.presentation_mode == PresentationMode.Interactive:
			self._render_file("base/pybeamer_menu.css", rendered_presentation, template_args)
		self._render_file("base/pybeamer_tooltip.css", rendered_presentation, template_args)
		self._render_file("base/pybeamer_forms.css", rendered_presentation, template_args)

		for filename in self._template_config.get("files", { }).get("static", [ ]):
			rendered_presentation.copy_template_file("%s/%s" % (self._rendering_params.template_style, filename), destination_relpath = filename)
		for filename in self._template_config.get("files", { }).get("css", [ ]):
			rendered_presentation.copy_template_file("%s/%s" % (self._rendering_params.template_style, filename))
			rendered_presentation.add_css(filename)

		# Run it first to build the initial TOC
		self._compute_renderable_slides(rendered_presentation)

		# Then run it again to get the page numbers straight (e.g., the TOC
		# pages will be emitted, giving different page numbers)
		rendered_presentation.finalize_toc()
		self._compute_renderable_slides(rendered_presentation)
		rendered_presentation.finalize_toc()

		for renderable_slide in self._compute_renderable_slides(rendered_presentation):
			args = dict(template_args)
			args.update({
				"slide":			renderable_slide,
			})
			template = self._lookup.get_template("slide_%s.html" % (renderable_slide.slide_type))
			result = template.render(**args)
			rendered_presentation.append_slide(result)

		self._render_file("base/index.html", rendered_presentation, template_args, target_filename = self.rendering_params.index_filename)
		return rendered_presentation
