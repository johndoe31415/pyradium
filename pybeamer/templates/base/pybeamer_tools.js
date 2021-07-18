/*
	*	pybeamer - HTML presentation/slide show generator
	*	Copyright (C) 2015-2021 Johannes Bauer
	*
	*	This file is part of pybeamer.
	*
	*	pybeamer is free software; you can redistribute it and/or modify
	*	it under the terms of the GNU General Public License as published by
	*	the Free Software Foundation; this program is ONLY licensed under
	*	version 3 of the License, later versions are explicitly excluded.
	*
	*	pybeamer is distributed in the hope that it will be useful,
	*	but WITHOUT ANY WARRANTY; without even the implied warranty of
	*	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	*	GNU General Public License for more details.
	*
	*	You should have received a copy of the GNU General Public License
	*	along with pybeamer; if not, write to the Free Software
	*	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
	*
	*	Johannes Bauer <JohannesBauer@gmx.de>
*/

export class TimeTools {
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
