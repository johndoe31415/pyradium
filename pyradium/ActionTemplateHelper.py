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

from .BaseAction import BaseAction

_KNOWN_TEMPLATES = {
	"slide_title": """
	<slide type="title"/>
	""",

	"slide_toc": """
	<slide type="toc"/>
	""",

	"slide_sectiontitle": """
	<slide type="sectiontitle">
		<s:time abs="10 sec" />
	</slide>
	""",

	"slide_leftright": """
	<slide type="leftright">
	<s:var name="heading" value="" />
		<s:content name="left">
			Left
		</s:content>
		<s:content name="right">
			Right
		</s:content>
	</slide>
	""",

	"slide_quote": """
	<slide type="quote">
		<s:time abs="15 sec"/>
		Quote
		<s:var name="author" value="Author"/>
	</slide>
	""",

	"slide_final": """
	<slide type="final">
		<s:time rel="0" />
	</slide>
	""",

	"slide_acronyms": """
	<slide type="acronyms">
		<s:time rel="0" />
	</slide>
	""",

	"slide_feedback": """
	<slide type="feedback">
		<s:time rel="0" />
		<s:var name="endpoint" value="https://my_server.com/feedback/submit" />
	</slide>
	""",

	"textblock_code": """
		<s:code lang="X"><![CDATA[
		]]></s:code>
	""",

	"textblock_term": """
		<s:term prompt="$ "><![CDATA[
		]]></s:term>
	""",


	"image_img": """<s:img src="X" />""",
	"image_anim": """
	<slide type="animation">
		<s:var name="heading" value="X" />
		<s:var name="filename" value="X.svg" />
	</slide>
	""",
	"image_plot": """<s:plot src="X" />""",
	"image_graphviz": """<s:graphviz src="X" />""",

	"other_circuitjs": """
	<slide>
		<s:var name="heading" value="Title"/>
		<s:circuit>
			<s:param name="name" value="X"/>
			<s:param name="content" value="image"/>
			<s:param name="src" value="*"/>
		</s:circuit>
	</slide>
	""",
}

class ActionTemplateHelper(BaseAction):
	def run(self):
		if self._args.template_name not in _KNOWN_TEMPLATES:
			raise Exception("No such template: %s (must be one of %s)" % (self._args.template_name, ", ".join(sorted(_KNOWN_TEMPLATES))))
		text = _KNOWN_TEMPLATES[self._args.template_name]
		text = text.lstrip("\n").rstrip("\r\n\t ")
		print(text)
