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

import logging
from pyradium.Controller import BaseController
from pyradium.Exceptions import UsageException, MalformedXMLInputException
from pysvgedit import SVGDocument, SVGAnimation, SVGAnimationMode

_log = logging.getLogger(__spec__.name)

def _parse_frame_range(frame_range_str):
	if frame_range_str is None:
		return None
	frames = set()
	try:
		for element in frame_range_str.split(","):
			element = element.split("-")
			if len(element) == 1:
				frames.add(int(element[0]))
			elif len(element) == 2:
				(from_frame, to_frame) = (int(element[0]), int(element[1]))
				frames |= set(range(from_frame, to_frame + 1))
			else:
				raise MalformedXMLInputException("Do not understand how to parse frame range in animation: {element}")
	except ValueError as e:
		raise MalformedXMLInputException("Frame element in animation is not a string: {str(e)}") from e
	return frames

class AnimationController(BaseController):
	def render(self):
		filename = self.slide.get_xml_slide_var("filename")
		if filename is None:
			raise UsageException("Any 'animation' type slide requires a variable called 'filename' to be set.")
		if not filename.lower().endswith(".svg"):
			raise UsageException("Any 'animation' type slide requires an SVG input filename, but found: %s" % (filename))


		animation_mode = self.slide.get_xml_slide_var("mode")
		if animation_mode is None:
			animation_mode = SVGAnimationMode.Compose
		else:
			try:
				animation_mode = SVGAnimationMode(animation_mode)
			except ValueError as e:
				raise UsageException("An 'animation' type slide needs to have a mode set to any of %s, but found: %s" % (", ".join(mode.value for mode in SVGAnimationMode), animation_mode)) from e


		frame_range = _parse_frame_range(self.slide.get_xml_slide_var("range"))
		full_filename = self.rendered_presentation.renderer.lookup_include(filename)

		svg_doc = SVGDocument.readfile(full_filename)
		svg_animation = SVGAnimation(svg_doc, animation_mode = animation_mode)
		renderer = self.rendered_presentation.renderer.get_custom_renderer("img")

		# TODO: we're including all files in the presentation even if we only
		# need the last because we're collapsing the presentation
		additional_slide_var_list = [ ]
		for svg_frame in svg_animation:
			rendered_image = renderer.render({
				"filetype":			"svg",
				"value":			svg_frame.asbytes(),
				"max_dimension":	self.rendered_presentation.renderer.rendering_params.image_max_dimension
			})
			local_filename = f"imgs/anim/{rendered_image.keyhash}.{rendered_image.data['extension']}"
			self.rendered_presentation.add_file(local_filename, rendered_image.data["img_data"])
			additional_slide_var_list.append({
				"image": local_filename,
			})


		if frame_range is not None:
			filtered_slide_var_list = [ ]
			for (frame_no, frame) in enumerate(additional_slide_var_list, 1):
				if frame_no in frame_range:
					filtered_slide_var_list.append(frame)
			additional_slide_var_list = filtered_slide_var_list

		if len(additional_slide_var_list) == 0:
			_log.warning("SVG animation from %s rendered into no slides.", filename)
		else:
			_log.debug("SVG animation from %s rendered into %d slides.", filename, len(additional_slide_var_list))
		if not self.rendered_presentation.renderer.rendering_params.collapse_animation:
			yield from self.slide.emit_nocontent_slide(self.rendered_presentation, self.content_containers, additional_slide_var_list)
		else:
			yield from self.slide.emit_nocontent_slide(self.rendered_presentation, self.content_containers, additional_slide_var_list[-1])
