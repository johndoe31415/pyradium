#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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
import mako.lookup
import pyradium
from pyradium.Controller import ControllerManager
from pyradium.renderer.LatexFormulaRenderer import LatexFormulaRenderer
from pyradium.renderer.ImageRenderer import ImageRenderer
from pyradium.renderer.ExecRenderer import ExecRenderer
from .Acronyms import Acronyms
from .RendererCache import RendererCache
from .RenderedPresentation import RenderedPresentation
from .Enums import PresentationMode
from .Exceptions import TemplateErrorException
from .Slide import RenderSlideDirective

class Renderer():
	def __init__(self, presentation, rendering_params):
		self._rendered_slides = [ ]
		self._presentation = presentation
		self._rendering_params = rendering_params
		self._custom_renderers = {
			"latex":	RendererCache(LatexFormulaRenderer()),
			"img":		RendererCache(ImageRenderer()),
			"exec":		RendererCache(ExecRenderer()),
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

	def _determine_slide_types(self):
		slide_types = set()
		for directive in self._presentation:
			if isinstance(directive, RenderSlideDirective):
				slide_types.add(directive.slide_type)
		return slide_types

	def _compute_renderable_slides(self, rendered_presentation):
		renderable_slides = [ ]
		for directive in self._presentation:
			generator = directive.render(rendered_presentation)
			if generator is not None:
				renderable_slides += generator
		return renderable_slides

	def render_file(self, template_filename, rendered_presentation = None, additional_template_args = None):
		def _template_error(text):
			raise TemplateErrorException(text)

		template_args = {
			"pyradium_version":			pyradium.VERSION,
			"renderer":					self,
			"presentation":				self._presentation,
			"template_error":			_template_error,
		}
		if rendered_presentation is not None:
			template_args["rendered_presentation"] = rendered_presentation
		if additional_template_args is not None:
			template_args.update(additional_template_args)

		template = self._lookup.get_template(template_filename)
		result = template.render(**template_args)
		return result

	def render(self, deploy_directory):
		rendered_presentation = RenderedPresentation(self, deploy_directory = deploy_directory)

		for feature in self.rendering_params.presentation_features:
			rendered_presentation.add_feature(feature.value)
		if self.rendering_params.presentation_mode == PresentationMode.Interactive:
			rendered_presentation.add_feature("interactive")

		# Run it first to build the initial TOC and determine feature set
		self._compute_renderable_slides(rendered_presentation)

		# Then copy the dependencies
		rendered_presentation.handle_dependencies(self._template_config.get("files"))
		for slide_type in self._determine_slide_types():
			rendered_presentation.handle_dependencies(self._template_config.get("dependencies", { }).get("slidetype", { }).get(slide_type))
		for feature in rendered_presentation.features:
			rendered_presentation.handle_dependencies(self._template_config.get("dependencies", { }).get("feature", { }).get(feature))

		# Then run it again to get the page numbers straight (e.g., the TOC
		# pages will be emitted, giving different page numbers)
		rendered_presentation.finalize_toc()
		self._compute_renderable_slides(rendered_presentation)
		rendered_presentation.finalize_toc()

		# Compute the schedule
		rendered_presentation.schedule.compute()

		for renderable_slide in self._compute_renderable_slides(rendered_presentation):
			additional_template_args = {
				"slide":			renderable_slide,
			}
			template_filename = "slide_%s.html" % (renderable_slide.slide_type)
			rendered_slide = self.render_file(template_filename, rendered_presentation = rendered_presentation, additional_template_args = additional_template_args)
			rendered_presentation.append_slide(rendered_slide)

		rendered_index = self.render_file("base/index.html", rendered_presentation = rendered_presentation)
		rendered_presentation.add_file(self.rendering_params.index_filename, rendered_index)
		return rendered_presentation
