#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

from .Tools import XMLTools
from .Exceptions import UndefinedContentException
from .BaseDirective import BaseDirective
from .RenderableSlide import RenderableSlide
from .PauseRenderer import PauseRenderer
from pybeamer.xmlhooks.XMLHookRegistry import XMLHookRegistry

class RenderSlideDirective(BaseDirective):
	def __init__(self, xmlnode):
		assert(xmlnode.tagName == "slide")
		self._dom = xmlnode
		if not self._dom.hasAttribute("type"):
			self._dom.setAttribute("type", "default")
		self._slide_vars = self._get_slide_vars()
		self._content_containers = { }
		for content_node in XMLTools.findall(self._dom, "s:content"):
			self._content_containers[content_node.getAttribute("name")] = content_node
		if len(self._content_containers) == 0:
			self._content_containers["default"] = self._dom
		self._enumerate_pause_nodes()

	@property
	def containers(self):
		return self._content_containers

	def clone_containers(self):
		return { name: container.cloneNode(deep = True) for (name, container) in self._content_containers.items() }

	@property
	def slide_type(self):
		return self._dom.getAttribute("type")

	def _get_slide_vars(self):
		# First search DOM for any variables
		slide_vars = { }
		for node in XMLTools.findall(self._dom, "s:var"):
			(key, value) = (node.getAttribute("name"), node.getAttribute("value"))
			slide_vars[key] = value
		return slide_vars

#	def _get_pause_order_

	def _enumerate_pause_nodes_of(self, root_node, start_order):
		pause_node_count = 0
		order = start_order
		for pause_node in XMLTools.findall_recurse(root_node, "s:pause"):
			if not pause_node.hasAttribute("order"):
				pause_node.setAttribute("order", str(order))
			else:
				pause_node.setAttribute("order", str(int(pause_node.getAttribute("order"))))
			pause_node_count += 1
			order += 1
		return pause_node_count

	def _enumerate_pause_nodes(self):
		order = 1
		total_pause_node_count = 0
		for (name, container_node) in sorted(self._content_containers.items()):
			pause_node_count = self._enumerate_pause_nodes_of(container_node, order)
			total_pause_node_count += pause_node_count
			order += pause_node_count
		return total_pause_node_count

	def render(self, renderer):
		paused_containers = PauseRenderer(self, honor_pauses = renderer.rendering_params.honor_pauses).render()

		for paused_container in paused_containers:
			for container_node in paused_container.values():
				XMLHookRegistry.mangle(container_node)
			yield RenderableSlide(slide_type = self.slide_type, content_containers = paused_container, slide_vars = self._slide_vars)

	def __repr__(self):
		return "Slide<%s>" % (self.slide_type)
