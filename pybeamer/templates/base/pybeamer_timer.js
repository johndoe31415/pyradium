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

import {TimeTools} from "./pybeamer_tools.js";

export class PresentationTimer {
	constructor(ui_elements) {
		this._ui_elements = ui_elements;
		this._bc = new BroadcastChannel("presentation");
		this._bc.addEventListener("message", (msg) => this._rx_message(msg));
		this._session = null;
		this._status = null;
		this._meta = null;
		this._active_presentation_time_secs = 300.0;
		this._tx_message({ "type": "query_status" });
		this._tx_message({ "type": "query_presentation_meta" });
	}

	_update() {
		if ((this._status == null) || (this._meta == null)) {
			return;
		}

		let current_rel_ratio = 0;
		let slide_time_allocation_secs = 0;
		if (Math.abs(this._status.begin_ratio - this._status.end_ratio) > 1e-4) {
			/* Non-zero time slide */
			const current_abs_ratio = this._status.timekeeper.started / this._active_presentation_time_secs;
			current_rel_ratio = (current_abs_ratio - this._status.begin_ratio) / (this._status.end_ratio - this._status.begin_ratio);
			slide_time_allocation_secs = (this._status.end_ratio - this._status.begin_ratio) * this._active_presentation_time_secs;
		}
		const slide_time_used_secs = current_rel_ratio * slide_time_allocation_secs;
		const slide_time_remaining_secs = slide_time_allocation_secs - slide_time_used_secs;

		this._ui_elements.presentation_mode.innerHTML = this._status.presentation_mode;
		this._ui_elements.spent_time.innerHTML = this._status.timekeeper.started;
		this._ui_elements.slide_time_allocation.innerHTML = TimeTools.format_hms(slide_time_allocation_secs);
		this._ui_elements.slide_time_remaining.innerHTML = TimeTools.format_hms(slide_time_remaining_secs);
	}

	_update_meta() {
		this._ui_elements.total_presentation_time.value = this._meta.total_presentation_time;
		this._ui_elements.pause_minutes.value = this._meta.pause_minutes;
	}

	_tx_message(msg) {
		this._bc.postMessage(msg);
	}

	_rx_message(msg) {
		const data = msg.data;
		if ((this._session != null) && (this._session != data.data.presentation_id)) {
			/* Other presentation window open, ignore data. */
			return;
		}

		if (data.type == "status") {
			if (this._session == null) {
				this._session = data.data.presentation_id;
			}
			this._status = data.data;

			this._update();
		} else if (data.type == "presentation_meta") {
			if (this._meta == null) {
				this._meta = data.data;
				this._update_meta();
				this._update();
			}
		}
	}
}
