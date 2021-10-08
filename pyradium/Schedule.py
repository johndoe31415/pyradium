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
from .Exceptions import TimeSpecificationError

class TimeSpecificationType(enum.IntEnum):
	Relative = 0
	Absolute = 1

class TimeSpecification():
	_ABS_REGEX = re.compile(r"((?P<single_value>(\d*\.)?\d+)\s*(?P<unit>min|sec|m|s)|(?P<mins>\d+):(?P<secs>\d+))")
	_REL_REGEX = re.compile(r"(?P<rel_value>(\d*\.)?\d+)")

	def __init__(self, value, spec_type):
		assert(isinstance(spec_type, TimeSpecificationType))
		self._value = value
		self._spec_type = spec_type

	@property
	def value(self):
		return self._value

	@property
	def spec_type(self):
		return self._spec_type

	@classmethod
	def parse(cls, abs_string = None, rel_string = None):
		if (abs_string is None) and (rel_string is None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied.")
		if (abs_string is not None) and (rel_string is not None):
			raise TimeSpecificationError("Either absolute or relative timing must be supplied, not both.")

		if abs_string is not None:
			match = cls._ABS_REGEX.fullmatch(abs_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for absolute timespecification: \"%s\"" % (abs_string))
			match = match.groupdict()
			if match["unit"] in [ "min", "m" ]:
				value = float(match["single_value"]) * 60
			elif match["unit"] in [ "sec", "s" ]:
				value = float(match["single_value"])
			elif match["unit"] is None:
				value = (60 * int(match["mins"])) + int(match["secs"])
			else:
				raise NotImplementedError(match["unit"])
			return cls(spec_type = TimeSpecificationType.Absolute, value = value)
		else:
			match = cls._REL_REGEX.fullmatch(rel_string)
			if match is None:
				raise TimeSpecificationError("Invalid string for relative timespecification: \"%s\"" % (rel_string))
			match = match.groupdict()
			return cls(spec_type = TimeSpecificationType.Relative, value = float(match["rel_value"]))

	def __str__(self):
		return "TimeSpecification<%s, %.0f>" % (self.spec_type.name, self.value)

class TimeRange():
	_TIME_RE = re.compile(r"\s*(?P<begin_hrs>\d+):(?P<begin_mins>\d{2})\s*-\s*(?P<end_hrs>\d+):(?P<end_mins>\d{2})\s*")
	def __init__(self, range_begin, range_end):
		self._range_begin = range_begin
		self._range_end = range_end

	@property
	def range_begin(self):
		return self._range_begin

	@property
	def range_end(self):
		return self._range_end

	@property
	def begin_time(self):
		return divmod(self.range_begin % 1440, 60)

	@property
	def end_time(self):
		return divmod(self.range_end % 1440, 60)

	@property
	def duration_mins(self):
		return self.range_end - self.range_begin

	@classmethod
	def parse(cls, text):
		match = cls._TIME_RE.fullmatch(text)
		if match is None:
			raise TimeSpecificationError("Invalid time range: \"%s\"" % (text))
		match = match.groupdict()
		match = { key: int(value) for (key, value) in match.items() }
		if not (0 <= match["begin_hrs"] <= 23):
			raise TimeSpecificationError("Invalid time range: \"%s\"; begin hours must be in range 0..23" % (text))
		if not (0 <= match["end_hrs"] <= 23):
			raise TimeSpecificationError("Invalid time range: \"%s\"; end hours must be in range 0..23" % (text))
		if not (0 <= match["begin_mins"] <= 59):
			raise TimeSpecificationError("Invalid time range: \"%s\"; begin minutes must be in range 0..59" % (text))
		if not (0 <= match["end_mins"] <= 59):
			raise TimeSpecificationError("Invalid time range: \"%s\"; end minutes must be in range 0..59" % (text))

		range_begin = (int(match["begin_hrs"]) * 60) + int(match["begin_mins"])
		range_end = (int(match["end_hrs"]) * 60) + int(match["end_mins"])
		if range_end < range_begin:
			range_end += 1440
		return cls(range_begin = range_begin, range_end = range_end)

	def __str__(self):
		return "%d:%02d-%d:%02d" % (self.begin_time[0], self.begin_time[1], self.end_time[0], self.end_time[1])

class TimeRanges():
	_SPLITTER_RE = re.compile(r"\s+")

	def __init__(self, time_ranges):
		assert(all(isinstance(time_range, TimeRange) for time_range in time_ranges))
		self._time_ranges = tuple(time_ranges)

	@classmethod
	def parse(cls, text):
		return cls(tuple(TimeRange.parse(text_value) for text_value in cls._SPLITTER_RE.split(text)))

	@property
	def duration_mins(self):
		return sum(time_range.duration_mins for time_range in self)

	def __iter__(self):
		return iter(self._time_ranges)

	def __str__(self):
		return " ".join(str(time_range) for time_range in self)

class PresentationSchedule():
	_TimeSlice = collections.namedtuple("TimeSlice", [ "slide_no", "slide_ratio", "begin_ratio", "end_ratio", "time_seconds" ])

	def __init__(self, active_presentation_time_minutes):
		if active_presentation_time_minutes is not None:
			self._active_presentation_time_seconds = 60 * active_presentation_time_minutes
		else:
			self._active_presentation_time_seconds = None
		self._time_specs = { }
		self._timeslices = None
		self._max_slide_no = 0

	def have_slide(self, slide_no):
		self._max_slide_no = max(self._max_slide_no, slide_no)

	def set_slide_no(self, slide_no, time_spec):
		assert(isinstance(time_spec, TimeSpecification))
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
						abs_sum_secs += time_spec.value
					elif time_spec.spec_type == TimeSpecificationType.Relative:
						rel_sum_pts += time_spec.value
					else:
						raise NotImplementedError(time_spec.spec_type)
				else:
					rel_sum_pts += 1

			if (abs_sum_secs > 0) and (self._active_presentation_time_seconds is None):
				raise TimeSpecificationError("You are free to not define a presentation length beforehand, but then absolute time references may not be used.")

			if self._active_presentation_time_seconds is not None:
				active_rel_time_secs = self._active_presentation_time_seconds - abs_sum_secs
				if active_rel_time_secs < 0:
					raise TimeSpecificationError("Presentation active time is %.0f seconds, but %.0f seconds already allocated for absolute slides." % (self._active_presentation_time_seconds, abs_sum_secs))
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
						slide_time_secs = time_spec.value
					elif time_spec.spec_type == TimeSpecificationType.Relative:
						slide_time_secs = time_spec.value / rel_sum_pts * active_rel_time_secs
				else:
					slide_time_secs = 1 / rel_sum_pts * active_rel_time_secs

				if self._active_presentation_time_seconds is not None:
					slide_ratio = slide_time_secs / self._active_presentation_time_seconds
				else:
					slide_ratio = slide_time_secs
				timeslice = self._TimeSlice(slide_no = slide_no, slide_ratio = slide_ratio, begin_ratio = current_slide_ratio, end_ratio = current_slide_ratio + slide_ratio, time_seconds = slide_time_secs)
				current_slide_ratio += slide_ratio
				timeslices[slide_no] = timeslice

			self._timeslices = timeslices
		return self._timeslices

	def __getitem__(self, slide_no):
		if self._timeslices is None:
			return self._TimeSlice(slide_no = slide_no, slide_ratio = 1, begin_ratio = 0, end_ratio = 1, time_seconds = 1)
		else:
			return self._timeslices[slide_no]

	def __iter__(self):
		return iter(self._timeslices.values())
