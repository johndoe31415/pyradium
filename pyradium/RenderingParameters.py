#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2023 Johannes Bauer
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

import dataclasses
import os
from .FileLookup import FileLookup

@dataclasses.dataclass()
class RenderingParameters():
	template_style: str = "default"
	template_style_opts: list[str] | None = None
	honor_pauses: bool = True
	collapse_animation: bool = False
	template_dirs: list[str] | None = dataclasses.field(default = None, init = False)
	extra_template_dirs: list[str] | None = None
	include_dirs: list[str] | None = None
	index_filename: str = "index.html"
	resource_uri: str = ""
	geometry: tuple = (1280, 720)
	image_max_dimension: int = 1920
	presentation_features: set | None = None
	injected_metadata: dict | None = None
	trustworthy_source: bool = False

	@property
	def geometry_x(self):
		return self.geometry[0]

	@property
	def geometry_y(self):
		return self.geometry[1]

	def __post_init__(self):
		# Initialize default values
		if self.template_style_opts is None:
			self.template_style_opts = [ ]
		if self.extra_template_dirs is None:
			self.extra_template_dirs = [ ]
		if self.include_dirs is None:
			self.include_dirs = [ ]
		if self.presentation_features is None:
			self.presentation_features = frozenset()
		else:
			self.presentation_features = frozenset(self.presentation_features)

		# Compute non-settable variables and initialize wrappers
		self.template_dirs = FileLookup([ os.path.expanduser("~/.config/pyradium/templates"), os.path.dirname(os.path.realpath(__file__)) + "/templates" ] + self.extra_template_dirs)
		self.include_dirs = FileLookup(self.include_dirs)
