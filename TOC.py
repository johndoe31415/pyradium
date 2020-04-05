#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2015-2020 Johannes Bauer
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

class TOCError(Exception): pass

class TOC():
	def __init__(self):
		self._section = None
		self._subsection = None
		self._toc = [ ]

	@property
	def section(self):
		return self._section

	@section.setter
	def section(self, value):
		self._section = value
		self._toc.append((self._section, [ ]))

	@property
	def subsection(self):
		return self._subsection

	@subsection.setter
	def subsection(self, value):
		self._subsection = value
		if len(self._toc) == 0:
			raise TOCError("Cannot have subsection '%s' without a section." % (value))
		self._toc[-1][-1].append(self._subsection)
