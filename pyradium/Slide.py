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

from pyradium.xmlhooks.XMLHookRegistry import XMLHookRegistry
from .Tools import XMLTools
from .BaseDirective import BaseDirective
from .RenderableSlide import RenderableSlide
from .PauseRenderer import PauseRenderer

class RenderSlideDirective(BaseDirective):
	def __init__(self, xmlnode):
		assert(xmlnode.tagName == "slide")
		self._dom = xmlnode
		if not self._dom.hasAttribute("type"):
			self._dom.setAttribute("type", "default")
		self._xml_slide_vars = self._get_xml_slide_vars()
		self._content_containers = { }
		for content_node in XMLTools.findall(self._dom, "s:content"):
			self._content_containers[content_node.getAttribute("name")] = content_node
		if len(self._content_containers) == 0:
			self._content_containers["default"] = self._dom

	@property
	def xmlnode(self):
		return self._dom

	@property
	def slide_type(self):
		return self._dom.getAttribute("type")

	def get_xml_slide_var(self, key):
		return self._xml_slide_vars.get(key)

	def _get_xml_slide_vars(self):
		# First search DOM for any variables
		slide_vars = { }
		for node in XMLTools.findall(self._dom, "s:var"):
			(key, value) = (node.getAttribute("name"), node.getAttribute("value"))
			slide_vars[key] = value
			XMLTools.remove_node(node)
		return slide_vars

	def compute_slide_vars(self, rendered_presentation, sub_slide_index):
		slide_vars = dict(self._xml_slide_vars)
		slide_vars.update({
			"current_slide_number":	rendered_presentation.current_slide_number,
			"total_slide_count":	rendered_presentation.total_slide_count,
			"toc":					rendered_presentation.frozen_toc,
			"sub_slide_index":		sub_slide_index,
			"generate_uid":			lambda: rendered_presentation.next_unique_id,
		})
		if rendered_presentation.frozen_toc is not None:
			slide_vars["toc_entry"] = rendered_presentation.frozen_toc.current_item
		return slide_vars

	def emit_nocontent_slide(self, rendered_presentation, content_containers, additional_slide_var_list = None):
		rendered_presentation.advance_slide()
		# We need to render the content containers even though they're not
		# used: Traversal of the containers is necessary because they might
		# contain instructions such as the <s:time> specification.
		for container_node in content_containers.values():
			XMLHookRegistry.mangle(rendered_presentation, container_node)
		if additional_slide_var_list is None:
			additional_slide_var_list = [ { } ]
		elif not isinstance(additional_slide_var_list, list):
			additional_slide_var_list = [ additional_slide_var_list ]

		for (sub_slide_index, additional_slide_vars) in enumerate(additional_slide_var_list):
			slide_vars = self.compute_slide_vars(rendered_presentation, sub_slide_index)
			slide_vars.update(additional_slide_vars)
			yield RenderableSlide(slide_type = self.slide_type, content_containers = None, slide_vars = slide_vars)

	def emit_content_slide(self, rendered_presentation, content_containers, additional_slide_vars = None):
		rendered_presentation.advance_slide()
		paused_containers = PauseRenderer(content_containers, honor_pauses = rendered_presentation.renderer.rendering_params.honor_pauses).render()

		for (sub_slide_index, paused_container) in enumerate(paused_containers):
			for container_node in paused_container.values():
				XMLHookRegistry.mangle(rendered_presentation, container_node)

			slide_vars = self.compute_slide_vars(rendered_presentation, sub_slide_index)
			if additional_slide_vars is not None:
				slide_vars.update(additional_slide_vars)
			yield RenderableSlide(slide_type = self.slide_type, content_containers = paused_container, slide_vars = slide_vars)

	def render(self, rendered_presentation):
		controller = rendered_presentation.renderer.controllers.get_controller(self, self._content_containers, rendered_presentation)
		if controller is None:
			yield from self.emit_content_slide(rendered_presentation, self._content_containers)
		else:
			yield from controller.render()

	def __repr__(self):
		return "RenderSlideDirective<%s>" % (self.slide_type)
