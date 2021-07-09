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

import sys
from .MultiCommand import MultiCommand
from .ActionRender import ActionRender

def main():
	mc = MultiCommand()

	def genparser(parser):
		parser.add_argument("-f", "--force", action = "store_true", help = "Overwrite files in destination directory if they already exist.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified more than once.")
		parser.add_argument("infile", help = "Input XML file of the slide show.")
		parser.add_argument("outdir", help = "Output directory the presentation is put into.")
	mc.register("render", "Render a slide show", genparser, action = ActionRender)

	mc.run(sys.argv[1:])


if __name__ == "__main__":
	main()
