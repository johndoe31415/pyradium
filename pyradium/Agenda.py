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

import re
import collections
from pyradium.Exceptions import IllegalAgendaSyntaxException, UndefinedAgendaTimeException, UnresolvableWeightedEntryException, AgendaTimeMismatchException

AgendaItem = collections.namedtuple("AgendaItem", [ "start_time", "end_time", "duration", "text" ])
_UnresolvedAgendaItem = collections.namedtuple("UnresolvedAgendaItem", [ "spec_type", "value", "text", "markers" ])

class Agenda():
	_AGENDA_REGEX = re.compile(r"((?P<relative>\+)?((?P<day>\d+)\+)?(?P<hour>\d{1,2}):(?P<minute>\d{1,2})(/(?P<divider>\d+(\.\d+)?))?|(?P<wildcard>\*)(?P<weight>\d+(\.\d+)?)?)(\s+(?P<text>.*))?|:(?P<marker>.+)")

	def __init__(self, agenda_items: list[AgendaItem], markers: collections.OrderedDict, name: str | None = None):
		self._agenda_items = agenda_items
		self._markers = markers
		self._name = name

	@property
	def name(self):
		return self._name

	@property
	def markers(self):
		return iter(self._markers.items())

	def dump(self):
		print(f"Agenda with {len(self)} items:")
		for item in self:
			print(f"    {item}")

	def __len__(self):
		return len(self._agenda_items)

	def __getitem__(self, index):
		return self._agenda_items[index]

	@classmethod
	def _hmstr(cls, minutes):
		minutes = round(minutes) % (24 * 60)
		return f"{minutes // 60}:{minutes % 60:02d}"

	@classmethod
	def _roundto(cls, value, boundary):
		return round(value / boundary) * boundary

	@classmethod
	def _resolve_relative_references(cls, unresolved_agenda, reverse = False):
		if len(unresolved_agenda) == 0:
			return [ ]

		now = None
		resolved_items = [ ]
		unresolved_agenda = unresolved_agenda if (not reverse) else reversed(unresolved_agenda)

		for item in unresolved_agenda:
			if item.spec_type == "abs":
				now = item.value
				resolved_items.append(item)
			elif (item.spec_type == "rel") and (now is not None):
				if not reverse:
					now += item.value
				resolved_item = _UnresolvedAgendaItem(spec_type = "abs", value = now, text = item.text, markers = item.markers)
				if reverse:
					now -= item.value
				resolved_items.append(resolved_item)
			else:
				now = None
				resolved_items.append(item)

		if reverse and (now is not None):
			resolved_item = _UnresolvedAgendaItem(spec_type = "abs", value = now, text = None, markers = [ ])
			resolved_items.append(resolved_item)

		if reverse:
			resolved_items.reverse()
		return resolved_items

	@classmethod
	def _resolve_forward_relative_references(cls, unresolved_agenda: list[_UnresolvedAgendaItem]):
		return cls._resolve_relative_references(unresolved_agenda)

	@classmethod
	def _resolve_backward_relative_references(cls, unresolved_agenda: list[_UnresolvedAgendaItem]):
		return cls._resolve_relative_references(unresolved_agenda, reverse = True)

	@classmethod
	def _resolve_all_relative_references(cls, unresolved_agenda: list[_UnresolvedAgendaItem]):
		unresolved_agenda = cls._resolve_forward_relative_references(unresolved_agenda)
		unresolved_agenda = cls._resolve_backward_relative_references(unresolved_agenda)
		return unresolved_agenda

	@classmethod
	def _resolve_enclosed_weighted_references(cls, enclosed_agenda: list[_UnresolvedAgendaItem]):
		assert(len(enclosed_agenda) >= 3)
		assert(enclosed_agenda[0].spec_type == "abs")
		assert(enclosed_agenda[-1].spec_type == "abs")
		resolved_items = [ ]
		total_time = enclosed_agenda[-1].value - enclosed_agenda[0].value
		relative_time = 0
		weight_sum = 0
		for item in enclosed_agenda:
			if item.spec_type == "rel":
				relative_time += item.value
			elif item.spec_type == "weight":
				weight_sum += item.value
		if weight_sum == 0:
			raise UnresolvableWeightedEntryException("Sum of weights is zero.")
		if relative_time > total_time:
			raise UnresolvableWeightedEntryException(f"Unresolvable weighted exception: relative time within enclosed absolute time bracket too long relative {cls._hmstr(relative_time)} but total time only {cls._hmstr(total_time)}")

		weighted_time = total_time - relative_time
		now = enclosed_agenda[0].value
		for item in enclosed_agenda[1 : -1]:
			if item.spec_type == "abs":
				pass
			elif item.spec_type == "rel":
				now += item.value
				item = _UnresolvedAgendaItem(spec_type = "abs", value = now, text = item.text, markers = item.markers)
			elif item.spec_type == "weight":
				now += (item.value / weight_sum) * weighted_time
				item = _UnresolvedAgendaItem(spec_type = "abs", value = now, text = item.text, markers = item.markers)
			resolved_items.append(item)
		return resolved_items

	@classmethod
	def _resolve_weighted_references(cls, unresolved_agenda: list[_UnresolvedAgendaItem]):
		resolved_items = [ ]

		index = 0
		while index < len(unresolved_agenda):
			item = unresolved_agenda[index]
			if item.spec_type == "weight":
				if index == 0:
					raise UnresolvableWeightedEntryException("Unresolvable weighted exception: May not have a weighted relative item at the beginning")
				enclosed = [ unresolved_agenda[index - 1], item ]

				index += 1
				while index < len(unresolved_agenda):
					item = unresolved_agenda[index]
					enclosed.append(item)
					if item.spec_type == "abs":
						break
					index += 1

				if enclosed[-1].spec_type != "abs":
					raise UnresolvableWeightedEntryException("Unresolvable weighted exception: May not have a weighted relative item at the end")
				resolved_items += cls._resolve_enclosed_weighted_references(enclosed)
			else:
				resolved_items.append(item)
				index += 1
		return resolved_items

	@classmethod
	def _resolve(cls, unresolved_agenda: list[_UnresolvedAgendaItem], granularity_minutes: int):
		unresolved_agenda = cls._resolve_all_relative_references(unresolved_agenda)
		unresolved_agenda = cls._resolve_weighted_references(unresolved_agenda)

		resolved_agenda_items = [ ]
		markers = collections.OrderedDict()
		prev_item = None
		for item in unresolved_agenda:
			if (prev_item is not None) and (item.value is not None) and (prev_item.value is not None) and (item.value < prev_item.value):
				raise AgendaTimeMismatchException(f"Time cannot move backwards: Previously at {cls._hmstr(prev_item.value)}, but requested moving back to {cls._hmstr(item.value)} (from {prev_item} to {item})")
			if item.text is not None:
				if (prev_item is None) or (prev_item.value is None):
					raise UndefinedAgendaTimeException(f"Unable to determine start time of event: {item}")

				start = cls._roundto(prev_item.value, granularity_minutes)
				end = cls._roundto(item.value, granularity_minutes)
				duration = end - start
				agenda_item = AgendaItem(start_time = cls._hmstr(start), end_time = cls._hmstr(end), duration = cls._hmstr(duration), text = item.text)
				resolved_agenda_items.append(agenda_item)
			for marker in item.markers:
				ts = cls._roundto(item.value, granularity_minutes)
				markers[marker] = cls._hmstr(ts)
			prev_item = item
		return (resolved_agenda_items, markers)

	@classmethod
	def parse(cls, text: str, name: str | None = None, granularity_minutes: int = 5):
		now = None

		unresolved_items = [ ]
		day = 0
		for line in text.split("\n"):
			line = line.strip()
			if line == "":
				continue

			rematch = cls._AGENDA_REGEX.fullmatch(line)
			if rematch is None:
				raise IllegalAgendaSyntaxException(f"Do not understand agenda element: {line}")

			rematch = rematch.groupdict()
			if rematch["hour"] is not None:
				if rematch["day"] is not None:
					day = int(rematch["day"])
				time_value = (int(rematch["hour"]) * 60) + int(rematch["minute"]) + (1440 * day)
				relative = rematch["relative"] is not None
				if rematch["divider"] is not None:
					if not relative:
						raise IllegalAgendaSyntaxException(f"Specifying a divider for an absolute time element does not make sense: {line}")
					divider = float(rematch["divider"])
					time_value /= divider
				timespec = ("rel" if relative else "abs", time_value)
			elif rematch["wildcard"] is not None:
				if rematch["weight"] is not None:
					weight = float(rematch["weight"])
				else:
					weight = 1
				timespec = ("weight", weight)
			elif rematch["marker"] is not None:
				if len(unresolved_items) == 0:
					raise IllegalAgendaSyntaxException(f"Cannot have a marker as the first element: {line}")
				last_item = unresolved_items[-1]
				last_item.markers.append(rematch["marker"])
				continue

			unresolved_item = _UnresolvedAgendaItem(spec_type = timespec[0], value = timespec[1], text = rematch["text"], markers = [ ])
			unresolved_items.append(unresolved_item)
		(agenda_items, markers) = cls._resolve(unresolved_items, granularity_minutes = granularity_minutes)
		return cls(agenda_items = agenda_items, markers = markers, name = name)
