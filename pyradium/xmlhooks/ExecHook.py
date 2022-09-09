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

import shutil
import xml.dom.minidom
from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry
from pyradium.Tools import XMLTools
from pyradium.CmdlineParser import CmdlineParser
from pyradium.Exceptions import FailedToLookupFileException, MalformedXMLInputException
from pyradium.CmdlineEscape import CmdlineEscape

@XMLHookRegistry.register_hook
class ExecHook(BaseHook):
	_TAG_NAME = "exec"

	@classmethod
	def handle(cls, rendered_presentation, node):
		if not node.hasAttribute("cmd"):
			raise MalformedXMLInputException("An s:exec node must have a 'cmd' attribute.")

		cmd_str = node.getAttribute("cmd")
		cmd = CmdlineParser().parse(cmd_str)
		if not cmd[0].startswith("/"):
			# Not an absolute path given, look up path of executable
			try:
				full_executable_path = rendered_presentation.renderer.lookup_include(cmd[0])
			except FailedToLookupFileException as e:
				# Try if this is a path command
				full_executable_path = shutil.which(cmd[0])
				if full_executable_path is None:
					raise FailedToLookupFileException("Could lookup executable \"%s\" neither in include dirs (%s) not in $PATH." % (cmd[0], str(e))) from e

		cmd[0] = full_executable_path
		properties = {
			"cmd":		cmd,
			"cache":	XMLTools.get_bool_attr(node, "cache", default_value = True),
		}

		exec_renderer = rendered_presentation.renderer.get_custom_renderer("exec")
		result = exec_renderer.render(properties)

		xml_data = result.data["stdout"]
		try:
			doc = xml.dom.minidom.parseString(xml_data)
		except xml.parsers.expat.ExpatError as e:
			raise MalformedXMLInputException("Ouptut of script execution (%s) returned invalid XML: %s" % (CmdlineEscape().cmdline(cmd), str(e))) from e

		root = doc.firstChild
		return list(root.childNodes)
