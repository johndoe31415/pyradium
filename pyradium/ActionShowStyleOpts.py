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

import json
import logging
from .BaseAction import BaseAction
from .RenderingParameters import RenderingParameters
from .StyleParameters import StyleParameters

_log = logging.getLogger(__spec__.name)

class ActionShowStyleOpts(BaseAction):
	def run(self):
		rendering_parameters = RenderingParameters(
			template_style = self._args.template_style,
			extra_template_dirs = self._args.template_dir,
		)
		config_filename = rendering_parameters.template_dirs.lookup(rendering_parameters.template_style + "/configuration.json")
		_log.debug("Using configuration: %s", config_filename)
		with open(config_filename) as f:
			config = json.load(f)

		if "parameters" not in config:
			print("Template has no parameters.")
		else:
			parameters = StyleParameters(config["parameters"])
			parameters.print()
