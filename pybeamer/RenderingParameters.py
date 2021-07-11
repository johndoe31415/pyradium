#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
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

import os

class RenderingParameters():
	def __init__(self, template_style = "default", honor_pauses = True, extra_template_dirs = None, include_dirs = None):
		self._template_style = template_style
		self._honor_pauses = honor_pauses
		self._template_dirs = [ os.path.expanduser("~/.config/pybeamer/templates"), os.path.dirname(os.path.realpath(__file__)) + "/templates" ]
		if extra_template_dirs is not None:
			self._template_dirs += extra_template_dirs
		if include_dirs is None:
			self._include_dirs = [ ]
		else:
			self._include_dirs = list(include_dirs)

	@property
	def geometry_x(self):
		return 1280

	@property
	def geometry_y(self):
		return 720

	@property
	def template_style(self):
		return self._template_style

	@property
	def honor_pauses(self):
		return self._honor_pauses

	@property
	def template_dirs(self):
		return iter(self._template_dirs)

	@property
	def include_dirs(self):
		return iter(self._include_dirs)
