#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

import hashlib
import subprocess
from pybeamer.Tools import HashTools
from pybeamer.RendererCache import BaseRenderer
from pybeamer.Exceptions import UsageException
from pybeamer.CmdlineParser import CmdlineParser, CmdlineParserException

class ExecRenderer(BaseRenderer):
	def __init__(self):
		super().__init__()

	@property
	def name(self):
		return "exec"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def render(self, property_dict):
		cmdline = property_dict["cmdline"]
		cmd = CmdlineParser().parse(cmdline)

		srchash = HashTools.hash_file(cmd[0])

		stdout = b"foo bar"

		result = {
			"cmdline":		cmdline,
			"srchash":		srchash,
			"stdout":		stdout,
		}
		return result

if __name__ == "__main__":
	from pybeamer.RendererCache import RendererCache
	renderer = RendererCache(ExecRenderer())
	print(renderer.render({
		"cmdline":	"/bin/ls -l /",
	}))
