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
import contextlib
from .GenericTOC import GenericTOC
from .OrderedSet import OrderedSet
from .Schedule import PresentationSchedule, TimeSpecification
from .Enums import PresentationFeature

class RenderedPresentation():
	def __init__(self, renderer, deploy_directory, resource_directory):
		self._renderer = renderer
		self._deploy_directory = deploy_directory
		self._resource_directory = resource_directory
		self._rendered_slides = [ ]
		self._css = { }
		self._js = OrderedSet()
		self._toc = GenericTOC()
		self._frozen_toc = None
		self._added_files = set()
		self._current_slide_number = 0
		self._total_slide_count = 0
		self._uid = 0
		self._features = set()

		time_range = self._renderer.presentation.meta.get("presentation-time")
		if time_range is None:
			self._presentation_length_mins = None
		else:
			self._presentation_length_mins = TimeSpecification.parse(time_range, default_abs_interpretation = "h:m").duration_secs
		self._schedule = None

	def init_schedule(self):
		self._schedule = PresentationSchedule(self._presentation_length_mins)

	@property
	def next_unique_id(self):
		self._uid += 1
		return "uid_%x" % (self._uid)

	@property
	def current_slide_number(self):
		return self._current_slide_number

	@property
	def total_slide_count(self):
		return self._total_slide_count

	def advance_slide(self):
		self._current_slide_number += 1
		self._total_slide_count = max(self._total_slide_count, self._current_slide_number)
		self._toc.at_page(self.current_slide_number)
		if self.schedule is not None:
			self.schedule.have_slide(self.current_slide_number)

	def finalize_toc(self):
		self._frozen_toc = self._toc.finalize()
		self._toc = GenericTOC()
		self._current_slide_number = 0

	@property
	def renderer(self):
		return self._renderer

	@property
	def rendered_slides(self):
		return iter(self._rendered_slides)

	@property
	def js(self):
		return iter(self._js)

	@property
	def css(self):
		for (filename, order) in sorted(self._css.items(), key = lambda x: (x[1], x[0])):
			yield filename

	@property
	def schedule(self):
		return self._schedule

	def add_css(self, filename, order = None, target_directory = "/"):
		assert(target_directory.startswith("/"))
		assert(target_directory.endswith("/"))
		if order is None:
			order = len(self._css)
		key = target_directory[1:] + filename
		if key not in self._css:
			self._css[key] = order

	def add_js(self, filename):
		return self._js.add(filename)

	@property
	def toc(self):
		return self._toc

	@property
	def frozen_toc(self):
		return self._frozen_toc

	@property
	def features(self):
		return self._features

	def add_feature(self, feature):
		assert(isinstance(feature, PresentationFeature))
		self._features.add(feature)

	def has_feature(self, feature):
		if isinstance(feature, str):
			feature = PresentationFeature(feature)
		return feature in self.features

	def append_slide(self, rendered_slide):
		self._rendered_slides.append(rendered_slide)

	def add_file(self, destination_relpath, content, target_directory = "/", to_deployment_dir = False):
		assert(target_directory.startswith("/"))
		assert(target_directory.endswith("/"))
		if destination_relpath in self._added_files:
			return
		self._added_files.add(destination_relpath)
		directory = self._deploy_directory if to_deployment_dir else self._resource_directory
		filename = directory + target_directory + destination_relpath
		dirname = os.path.dirname(filename)
		with contextlib.suppress(FileExistsError):
			os.makedirs(dirname)
		with open(filename, "w" if isinstance(content, str) else "wb") as f:
			f.write(content)

	def copy_file(self, rel_filename, target_directory = "/"):
		if rel_filename in self._added_files:
			return
		source_filename = self.renderer.lookup_template_file(rel_filename)
		with open(source_filename, "rb") as f:
			self.add_file(rel_filename, f.read(), target_directory)

	def handle_dependencies(self, dependencies):
		if dependencies is None:
			return
		for rel_filename in dependencies.get("static", [ ]):
			self.copy_file(rel_filename, target_directory = "/template/")
		for rel_filename in dependencies.get("css", [ ]):
			if isinstance(rel_filename, str):
				self.copy_file(rel_filename, target_directory = "/template/")
				self.add_css(rel_filename, target_directory = "/template/")
			else:
				if rel_filename.get("render"):
					rendered_css = self.renderer.render_file(rel_filename["name"], rendered_presentation = self)
					self.add_file(rel_filename["name"], rendered_css, target_directory = "/template/")
				else:
					self.copy_file(rel_filename["name"], target_directory = "/template/")
				self.add_css(rel_filename["name"], target_directory = "/template/", order = rel_filename.get("order"))

	@property
	def meta_interactive(self):
		return {
			"slide_ratios":			self.schedule.slide_ratio_list,
			"presentation_time":	self.renderer.presentation.meta.get("presentation-time"),
		}

	@property
	def meta_info(self):
		return self.renderer.presentation.meta_info
