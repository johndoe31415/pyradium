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

import os
import logging
from .BaseAction import BaseAction
from .RenderingParameters import RenderingParameters
from .Presentation import Presentation
from .OrderedSet import OrderedSet
from .Slide import RenderSlideDirective
from .Acronyms import AcronymDirective
from .Tools import XMLTools, HashTools
from .CmdlineParser import CmdlineParser

_log = logging.getLogger(__spec__.name)

class ActionHashPresentation(BaseAction):
	def run(self):
		self._rendering_parameters = RenderingParameters(include_dirs = [ os.path.dirname(self._args.infile) or "." ] + self._args.include_dir)
		presentation = Presentation.load_from_file(self._args.infile, self._rendering_parameters)

		# The first dependencies are the XML files themselves
		self._dependencies = OrderedSet()
		self._dependencies |= presentation.sources

		# Then we iterate throught the directives
		for directive in presentation.content:
			self._handle_directive(directive)

		hash_value = HashTools.hash_files(self._dependencies)
		print(hash_value)

	def _add_dependency(self, relative_filename):
		abs_filename = self._rendering_parameters.include_dirs.lookup(relative_filename)
		self._dependencies.add(abs_filename)

	def _visit_node(self, node):
		if node.tagName == "s:img":
			self._add_dependency(node.getAttribute("src"))
		elif node.tagName in [ "s:code", "s:term" ]:
			if node.hasAttribute("src"):
				self._add_dependency(node.getAttribute("src"))
		elif node.tagName == "s:exec":
			cmdline = CmdlineParser().parse(node.getAttribute("cmd"))
			self._add_dependency(cmdline[0])

	def _handle_directive(self, directive):
		if isinstance(directive, RenderSlideDirective):
			XMLTools.walk_elements(directive.xmlnode, self._visit_node)
		elif isinstance(directive, AcronymDirective):
			self._add_dependency(directive.src)
