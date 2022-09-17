#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2022 Johannes Bauer
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

import os
import json
import hashlib
import subprocess
from pyradium.Exceptions import InvalidBooleanValueException, InvalidValueNodeException

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
		parent = node.parentNode
		if not isinstance(replacement, list):
			parent.replaceChild(replacement, node)
		else:
			if len(replacement) == 0:
				cls.remove_node(node)
			else:
				result = node.parentNode.replaceChild(replacement[-1], node)
				last_node = replacement[-1]
				for sibling_node in reversed(replacement[ : -1]):
					parent.insertBefore(sibling_node, last_node)
					last_node = sibling_node

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
		cls.walk(node, callback, predicate = lambda node: node.nodeType in [ node.TEXT_NODE, node.CDATA_SECTION_NODE ])
		return "".join(result)

	@classmethod
	def get_ns_tag(cls, node):
		if ":" in node.tagName:
			return node.tagName.split(":")
		else:
			return (None, node.tagName)

	@classmethod
	def walk(cls, node, callback, predicate = None, cancel_descent_predicate = None):
		if (cancel_descent_predicate is not None) and cancel_descent_predicate(node):
			return
		if (predicate is None) or predicate(node):
			callback(node)
		for child in node.childNodes:
			cls.walk(child, callback, predicate = predicate, cancel_descent_predicate = cancel_descent_predicate)

	@classmethod
	def walk_elements(cls, node, callback):
		cls.walk(node, callback, predicate = lambda node: node.nodeType == node.ELEMENT_NODE)

	@classmethod
	def findall_recurse_predicate(cls, root_node, predicate):
		result = [ ]
		def callback(node):
			if predicate(node):
				result.append(node)
		cls.walk_elements(root_node, callback)
		return result

	@classmethod
	def findall_recurse(cls, root_node, name):
		return cls.findall_recurse_predicate(root_node, predicate = lambda node: (node.nodeType == node.ELEMENT_NODE) and (node.tagName == name))

	@classmethod
	def findall_text(cls, root_node, recursive = False):
		for node in root_node.childNodes:
			if node.nodeType in [ node.TEXT_NODE, node.CDATA_SECTION_NODE ]:
				yield node
			elif recursive:
				yield from cls.findall_text(node, recursive = True)

	@classmethod
	def findall_generator(cls, root_node, name, namespace_uri = "*"):
		for node in root_node.childNodes:
			if (node.nodeType == node.ELEMENT_NODE) and (node.tagName == name) and (namespace_uri in ("*", node.namespaceURI)):
				yield node

	@classmethod
	def findfirst(cls, root_node, name, namespace_uri = "*"):
		return next(cls.findall_generator(root_node, name, namespace_uri = namespace_uri))

	@classmethod
	def findall(cls, root_node, name, namespace_uri = "*"):
		return list(cls.findall_generator(root_node, name, namespace_uri = namespace_uri))

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

		# Finally, traverse the tree again and change tag names
		def visit(node):
			(ns, tag) = cls.get_ns_tag(node)
			if node.namespaceURI is None:
				new_prefix = None
				new_tagname = tag
			else:
				new_prefix = assigned_namespaces[node.namespaceURI]
				new_tagname = new_prefix + ":" + tag
			node.prefix = new_prefix
			node.tagName = new_tagname
			node.nodeName = new_tagname
		cls.walk_elements(node, visit)

		return assigned_namespaces

	@classmethod
	def inner_toxml(cls, node):
		return "".join(child.toxml() for child in node.childNodes)

	@classmethod
	def clone(cls, node):
		return node.cloneNode(deep = True)

	@classmethod
	def has_sub_elements(cls, node):
		for node in node.childNodes:
			if node.nodeType == node.ELEMENT_NODE:
				return True
		return False

	@classmethod
	def xml_to_dict(cls, node):
		if node is None:
			return None
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

	@classmethod
	def get_bool_attr(cls, node, attr_name, default_value = False):
		if not node.hasAttribute(attr_name):
			return default_value
		value = node.getAttribute(attr_name).lower().strip()
		if value in [ "1", "on", "true", "yes" ]:
			return True
		elif value in [ "0", "off", "false", "no" ]:
			return False
		else:
			raise InvalidBooleanValueException("Invalid boolean value for attribute %s of node %s." % (attr_name, node))

	@classmethod
	def get_node_value(cls, node, find_file_function = None):
		if node.hasAttribute("value"):
			return node.getAttribute("value")
		elif node.hasAttribute("src"):
			filename = node.getAttribute("src")
			if find_file_function is None:
				raise InvalidValueNodeException(f"Value node referenced filename '{filename}', but no lookup function passed internally.")
			full_filename = find_file_function(filename)
			with open(full_filename) as f:
				return f.read()
		else:
			return cls.inner_text(node)

class JSONTools():
	@classmethod
	def round_dict_floats(cls, obj, digits = 4):
		if isinstance(obj, float):
			return round(obj, digits)
		elif isinstance(obj, list):
			return [ cls.round_dict_floats(child, digits = digits) for child in obj ]
		elif isinstance(obj, dict):
			return { key: cls.round_dict_floats(value, digits = digits) for (key, value) in obj.items() }
		else:
			return obj

class ImageTools():
	@classmethod
	def get_image_info(cls, filename):
		image_info = json.loads(subprocess.check_output([ "convert", filename, "json:-" ]))[0]
		return image_info

	@classmethod
	def svg_canvas_size_to_object(cls, filename):
		cmd = [ "inkscape", "-g", "--verb=FitCanvasToDrawing;FileSave;FileQuit", filename ]
		subprocess.check_call(cmd)

class HashTools():
	_HASHFNC = hashlib.md5

	@classmethod
	def _update_file(cls, hashfnc, f):
		while True:
			chunk = f.read(1024 * 1024)
			if len(chunk) == 0:
				break
			hashfnc.update(chunk)

	@classmethod
	def hash_files(cls, filenames):
		hashfnc = HashTools._HASHFNC()
		for filename in filenames:
			with open(filename, "rb") as f:
				cls._update_file(hashfnc, f)
		return hashfnc.hexdigest()

	@classmethod
	def hash_file(cls, filename):
		return cls.hash_files([ filename ])

	@classmethod
	def hash_data(cls, data: bytes):
		return HashTools._HASHFNC(data).hexdigest()

class FileTools():
	@classmethod
	def base_random_file_on(cls, filename):
		dirname = os.path.dirname(filename)
		basename = os.path.basename(filename)
		while True:
			if dirname == "":
				rndname = f".{basename}_{os.urandom(8).hex()}"
			elif dirname == "/":
				rndname = f"/.{basename}_{os.urandom(8).hex()}"
			else:
				rndname = f"{dirname}/.{basename}_{os.urandom(8).hex()}"
			if not os.path.exists(rndname):
				return rndname
