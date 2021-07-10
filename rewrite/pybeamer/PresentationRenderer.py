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

from .RendererCache import RendererCache
from .TOC import TOC
from pybeamer.renderer.LatexFormulaRenderer import LatexFormulaRenderer
import mako.lookup

class RenderedPresentation():
	def __init__(self):
		self._rendered_slides = [ ]
		self._css = set()

	@property
	def rendered_slides(self):
		return iter(self._rendered_slides)

	@property
	def css(self):
		return iter(self._css)

	def append_slide(self, rendered_slide):
		self._rendered_slides.append(rendered_slide)

	def require_css(self, css_filename):
		self._css.add(css_filename)

class PresentationRenderer():
	def __init__(self, presentation, rendering_params):
		self._rendered_slides = [ ]
		self._presentation = presentation
		self._rendering_params = rendering_params
		self._custom_renderers = {
			"latex":	RendererCache(LatexFormulaRenderer()),
		}
		self._toc = TOC()
		self._lookup = mako.lookup.TemplateLookup([ "pybeamer/templates", "pybeamer/templates/default" ], strict_undefined = True, input_encoding = "utf-8")

	@property
	def rendering_params(self):
		return self._rendering_params

	@property
	def toc(self):
		return self._toc

	def _render_directive(self, directive):
		return directive.render(self)

	def render(self):
		renderable_slides = [ ]
		for directive in self._presentation:
			generator = self._render_directive(directive)
			if generator is not None:
				renderable_slides += generator

		rendered_presentation = RenderedPresentation()
		for renderable_slide in renderable_slides:
			args = {
				"slide":			renderable_slide,
				"require_css":		rendered_presentation.require_css,
				"presentation":		self._presentation,
			}
			template = self._lookup.get_template("slide_%s.html" % (renderable_slide.slide_type))
			result = template.render(**args)
			rendered_presentation.append_slide(result)

		master_template = self._lookup.get_template("base/master.html")
		args = {
			"rendered_presentation":	rendered_presentation,
			"presentation":				self._presentation,
		}
		result = master_template.render(**args)
		print(result)
