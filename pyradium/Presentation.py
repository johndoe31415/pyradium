#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
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
import hashlib
import subprocess
import logging
import xml.dom.minidom
import pyradium
from pyradium.Agenda import Agenda
from .Tools import XMLTools, JSONTools
from .TOC import TOCElement, TOCDirective
from .Slide import RenderSlideDirective
from .Acronyms import AcronymDirective
from .Exceptions import XMLFileNotFoundException, MalformedXMLInputException, JSONFileNotFoundException, MalformedJSONInputException

_log = logging.getLogger(__spec__.name)

class Presentation():
	_NAMESPACES = {
		"https://github.com/johndoe31415/pyradium":		"s",
	}

	def __init__(self, meta, content, sources, variables):
		self._meta = meta
		self._content = content
		self._sources = sources
		self._variables = variables
		self._validate_metadata()

	@property
	def meta(self):
		return self._meta

	@property
	def content(self):
		return self._content

	@property
	def sources(self):
		return self._sources

	@property
	def variables(self):
		return self._variables

	@classmethod
	def _merge_metadata(cls, meta_dict, injected_dict):
		if not isinstance(injected_dict, dict):
			raise MalformedJSONInputException(f"Could not inject metadata (not a dictionary): {str(injected_dict)}")
		meta_dict.update(injected_dict)
		return meta_dict

	@classmethod
	def parse_xml(cls, filename):
		try:
			dom = xml.dom.minidom.parse(filename)
		except FileNotFoundError as e:
			raise XMLFileNotFoundException(f"Cannot parse {filename}: {str(e)}") from e
		except xml.parsers.expat.ExpatError as e:
			raise MalformedXMLInputException(f"Cannot parse {filename}: {str(e)}") from e
		XMLTools.normalize_ns(dom.documentElement, cls._NAMESPACES)
		presentation = XMLTools.child_tagname(dom, "presentation")
		if presentation is None:
			raise MalformedXMLInputException("No 'presentation' node is present as top node of the XML input document.")
		return (dom, presentation)

	@classmethod
	def _parse_variables(cls, json_filenames: list[str] | None, rendering_parameters):
		variables = { }

		if (json_filenames is not None) and (len(json_filenames) > 0) and (rendering_parameters is None):
			_log.warning("Ingored variables directive because no include directories are known: %s", str(json_filenames))
			return variables

		for filename in json_filenames:
			lookup_filename = rendering_parameters.include_dirs.lookup(filename)
			try:
				with open(lookup_filename) as f:
					variable = json.load(f)
			except FileNotFoundError as e:
				raise JSONFileNotFoundException(f"Cannot load variable data from {lookup_filename}: {str(e)}") from e
			except json.decoder.JSONDecodeError as e:
				raise MalformedJSONInputException(f"Cannot parse variable data from {lookup_filename}: {str(e)}") from e

			if not isinstance(variable, dict):
				raise MalformedJSONInputException(f"Data type error after parsing {lookup_filename}: expected root node of type dict, but got \"{type(variable).__name__}\"")

			variables = JSONTools.merge_dicts(variables, variable)
		print(variables)
		return variables

	@classmethod
	def load_from_file(cls, filename, rendering_parameters = None):
		(dom, presentation) = cls.parse_xml(filename)
		meta = None
		content = [ ]
		sources = [ filename ]
		for child in presentation.childNodes:
			if child.nodeType != child.ELEMENT_NODE:
				continue

			if child.tagName == "meta":
				meta = XMLTools.xml_to_dict(XMLTools.child_tagname(dom, ("presentation", "meta")), multikeys = [ "variables" ])
			elif child.tagName == "slide":
				if not XMLTools.get_bool_attr(child, "hide"):
					content.append(RenderSlideDirective(child))
			elif child.tagName == "include":
				src = child.getAttribute("src")
				if rendering_parameters is not None:
					sub_presentation_filename = rendering_parameters.include_dirs.lookup(src)
					sub_presentation = cls.load_from_file(sub_presentation_filename)
					content += sub_presentation.content
					sources += sub_presentation.sources
				else:
					_log.warning("Ingored include directive because no include directories are known: %s", src)
			elif child.tagName in [ "chapter", "section", "subsection" ]:
				toc_element = TOCElement(child.tagName)
				toc_directive = TOCDirective(toc_element, XMLTools.inner_text(child))
				content.append(toc_directive)
			elif child.tagName == "acronyms":
				content.append(AcronymDirective(child))
			else:
				_log.warning("Ignored unknown tag '%s'.", child.tagName)
		if (rendering_parameters is not None) and (rendering_parameters.injected_metadata is not None):
			meta = cls._merge_metadata(meta, rendering_parameters.injected_metadata)
		if meta is not None:
			variables = cls._parse_variables(meta.get("variables"), rendering_parameters = rendering_parameters)
		else:
			variables = { }
		return cls(meta, content, sources, variables)

	def _validate_metadata(self):
		if self._meta is None:
			return
		if "agenda" in self._meta:
			self._meta["agenda"] = Agenda.parse(text = self._meta["agenda"])

	def _determine_sha256(self, filename):
		with open(filename, "rb") as f:
			return hashlib.sha256(f.read()).hexdigest()

	def _determine_git_commit(self, filename):
		try:
			return subprocess.check_output([ "git", "rev-list", "-1", "--all", filename ], stderr = subprocess.DEVNULL).decode().rstrip("\n")
		except subprocess.CalledProcessError:
			return None

	def _determine_version(self, filename):
		return {
			"sha256":	self._determine_sha256(filename),
			"git":		self._determine_git_commit(filename),
		}

	@property
	def version_information(self):
		return [
			{
				"filename":	filename,
				"version":	self._determine_version(filename),
			} for filename in self.sources ]

	@property
	def meta_info(self):
		return {
			"renderer":			pyradium.VERSION,
			"source_versions":	self.version_information,
		}

	def __iter__(self):
		return iter(self._content)
