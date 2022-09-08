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

import logging
import subprocess

logging.TRACE = logging.DEBUG - 1
logging.SINGLESTEP = logging.DEBUG - 2
logging.addLevelName(logging.TRACE, "TRACE")
logging.addLevelName(logging.SINGLESTEP, "SINGLESTEP")

class CustomLogger(logging.Logger):
	@property
	def subproc_target(self):
		if self.isEnabledFor(logging.TRACE):
			return None
		else:
			return subprocess.DEVNULL

	def trace(self, msg, *args, **kwargs):
		if self.isEnabledFor(logging.TRACE):
			self._log(logging.TRACE, msg, args, **kwargs)

	def singlestep(self, msg, *args, **kwargs):
		if self.isEnabledFor(logging.SINGLESTEP):
			self._log(logging.SINGLESTEP, msg, args, **kwargs)

	@classmethod
	def set_logging_by_verbosity(cls, verbosity):
		if verbosity == 0:
			loglevel = logging.WARN
		elif verbosity == 1:
			loglevel = logging.INFO
		elif verbosity == 2:
			loglevel = logging.DEBUG
		elif verbosity == 3:
			loglevel = logging.TRACE
		else:
			loglevel = logging.SINGLESTEP
		logging.basicConfig(format = "{name:>30s} [{levelname:.1s}]: {message}", style = "{", level = loglevel)

logging.setLoggerClass(CustomLogger)
