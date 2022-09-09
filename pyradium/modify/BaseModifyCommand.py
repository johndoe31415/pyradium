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

import sys
import logging
from pyradium.FriendlyArgumentParser import FriendlyArgumentParser

class BaseModifyCommand():
	_SUBCOMMANDS = { }
	_NAME = None
	_DESCRIPTION = None
	_VISIBLE = True

	def __init__(self, args):
		self._args = args

	@classmethod
	def get_supported_cmd_list(cls):
		return cls._SUBCOMMANDS.keys()

	@classmethod
	def get_handler(cls, name):
		return cls._SUBCOMMANDS[name]

	@classmethod
	def register(cls, handler):
		if not handler._VISIBLE:
			return
		name = handler._NAME
		if name is None:
			raise ValueError("Handler name not set in child class.")
		if handler._DESCRIPTION is None:
			raise ValueError("Handler description not set in child class.")

		cls._SUBCOMMANDS[handler._NAME] = handler

	@classmethod
	def _gen_parser(cls, parser):
		raise NotImplementedError("_gen_parser")

	@classmethod
	def parse(cls, arguments):
		parser = FriendlyArgumentParser(description = cls._DESCRIPTION, prog = f"{sys.argv[0]} {cls._NAME}", add_help = False)
		cls._gen_parser(parser)
		parsed_args = parser.parse_args(arguments)
		logging.getLoggerClass().set_logging_by_verbosity(parsed_args.verbose)
		return parsed_args
