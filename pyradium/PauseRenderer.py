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

from .Tools import XMLTools
from .Exceptions import DuplicateOrderException

class PauseRenderer():
	def __init__(self, content_containers, honor_pauses = True):
		self._content_containers = content_containers
		self._honor_pauses = honor_pauses
		self._used_order_ids = set()

	def _clone_containers(self):
		return { name: XMLTools.clone(container_node) for (name, container_node) in self._content_containers.items() }

	def _enumerate_pause_nodes_of(self, root_node):
		for pause_node in XMLTools.findall_recurse(root_node, "s:pause"):
			if not pause_node.hasAttribute("order"):
				if len(self._used_order_ids) == 0:
					assigned_order_id = 1
				else:
					assigned_order_id = max(self._used_order_ids) + 1
			else:
				assigned_order_id = int(pause_node.getAttribute("order"))
			if assigned_order_id in self._used_order_ids:
				raise DuplicateOrderException("Duplicate order ID: %d" % (assigned_order_id))
			self._used_order_ids.add(assigned_order_id)
			pause_node.setAttribute("order", str(assigned_order_id))

	def _enumerate_pause_nodes(self):
		for (name, container_node) in sorted(self._content_containers.items()):
			self._enumerate_pause_nodes_of(container_node)

	def _debug_result(self, rendered_containers):
		if len(rendered_containers) <= 1:
			return
		print("%d rendered containers:" % (len(rendered_containers)))
		for (index, rendered_container) in enumerate(rendered_containers):
			for (name, container_node) in sorted(rendered_container.items()):
				print("%s.%d:" % (name, index))
				print(XMLTools.inner_toxml(container_node))
				print()
		print("=" * 120)

	def render(self):
		if self._honor_pauses:
			self._enumerate_pause_nodes()

			rendered_containers = [ self._clone_containers() for _ in range(len(self._used_order_ids) + 1) ]
			sorted_order_ids = list(sorted(self._used_order_ids))

			for (max_order_id, rendered_container) in zip(sorted_order_ids, rendered_containers):
				for container_node in rendered_container.values():
					for pause_node in XMLTools.findall_recurse(container_node, "s:pause"):
						order = int(pause_node.getAttribute("order"))
						if order >= max_order_id:
							XMLTools.remove_siblings_after(pause_node)
						else:
							XMLTools.remove_node(pause_node)
		else:
			rendered_containers = [ self._clone_containers() ]

		# Remove all pause nodes from last container (the one which renders the
		# whole slide)
		for container_node in rendered_containers[-1].values():
			for pause_node in XMLTools.findall_recurse(container_node, "s:pause"):
				XMLTools.remove_node(pause_node)

#		self._debug_result(rendered_containers)
		return rendered_containers
