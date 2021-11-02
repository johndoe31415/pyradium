#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

import re
import enum
import collections
import logging
from .Exceptions import TimeSpecificationError

_log = logging.getLogger(__spec__.name)

class TimeSpecificationType(enum.IntEnum):
	Relative = 0
	Absolute = 1

class TimeSpecification():
	_ABS_REGEX = re.compile(r"("
							+ r"(?P<single_value>(\d*\.)?\d+)\s*(?P<unit>hrs?|mins?|secs?|h|m|s)"
							+ r"|(?P<hrs>\d+):(?P<mins>\d+):(?P<secs>\d+)"
							+ r"|(?P<val1>\d+):(?P<val2>\d+)\s*(?P<valunit>h:?m|m:?s)?"
							+ r")")
	_REL_REGEX = re.compile(r"(?P<rel_value>(\d*\.)?\d+)")

	def __init__(self, value, spec_type):
		assert(isinstance(spec_type, TimeSpecificationType))
		self._value = value
		self._spec_type = spec_type

	@property
	def relvalue(self):
		assert(self.spec_type == TimeSpecificationType.Relative)
		return self._value

	@property
	def duration_secs(self):
		assert(self.spec_type == TimeSpecificationType.Absolute)
		return self._value

	@property
	def duration_mins(self):
		assert(self.spec_type == TimeSpecificationType.Absolute)
		return self._value / 60

	@property
	def spec_type(self):
		return self._spec_type

	@classmethod
	def parse(cls, abs_string = None, rel_string = None, default_abs_interpretation = None):
		if (abs_string is None) and (rel_string is None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied.")
		if (abs_string is not None) and (rel_string is not None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied, not both.")

		if abs_string is not None:
			match = cls._ABS_REGEX.fullmatch(abs_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for absolute timespecification: \"%s\"" % (abs_string))
			match = match.groupdict()
			if match["unit"] is not None:
				# A unit was supplied
				if match["unit"] in [ "hr", "hrs", "h" ]:
					value = float(match["single_value"]) * 3600
				elif match["unit"] in [ "min", "mins", "m" ]:
					value = float(match["single_value"]) * 60
				elif match["unit"] in [ "sec", "secs", "s" ]:
					value = float(match["single_value"])
				else:
					raise NotImplementedError(match["unit"])
			elif match["hrs"] is not None:
				value = (3600 * int(match["hrs"])) + (60 * int(match["mins"])) + int(match["secs"])
			else:
				# xx:yy format, need to infer the correct unit (hrs:mins or
				# mins:secs)
				given_format = match["valunit"] or default_abs_interpretation
				if given_format is None:
					raise TimeSpecificationError("For the given timespec '%s' of format xx:yy it is impossible to tell wether hrs:mins or mins:secs is meant and no default value is available. Please specify." % (abs_string))
				if given_format in [ "h:m", "hm" ]:
					value = (3600 * int(match["val1"])) + (60 * int(match["val2"]))
				elif given_format in [ "m:s", "ms" ]:
					value = (60 * int(match["val1"])) + int(match["val2"])
				else:
					raise NotImplementedError(given_format)
			return cls(spec_type = TimeSpecificationType.Absolute, value = value)
		else:
			match = cls._REL_REGEX.fullmatch(rel_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for relative timespecification: \"%s\"" % (rel_string))
			match = match.groupdict()
			return cls(spec_type = TimeSpecificationType.Relative, value = float(match["rel_value"]))

	def __str__(self):
		if self.spec_type == TimeSpecificationType.Relative:
			return "TimeSpecification<%s, %.1f>" % (self.spec_type.name, self.relvalue)
		elif self.spec_type == TimeSpecificationType.Absolute:
			return "TimeSpecification<%s, %.0f sec>" % (self.spec_type.name, self.duration_secs)
		else:
			return "TimeSpecification<%s>" % (self.spec_type.name)

class PresentationSchedule():
	_TimeSlice = collections.namedtuple("TimeSlice", [ "slide_no", "slide_ratio", "begin_ratio", "end_ratio", "time_seconds" ])

	def __init__(self, presentation_time_seconds = None):
		self._presentation_time_seconds = presentation_time_seconds
		self._time_specs = { }
		self._timeslices = None
		self._max_slide_no = 0

	def have_slide(self, slide_no):
		self._max_slide_no = max(self._max_slide_no, slide_no)

	def set_slide_no(self, slide_no, time_spec):
		if self._timeslices is not None:
			# Already computed, disregards
			return

		assert(isinstance(time_spec, TimeSpecification))
		_log.trace("Setting slide timing of %d to %s", slide_no, str(time_spec))
		self._time_specs[slide_no] = time_spec
		self._max_slide_no = max(self._max_slide_no, slide_no)

	def _slide_range(self):
		return range(1, self._max_slide_no + 1)

	def _slide_no_timespec(self):
		for slide_no in self._slide_range():
			yield (slide_no, self._time_specs.get(slide_no))

	def compute(self):
		if self._timeslices is None:
			abs_sum_secs = 0
			rel_sum_pts = 0
			for (slide_no, time_spec) in self._slide_no_timespec():
				if time_spec is not None:
					if time_spec.spec_type == TimeSpecificationType.Absolute:
						abs_sum_secs += time_spec.duration_secs
					elif time_spec.spec_type == TimeSpecificationType.Relative:
						rel_sum_pts += time_spec.relvalue
					else:
						raise NotImplementedError(time_spec.spec_type)
				else:
					rel_sum_pts += 1

			if (abs_sum_secs > 0) and (self._presentation_time_seconds is None):
				raise TimeSpecificationError("You are free to not define a presentation length beforehand, but then absolute time references may not be used.")

			if self._presentation_time_seconds is not None:
				active_rel_time_secs = self._presentation_time_seconds - abs_sum_secs
				if active_rel_time_secs < 0:
					raise TimeSpecificationError("Presentation active time is %.0f seconds, but %.0f seconds already allocated for absolute slides." % (self._presentation_time_seconds, abs_sum_secs))
			else:
				# Doesn't matter at all, we're only dealing with relative references
				active_rel_time_secs = 1

			if rel_sum_pts == 0:
				# If they are in sum 0, it does not matter anyways, all the
				# numerators will be zero and this way we save two if-elses to
				# avoid divide-by-zero
				rel_sum_pts += 1

			timeslices = { }
			current_slide_ratio = 0
			for (slide_no, time_spec) in self._slide_no_timespec():
				if time_spec is not None:
					if time_spec.spec_type == TimeSpecificationType.Absolute:
						slide_time_secs = time_spec.duration_secs
					elif time_spec.spec_type == TimeSpecificationType.Relative:
						slide_time_secs = time_spec.relvalue / rel_sum_pts * active_rel_time_secs
				else:
					slide_time_secs = 1 / rel_sum_pts * active_rel_time_secs

				if self._presentation_time_seconds is not None:
					slide_ratio = slide_time_secs / self._presentation_time_seconds
				else:
					slide_ratio = slide_time_secs
				timeslice = self._TimeSlice(slide_no = slide_no, slide_ratio = slide_ratio, begin_ratio = current_slide_ratio, end_ratio = current_slide_ratio + slide_ratio, time_seconds = slide_time_secs)
				current_slide_ratio += slide_ratio
				timeslices[slide_no] = timeslice

			self._timeslices = timeslices
		if _log.isEnabledFor(logging.TRACE):
			self.dump()
		return self._timeslices

	def dump(self):
		_log.trace("Dumping %d timeslices determined from presentation schedule:", len(self._timeslices))
		sum_ratios = 0
		sum_duration = 0
		for (slide_no, timeslice) in sorted(self._timeslices.items()):
			sum_ratios += timeslice.slide_ratio
			sum_duration += timeslice.time_seconds
			_log.trace("Slide %2d: ratio %.4f  from %.4f  to %.4f  duration %.0f secs", timeslice.slide_no, timeslice.slide_ratio, timeslice.begin_ratio, timeslice.end_ratio, timeslice.time_seconds)
		_log.trace("Schedule sum of ratios %.3f (should be 1), sum of time %.0f secs", sum_ratios, sum_duration)

	@property
	def slide_ratio_list(self):
		if self._timeslices is None:
			return [ ]
		else:
			return [ timeslice.slide_ratio for (slide_no, timeslice) in sorted(self._timeslices.items()) ]

	def __getitem__(self, slide_no):
		if self._timeslices is None:
			return self._TimeSlice(slide_no = slide_no, slide_ratio = 1, begin_ratio = 0, end_ratio = 1, time_seconds = 1)
		else:
			return self._timeslices[slide_no]

	def __iter__(self):
		return iter(self._timeslices.values())
