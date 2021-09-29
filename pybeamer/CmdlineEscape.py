#!/usr/bin/python3
#
#	CmdlineEscape - Escape a command line so that it can be safely put in a bash script
#	Copyright (C) 2020-2020 Johannes Bauer
#
#	This file is part of pycommon.
#
#	pycommon is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pycommon is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pycommon; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#
#	File UUID df05d56b-c766-41a7-a240-0a8bef0a6064

class CmdlineEscape():
	_ESCAPE_CHARS = set(" \\\"';&*()|")

	def __init__(self, always_exported_env = None):
		self._always_exported_env = set(always_exported_env) if (always_exported_env is not None) else tuple()

	@classmethod
	def _needs_escaping(cls, text):
		for char in text:
			if char in cls._ESCAPE_CHARS:
				return True
		return None

	@classmethod
	def _escape(cls, text):
		if cls._needs_escaping(text):
			return "'%s'" % (text.replace("'", "'\\''"))
		else:
			return text

	def cmdline(self, cmd, env = None):
		if env is None:
			env = { }
		else:
			env = dict(env)
		for varname in self._always_exported_env:
			if (varname in os.environ) and (varname not in env):
				env[varname] = os.environ[varname]

		command = " ".join(self._escape(arg) for arg in cmd)
		if env is None:
			return command
		else:
			env_string = " ".join("%s=%s" % (key, self._escape(value)) for (key, value) in sorted(env.items()))
			return (env_string + " " + command).lstrip()

if __name__ == "__main__":
	cle = CmdlineEscape()
	print(cle.cmdline([ "echo", "hello-there" ]))
	print(cle.cmdline([ "echo", "hello there" ]))
	print(cle.cmdline([ "echo", "hello \" there" ]))
	print(cle.cmdline([ "echo", "hello ' there" ]))
	print(cle.cmdline([ "echo", "hello & there" ]))
	print(cle.cmdline([ "echo", "hello!", "you!" ]))
	print(cle.cmdline([ "echo", "hello!(", "you!" ]))
	print(cle.cmdline([ "echo", "()!&;'\" $foo" ]))
	print(cle.cmdline([ "echo", "\\\\" ]))
	print(cle.cmdline([ "echo", "foo 'bar' moo" ]))
