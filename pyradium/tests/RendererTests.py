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

import unittest
from pyradium.renderer import BaseRenderer

class RendererTests(unittest.TestCase):
	def test_dtg1(self):
		renderer = BaseRenderer.instanciate("dtg")
		renderer.render({
			"data": """
				C  = 00000|1111100000|1111100000|11111000
				D  = 11111 1100000000 0001010111 00000000
				Q  = 00000 1111111111 0000000000 11111111
					!Q = 11111 0000000000 1111111111 00000000
			""",
			"xdiv": 10,
			"height": 30,
			"vertical_distance": 10,
			"marker_extend": 20,
			"clock_ticks": True,
		})
