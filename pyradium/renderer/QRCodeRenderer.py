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

import subprocess
from .BaseRenderer import BaseRenderer

@BaseRenderer.register
class QRCodeRenderer(BaseRenderer):
	_NAME = "qrcode"

	@property
	def properties(self):
		return {
			"version":			1,
		}

	def render(self, property_dict):
		# Render QR-Code to SVG
		cmd = [ "qrencode", "-tsvg", "-m0", property_dict["data"] ]
		svg_data = subprocess.check_output(cmd)

		result = {
			"svg":		svg_data,
		}
		return result
