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

const TimestampMode = {
	ABSOLUTE: 0,
	RELATIVE_NOW: 1,
	RELATIVE_PRESENTATION_LENGTH: 2,
};

class Timestamp {
	constructor(ts_type, ts_value) {
		this._ts_type = ts_type;
		this._ts_value = ts_value;
		this._timestamp = null;
	}

	compute(presentation_duration_seconds) {
		if (this._ts_type == TimestampMode.ABSOLUTE) {
			return this._ts_value;
		} else if (this._ts_type == TimestampMode.RELATIVE_NOW) {
			const now = new Date();
			return new Date(now.getTime() + (this._ts_value * 1000));
		} else if (this._ts_type == TimestampMode.RELATIVE_PRESENTATION_LENGTH) {
			const now = new Date();
			return new Date(now.getTime() + (this._ts_value * presentation_duration_seconds * 1000));
		} else {
			console.log("Invalid TS type:", this._ts_type);
		}
	}
}

export class TimeTools {
	static parse_hh_mm(hh_mm_str) {
		const match = hh_mm_str.match(/^\s*(?<timestamp_hour>\d{1,2}):(?<timestamp_minute>\d{2})\s*$/);
		if (match) {
			const timestamp_hour = match.groups.timestamp_hour | 0;
			const timestamp_minute = match.groups.timestamp_minute | 0;
			if ((timestamp_hour < 0) || (timestamp_hour > 23)) {
				return null;
			}
			if ((timestamp_minute < 0) || (timestamp_minute > 59)) {
				return null;
			}
			return timestamp_hour * 60 + timestamp_minute;
		}
		return null;
	}

	static parse_timestamp(timestamp_str) {
		/* Absolute timestamp given day, hour, minute */
		{
			const now = new Date();
			const match = timestamp_str.match(/^\s*((?<timestamp_day>\d{1,2})-)?\s*(?<timestamp_hour>\d{1,2}):(?<timestamp_minute>\d{2})\s*$/);
			if (match) {
				const timestamp_hour = match.groups.timestamp_hour | 0;
				const timestamp_minute = match.groups.timestamp_minute | 0;
				const timestamp_day = (match.groups.timestamp_day == null) ? now.getDate() : (match.groups.timestamp_day | 0);
				if ((timestamp_hour < 0) || (timestamp_hour > 23)) {
					return null;
				}
				if ((timestamp_minute < 0) || (timestamp_minute > 59)) {
					return null;
				}
				if ((timestamp_day != null) && ((timestamp_day < 1) || (timestamp_day > 31))) {
					return null;
				}

				const option1 = new Date(now.getFullYear(), now.getMonth(), timestamp_day, timestamp_hour, timestamp_minute, 0);
				const option2 = new Date(now.getFullYear(), now.getMonth() + 1, timestamp_day, timestamp_hour, timestamp_minute, 0);
				const diff1 = Math.abs(option1.getTime() - now.getTime());
				const diff2 = Math.abs(option2.getTime() - now.getTime());
				const timestamp = (diff1 < diff2) ? option1 : option2;
				return new Timestamp(TimestampMode.ABSOLUTE, timestamp);
			}
		}

		/* Relative timestamp relative to current time */
		{
			const match = timestamp_str.match(/^\s*\+\s*(?<timestamp_hour>\d{1,2}):(?<timestamp_minute>\d{2})\s*$/);
			if (match) {
				const timestamp_hour = match.groups.timestamp_hour | 0;
				const timestamp_minute = match.groups.timestamp_minute | 0;
				const relative_seconds = (timestamp_hour * 3600) + (timestamp_minute * 60);
				return new Timestamp(TimestampMode.RELATIVE_NOW, relative_seconds);
			}
		}

		/* Fraction of the presentation duration */
		{
			const match = timestamp_str.match(/^\s*(?<numerator>\d+)\s*\/\s*(?<denominator>\d+)\s*$/);
			if (match) {
				const numerator = match.groups.numerator | 0;
				const denominator = match.groups.denominator | 0;
				if (denominator == 0) {
					return null;
				}
				return new Timestamp(TimestampMode.RELATIVE_PRESENTATION_LENGTH, numerator / denominator);
			}
		}

		/* Percent value of the presentation duration */
		{
			const match = timestamp_str.match(/^\s*(?<percent>\d+)\s*%\s*$/);
			if (match) {
				const percent = match.groups.percent | 0;
				if (percent == 0) {
					return null;
				}
				return new Timestamp(TimestampMode.RELATIVE_PRESENTATION_LENGTH, percent / 100);
			}
		}

		return null;
	}

	static format_datetime(datetime) {
		return {
			day: 	String(datetime.getFullYear()).padStart(4, "0") + "-" + String((datetime.getMonth() + 1)).padStart(2, "0") + "-" + String(datetime.getDate()).padStart(2, "0"),
			hms:	String(datetime.getHours()).padStart(2, "0") + ":" + String(datetime.getMinutes()).padStart(2, "0") + ":" + String(datetime.getSeconds()).padStart(2, "0"),
		}
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

	static format_hm(total_seconds) {
		if (total_seconds <= -0.5) {
			return "-" + TimeTools.format_hm(-total_seconds);
		}
		total_seconds = Math.round(total_seconds);
		const hours = Math.floor(total_seconds / 3600);
		const minutes = Math.floor(total_seconds % 3600 / 60);
		return String(hours) + ":" + String(minutes).padStart(2, "0");
	}

	static format_ms(total_seconds) {
		return TimeTools.format_hm(total_seconds * 60);
	}
}

export class MathTools {
	static clamp(value, minval, maxval) {
		if (value < minval) {
			return minval;
		} else if (value > maxval) {
			return maxval;
		} else {
			return value;
		}
	}
}
