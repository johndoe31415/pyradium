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

class XMLTools():
	@classmethod
	def child_tagname(cls, node, tag_name):
		if node is None:
			return None
		if isinstance(tag_name, str):
			for child in node.childNodes:
				if (child.nodeType == node.ELEMENT_NODE) and (child.tagName == tag_name):
					return child
			return None
		else:
			current = node
			for path_element in tag_name:
				current = cls.child_tagname(current, path_element)
			return current

	@classmethod
	def remove_node(cls, node):
		if node.parentNode is not None:
			node.parentNode.removeChild(node)

	@classmethod
	def replace_node(cls, node, replacement):
		node.parentNode.replaceChild(replacement, node)

	@classmethod
	def remove_siblings_after(cls, node):
		while node is not None:
			next_node = node.nextSibling
			cls.remove_node(node)
			node = next_node

	@classmethod
	def inner_text(cls, node):
		result = [ ]
		def callback(node):
			result.append(node.wholeText)
		cls.walk(node, callback, predicate = lambda node: node.nodeType == node.TEXT_NODE)
		return "".join(result)

	@classmethod
	def get_ns_tag(cls, node):
		if ":" in node.tagName:
			return node.tagName.split(":")
		else:
			return (None, node.tagName)

	@classmethod
	def walk(cls, node, callback, predicate = None):
		if (predicate is None) or predicate(node):
			callback(node)
		for child in node.childNodes:
			cls.walk(child, callback)

	@classmethod
	def walk_elements(cls, node, callback):
		cls.walk(node, callback, predicate = lambda node: node.nodeType == node.ELEMENT_NODE)

	@classmethod
	def findall_recurse_predicate(cls, root_node, predicate):
		result = [ ]
		def callback(node, parent):
			if predicate(node):
				result.append((node, parent))
		cls.walk_elements(root_node, callback)
		return result

	@classmethod
	def findall_recurse(cls, root_node, name):
		return cls.findall_recurse_predicate(root_node, predicate = lambda node: node.tag == name)

	@classmethod
	def normalize_ns(cls, node, known_namespaces = None):
		if known_namespaces is None:
			known_namespaces = { }

		# First collect all known namespace URIs
		present_namespaces = set()
		def visit(node):
			if node.namespaceURI is not None:
				present_namespaces.add(node.namespaceURI)
		cls.walk_elements(node, visit)

		# Then assign them
		assigned_namespaces = { }
		namespace_id = 0
		for uri in sorted(present_namespaces):
			if uri in known_namespaces:
				assigned_namespaces[uri] = known_namespaces[uri]
			else:
				assigned_namespaces[uri] = "ns%d" % (namespace_id)
				namespace_id += 1

		# Remove old namespace assignments
		remove_attributes = set(key for key in node.attributes.keys() if key.startswith("xmlns:"))
		for key in remove_attributes:
			node.attributes.removeNamedItem(key)

		# Append new namespace assignments to root element
		for (uri, key) in assigned_namespaces.items():
			node.setAttribute("xmlns:%s" % (key), uri)

		# Finally, traverse the tree again and change tag Names
		def visit(node):
			(ns, tag) = cls.get_ns_tag(node)
			if node.namespaceURI is None:
				new_tagname = tag
			else:
				new_tagname = assigned_namespaces[node.namespaceURI] + ":" + tag
			node.tagName = new_tagname
		cls.walk_elements(node, visit)

	@classmethod
	def inner_toxml(cls, node):
		return "".join(child.toxml() for child in node.childNodes)


	@classmethod
	def has_sub_elements(cls, node):
		for node in node.childNodes:
			if node.nodeType == node.ELEMENT_NODE:
				return True
		return False

	@classmethod
	def xml_to_dict(cls, node):
		if cls.has_sub_elements(node):
			result = { }
			for child in node.childNodes:
				if child.nodeType == node.ELEMENT_NODE:
					key = child.tagName
					value = cls.xml_to_dict(child)
					result[key] = value
			return result
		else:
			return cls.inner_text(node)
