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

import importlib

class BaseController():
	def __init__(self, slide, content_containers, rendered_presentation):
		self._slide = slide
		self._content_containers = content_containers
		self._rendered_presentation = rendered_presentation

	@property
	def slide(self):
		return self._slide

	@property
	def content_containers(self):
		return self._content_containers

	@property
	def rendered_presentation(self):
		return self._rendered_presentation

	def render(self):
		return self._slide.emit_slide(self._rendered_presentation, self._content_containers)

class ControllerManager():
	def __init__(self, renderer):
		self._renderer = renderer
		self._cached = { }

	def _controller_definition(self, name):
		return self._renderer.template_config.get("controllers", { }).get(name)

	def get_controller(self, slide, content_containers, rendered_presentation):
		if slide.slide_type not in self._cached:
			definition = self._controller_definition(slide.slide_type)
			if definition is not None:
				module_filename = self._renderer.lookup_styled_template_file(definition["file"])
				module = importlib.machinery.SourceFileLoader("controller_module", module_filename).load_module()
				handler_class = getattr(module, definition.get("class", "Controller"))
			else:
				handler_class = None
			self._cached[slide.slide_type] = handler_class
		else:
			handler_class = self._cached[slide.slide_type]

		if handler_class is None:
			return

		controller = handler_class(slide, content_containers, rendered_presentation)
		return controller
