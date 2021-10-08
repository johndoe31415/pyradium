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

export class TimeKeeper {
	constructor() {
		this._mode = null;
		this._timesum = { };
		this._start_ts = 0;
	}

	_timet() {
		return Date.now() / 1000;
	}

	get mode() {
		return this._mode;
	}

	set mode(value) {
		const now = this._timet();
		if (this._mode != null) {
			const current_elapsed = now - this._start_ts;
			this._timesum[this._mode] += current_elapsed;
		}
		this._mode = value;
		if (this._mode != null) {
			if (!(this._mode in this._timesum)) {
				this._timesum[this._mode] = 0;
			}
			this._start_ts = now;
		}
	}

	time_spent_in(mode) {
		if (!(mode in this._timesum)) {
			return 0;
		}
		if (mode == this._mode) {
			const now = this._timet();
			const current_elapsed = now - this._start_ts;
			return this._timesum[mode] + current_elapsed;
		} else {
			return this._timesum[mode];
		}
	}

	dump() {
		for (let mode in this._timesum) {
			console.log(mode, this.time_spent_in(mode));
		}
	}
}
