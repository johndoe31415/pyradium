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

from pybeamer.Controller import BaseController
from pybeamer.Exceptions import UsageException
from pybeamer.SVGTransformation import SVGTransformation

class AnimationController(BaseController):
	def render(self):
		filename = self.slide.get_xml_slide_var("filename")
		if filename is None:
			raise UsageException("Any 'animation' type slide requires a variable called 'filename' to be set.")
		if not filename.lower().endswith(".svg"):
			raise UsageException("Any 'animation' type slide requires an SVG input filename, but found: %s" % (filename))

		full_filename = self.rendered_presentation.renderer.lookup_include(filename)

		# Determine the number of layers the SVG has first
		svg = SVGTransformation(full_filename)
		considered_layers = list(svg.visible_layer_ids)

		# Hide them all first
		for layer_id in considered_layers:
			svg.get_layer(layer_id).hide()

		# Then show them one-by-one and render each
		renderer = self.rendered_presentation.renderer.get_custom_renderer("img")
		for layer_id in considered_layers:
			svg.get_layer(layer_id).show()


			print("EMIT")

		yield from [ ]
#		yield from self.slide.emit_slide(self.rendered_presentation, self.content_containers, { "acronyms": page_content })
