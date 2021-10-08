/*
	*	pyradium - HTML presentation/slide show generator
	*	Copyright (C) 2015-2021 Johannes Bauer
	*
	*	This file is part of pyradium.
	*
	*	pyradium is free software; you can redistribute it and/or modify
	*	it under the terms of the GNU General Public License as published by
	*	the Free Software Foundation; this program is ONLY licensed under
	*	version 3 of the License, later versions are explicitly excluded.
	*
	*	pyradium is distributed in the hope that it will be useful,
	*	but WITHOUT ANY WARRANTY; without even the implied warranty of
	*	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	*	GNU General Public License for more details.
	*
	*	You should have received a copy of the GNU General Public License
	*	along with pyradium; if not, write to the Free Software
	*	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
	*
	*	Johannes Bauer <JohannesBauer@gmx.de>
*/

class TimeRange {
	constructor(begin_hour, begin_minute, end_hour, end_minute) {
		this._begin_time = (60 * begin_hour) + begin_minute;
		this._end_time = (60 * end_hour) + end_minute;
		if (this._end_time < this._begin_time) {
			this._end_time += 1440;
		}
	}

	get duration_seconds() {
		return this.duration_minutes * 60;
	}

	get duration_minutes() {
		return this._end_time - this._begin_time;
	}

	get begin_hour() {
		return Math.floor(this._begin_time % 1440 / 60);
	}

	get begin_minute() {
		return Math.floor(this._begin_time % 1440 % 60);
	}

	get end_hour() {
		return Math.floor(this._end_time % 1440 / 60);
	}

	get end_minute() {
		return Math.floor(this._end_time % 1440 % 60);
	}
}

export class TimeTools {
	static parse_timerange(timerange_str) {
		const match = timerange_str.match(/^\s*(?<begin_hour>\d{1,2}):(?<begin_minute>\d{2})\s*-\s*(?<end_hour>\d{1,2}):(?<end_minute>\d{2})\s*$/);
		if (match) {
			const begin_hour = match.groups.begin_hour | 0;
			const begin_minute = match.groups.begin_minute | 0;
			const end_hour = match.groups.end_hour | 0;
			const end_minute = match.groups.end_minute | 0;
			if ((begin_hour < 0) || (begin_hour > 23)) {
				return null;
			}
			if ((begin_minute < 0) || (begin_minute > 59)) {
				return null;
			}
			if ((end_hour < 0) || (end_hour > 23)) {
				return null;
			}
			if ((end_minute < 0) || (end_minute > 59)) {
				return null;
			}
			if ((begin_hour == end_hour) && (begin_minute == end_minute)) {
				return null;
			}
			return new TimeRange(begin_hour, begin_minute, end_hour, end_minute);
		}
		return null;
	}

	static format_hms(total_seconds) {
		if (total_seconds <= -0.5) {
			return "-" + TimeTools.format_hms(-total_seconds);
		}
		total_seconds = Math.round(total_seconds);
		const hours = Math.floor(total_seconds / 3600);
		const minutes = Math.floor(total_seconds % 3600 / 60);
		const seconds = Math.floor(total_seconds % 3600 % 60);
		if (hours == 0) {
			return String(minutes) + ":" + String(seconds).padStart(2, "0");
		} else {
			return String(hours) + ":" + String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");
		}
	}
}
