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
	"img": """<s:img src="X" />""",

	"anim": """
	<slide type="animation">
		<s:var name="heading" value="X" />
		<s:var name="filename" value="X.svg" />
	</slide>
	""",

	"code": """
		<s:code lang="X"><![CDATA[
		]]></s:code>
	""",

	"term": """
		<s:term prompt="$ "><![CDATA[
		]]></s:term>
	""",

	"sectiontitle": """
	<slide type="sectiontitle">
		<s:time abs="10 sec" />
	</slide>
	""",

	"quote": """
	<slide type="quote">
        X
		<s:var name="author" value="X" />
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
