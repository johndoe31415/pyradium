#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
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
import sys
from .Acrofile import Acrofile
from .BaseAction import BaseAction
from .Tools import FileTools

class ActionAcroTex(BaseAction):
	def run(self):
		if (not self._args.force) and (self._args.tex_outfile != "-") and os.path.exists(self._args.tex_outfile):
			print(f"Refusing to overwrite: {self._args.tex_outfile}", file = sys.stderr)
			return 1

		acrofile = Acrofile.load_from_file(self._args.acrofile)
		with FileTools.open_write_stdout(self._args.tex_outfile) as f:
			print("\\begin{acronym}", file = f)
			if self._args.itemsep is not None:
				print(f"\\itemsep={{{self._args.itemsep}}}", file = f)
			for (acronym_id, acrodata) in sorted(acrofile):
				acronym = acrodata.get("acronym", acronym_id)
				if acronym_id == acronym:
					print(f"\\acro{{{acronym_id}}}{{{acrodata['text']}}}", file = f)
				else:
					print(f"\\acro{{{acronym_id}}}[{acronym}]{{{acrodata['text']}}}", file = f)
			print("\\end{acronym}", file = f)
