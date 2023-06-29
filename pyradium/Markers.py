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

import re
from .BaseDirective import BaseDirective
from .Exceptions import MalformedXMLInputException

class MarkerDirective(BaseDirective):
	_VALID_MARKER_RE = re.compile("[_a-zA-Z0-9]+")

	def __init__(self, name):
		self._name = name
		if self._VALID_MARKER_RE.fullmatch(name) is None:
			raise MalformedXMLInputException(f"Markers may only contain characters a-z, A-Z, 0-9 and _ character, but found: {name}")


	@property
	def name(self):
		return self._name

	def render(self, rendered_presentation):
		rendered_presentation.markers[self.name] = rendered_presentation.current_slide_number
