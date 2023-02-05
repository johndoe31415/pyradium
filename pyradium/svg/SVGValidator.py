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

import enum
import logging
import functools
import subprocess
import xml.dom.minidom
from pyradium.Tools import XMLTools
from pyradium.Exceptions import SVGValidationError
from .SVGStyle import SVGStyle

_log = logging.getLogger(__spec__.name)

class SVGValidatorErrorClass(enum.IntEnum):
	CheckDisabled = 0
	EmitWarning = 1
	ThrowException = 2

class SVGValidator():
	def __init__(self, check_missing_fonts: SVGValidatorErrorClass = SVGValidatorErrorClass.EmitWarning):
		self._check_missing_fonts = check_missing_fonts

	@functools.lru_cache(maxsize = 1000)
	def _have_font(self, font_family):
		return len(subprocess.check_output([ "fc-list", font_family ])) > 0

	def _validate_fonts(self, svg_filename, root):
		found_missing = set()
		for tagname in [ "text", "tspan" ]:
			for node in XMLTools.findall_recurse(root, tagname):
				style = SVGStyle.from_node(node)
				font_family = style["font-family"]
				if font_family is None:
					continue
				if (font_family[0] == "'") and (font_family[-1] == "'") and (len(font_family) >= 2):
					font_family = font_family[1 : -1]

				if font_family in found_missing:
					# Already reported.
					continue

				if not self._have_font(font_family):
					found_missing.add(font_family)
					if self._check_missing_fonts == SVGValidatorErrorClass.EmitWarning:
						_log.warning("SVG file %s has missing font: %s", svg_filename, font_family)
					elif self._check_missing_fonts == SVGValidatorErrorClass.ThrowException:
						raise SVGValidationError(f"SVG file {svg_filename} has missing font: {font_family}")

	def validate(self, svg_filename):
		root = xml.dom.minidom.parse(svg_filename)
		if self._check_missing_fonts != SVGValidatorErrorClass.CheckDisabled:
			self._validate_fonts(svg_filename, root)

if __name__ == "__main__":
	validator = SVGValidator()
	validator.validate("examples/3dbox.svg")
