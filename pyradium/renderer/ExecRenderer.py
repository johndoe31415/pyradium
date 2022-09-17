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

import subprocess
from pyradium.Tools import HashTools
from pyradium.Exceptions import FailedToExecuteSubprocessException
from .BaseRenderer import BaseRenderer

@BaseRenderer.register
class ExecRenderer(BaseRenderer):
	_NAME = "exec"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def rendering_key(self, property_dict):
		cmd = property_dict["cmd"]
		return {
			"srchash":		HashTools.hash_file(cmd[0]),
		}

	def render(self, property_dict):
		cmd = property_dict["cmd"]
		try:
			proc = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, check = True)
		except PermissionError as e:
			raise FailedToExecuteSubprocessException("Could not execute '%s' (%s)." % (str(cmd), str(e))) from e

		if proc.returncode != 0:
			raise FailedToExecuteSubprocessException("Could not execute '%s': returncode %d." % (str(cmd), proc.returncode))

		result = {
			"cmd":			cmd,
			"stdout":		proc.stdout,
			"stderr":		proc.stderr,
		}
		return result

if __name__ == "__main__":
	from pyradium.RendererCache import RendererCache
	renderer = RendererCache(ExecRenderer())
	print(renderer.render({
		"cmd":	[ "/bin/ls", "-l", "/" ],
	}))
