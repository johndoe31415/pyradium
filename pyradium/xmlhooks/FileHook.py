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

import os
import hashlib
from pyradium.xmlhooks.XMLHookRegistry import BaseHook, XMLHookRegistry, ReplacementFragment
from pyradium.Exceptions import MalformedXMLInputException

@XMLHookRegistry.register_hook
class FileHook(BaseHook):
	_TAG_NAME = "file"

	@classmethod
	def handle(cls, rendered_presentation, node):
		if not node.hasAttribute("src"):
			raise MalformedXMLInputException("File node needs 'src' attribute set.")

		filename_key = rendered_presentation.renderer.presentation.meta.get("filename-key", "")
		src_filename = rendered_presentation.renderer.lookup_include(node.getAttribute("src"))
		basename = os.path.basename(src_filename)
		filename_hash = hashlib.md5((basename + filename_key).encode("utf-8")).hexdigest()
		if rendered_presentation.renderer.rendering_params.resource_uri != "":
			target_filename = f"{rendered_presentation.renderer.rendering_params.resource_uri}/incfiles/{filename_hash}/{basename}"
		else:
			target_filename = f"incfiles/{filename_hash}/{basename}"
		rendered_presentation.copy_abs_file(src_filename, target_filename)

		replacement_node = node.ownerDocument.createElement("a")
		replacement_node.setAttribute("href", target_filename)

		if len(node.childNodes) == 0:
			# Include the literal file basename as text
			replacement_node.appendChild(node.ownerDocument.createTextNode(basename))
		else:
			for child in list(node.childNodes):
				replacement_node.appendChild(child)

		return ReplacementFragment(replacement = replacement_node)
