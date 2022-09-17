#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2022 Johannes Bauer
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
import logging
import mako.lookup
import mako.exceptions
import markupsafe
import pyradium
from pyradium.Controller import ControllerManager
from pyradium.renderer import BaseRenderer
from .Acronyms import Acronyms
from .RenderedPresentation import RenderedPresentation
from .Exceptions import TemplateErrorException, MalformedStyleConfigurationException, UnknownSlideTypeException
from .Slide import RenderSlideDirective
from .Enums import PresentationFeature
from .Tools import JSONTools
from .StyleParameters import StyleParameters

_log = logging.getLogger(__spec__.name)

class CustomRenderers():
	def __init__(self):
		self._static_instances = {
			"acronym":	Acronyms(),
		}

	def __getitem__(self, name):
		if name in self._static_instances:
			return self._static_instances[name]
		return BaseRenderer.instanciate(name)

class Renderer():
	def __init__(self, presentation, rendering_params):
		self._rendered_slides = [ ]
		self._presentation = presentation
		self._rendering_params = rendering_params
		self._custom_renderers = CustomRenderers()
		self._lookup = mako.lookup.TemplateLookup(list(self._get_mako_lookup_directories()), strict_undefined = True, input_encoding = "utf-8", default_filters = [ "h" ])
		self._template_config_filename = self.lookup_styled_template_file("configuration.json")
		with open(self._template_config_filename) as f:
			self._template_config = json.load(f)
		self._plausibilize_template_config()
		self._ctrlr_mgr = ControllerManager(self)
		self._style_parameters = self._parse_style_parameters()

	def _plausibilize_template_config(self):
		for feature_name in self._template_config.get("dependencies", { }).get("feature", { }):
			try:
				PresentationFeature(feature_name)
			except ValueError as e:
				raise MalformedStyleConfigurationException(f"The stylesheet file {self._template_config_filename} contains an unknown feature in config[\"dependencies\"][\"feature\"]: {feature_name}") from e

	def _parse_style_parameters(self):
		params = StyleParameters(self._template_config.get("parameters", { }))
		parser = params.new_parser()
		for param in self._rendering_params.template_style_opts:
			parser.parse(param)
		return parser.values

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

		def _jsonify(obj):
			return markupsafe.Markup(json.dumps(JSONTools.round_dict_floats(obj), sort_keys = True, separators = (",", ":")))

		template_args = {
			"pyradium_version":			pyradium.VERSION,
			"renderer":					self,
			"presentation":				self._presentation,
			"template_error":			_template_error,
			"jsonify":					_jsonify,
			"preuri":					self.rendering_params.resource_uri,
			"preuri_ds":				self.rendering_params.resource_uri if self.rendering_params.resource_uri.startswith("/") else ("./" + self.rendering_params.resource_uri),
			"styleopt":					self._style_parameters,
		}
		if rendered_presentation is not None:
			template_args["rendered_presentation"] = rendered_presentation
		if additional_template_args is not None:
			template_args.update(additional_template_args)

		try:
			template = self._lookup.get_template(template_filename)
		except mako.exceptions.MakoException as e:
			raise UnknownSlideTypeException("Could not retrieve template necessary to render slide type %s (searched in: %s)." % (template_filename, ":".join(self._get_mako_lookup_directories()))) from e
		result = template.render(**template_args)
		return result

	def render(self, deploy_directory, resource_directory = None):
		if resource_directory is None:
			resource_directory = deploy_directory
		rendered_presentation = RenderedPresentation(self, deploy_directory = deploy_directory, resource_directory = resource_directory)

		for feature in self.rendering_params.presentation_features:
			rendered_presentation.add_feature(feature)
		_log.trace("Initial feature set: %s", ", ".join(sorted(feature.name for feature in rendered_presentation.features)))

		# Run it first to build the initial TOC and determine feature set
		self._compute_renderable_slides(rendered_presentation)

		_log.debug("Finalized feature set: %s", ", ".join(sorted(feature.name for feature in rendered_presentation.features)))

		# Then copy general dependencies by the used template
		rendered_presentation.handle_dependencies(self._template_config.get("files"))

		# Additionally look for dependencies which are effective because
		# specific slide types are used (e.g., a "quote" slide might need its
		# own CSS)
		for slide_type in self._determine_slide_types():
			slide_type_dependencies = self._template_config.get("dependencies", { }).get("slidetype", { }).get(slide_type)
			if slide_type_dependencies is not None:
				for feature_dependency in slide_type_dependencies.get("features", { }):
					feature_dependency = PresentationFeature(feature_dependency)
					rendered_presentation.add_feature(feature_dependency)
				rendered_presentation.handle_dependencies(slide_type_dependencies)

		# Lastly, add dependencies which are effective because a feature flag
		# is active (e.g., when "interactive" is used, a menu needs to be
		# generated which requires its own CSS)
		for feature in rendered_presentation.features:
			feature_dependency = self._template_config.get("dependencies", { }).get("feature", { }).get(feature.value)
			rendered_presentation.handle_dependencies(feature_dependency)

		# Then run it again to get the page numbers straight (e.g., the TOC
		# pages will be emitted, giving different page numbers). Initialize
		# schedule for second run as well.
		rendered_presentation.finalize_toc()
		rendered_presentation.init_schedule()
		self._compute_renderable_slides(rendered_presentation)
		rendered_presentation.finalize_toc()

		# Compute the schedule before the last run
		rendered_presentation.schedule.compute()

		# Third and final slide run
		for renderable_slide in self._compute_renderable_slides(rendered_presentation):
			additional_template_args = {
				"slide":			renderable_slide,
			}
			template_filename = "slide_%s.html" % (renderable_slide.slide_type)
			rendered_slide = self.render_file(template_filename, rendered_presentation = rendered_presentation, additional_template_args = additional_template_args)
			rendered_presentation.append_slide(rendered_slide)

		rendered_index = self.render_file("base/index.html", rendered_presentation = rendered_presentation)
		rendered_presentation.add_file(self.rendering_params.index_filename, rendered_index, to_deployment_dir = True)

		return rendered_presentation
