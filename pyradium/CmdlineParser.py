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

class CmdlineParserException(Exception): pass
class TrailingEscapeCharException(CmdlineParserException): pass
class InvalidEscapeCharException(CmdlineParserException): pass

class CmdlineParser():
	def __init__(self):
		pass

	def parse(self, cmdline):
		cmdline = cmdline.strip(" ")
		args = [ "" ]
		current_escape = None
		i = 0
		while i < len(cmdline):
			char = cmdline[i]
			if char == "\\":
				if i == len(cmdline) - 1:
					raise TrailingEscapeCharException("End of string ends with meta character.")

				i += 1
				nextchar = cmdline[i]
				if nextchar not in [ "\\", "\"", "'", " " ]:
					raise InvalidEscapeCharException("Not a valid character for escaping: %s" % (nextchar))

				args[len(args) - 1] += nextchar
			elif current_escape is None:
				if char == " ":
					if len(args[len(args) - 1]) > 0:
						args.append("")
				elif char == "\"":
					current_escape = "\""
				elif char == "'":
					current_escape = "'"
				else:
					args[len(args) - 1] += char
			elif current_escape == "\"":
				if char == "\"":
					current_escape = None
				else:
					args[len(args) - 1] += char
			elif current_escape == "'":
				if char == "'":
					current_escape = None
				else:
					args[len(args) - 1] += char
			else:
				raise NotImplementedError(current_escape)

			i += 1
		return args
