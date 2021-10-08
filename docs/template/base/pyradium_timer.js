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

import {TimeTools} from "./pyradium_tools.js";

export class PresentationTimer {
	constructor(ui_elements) {
		this._ui_elements = ui_elements;
		this._bc = new BroadcastChannel("presentation");
		this._bc.addEventListener("message", (msg) => this._rx_message(msg));
		this._session_id = null;
		this._status = null;
		this._meta = null;
		this._total_presentation_time = null;
		this._active_presentation_time_secs = null;
		this._pause_minutes = null;
		this._tx_message({ "type": "query_status" });
		this._tx_message({ "type": "query_presentation_meta" });
		this._timeout_handle = null;
		this._reset_timeout();
		this._ui_elements.total_presentation_time.addEventListener("input", (event) => this._ui_change());
		this._ui_elements.pause_minutes.addEventListener("input", (event) => this._ui_change());
	}

	_ui_change() {
		this._total_presentation_time = TimeTools.parse_timerange(this._ui_elements.total_presentation_time.value);
		this._pause_minutes = this._ui_elements.pause_minutes.value | 0;
		this._active_presentation_time_secs = null;
		if (this._total_presentation_time != null) {
			const active_presentation_time_secs = this._total_presentation_time.duration_seconds - (60 * this._pause_minutes);
			if (active_presentation_time_secs > 0) {
				this._active_presentation_time_secs = active_presentation_time_secs;
			}
		}
		this._update();
	}

	_reset_timeout() {
		if (this._timeout_handle != null) {
			window.clearTimeout(this._timeout_handle);
		}
		this._timeout_handle = window.setTimeout(() => this._connection_lost(), 5000);
	}

	_connection_lost() {
		console.log("Connection to presentation lost.");
		this._ui_elements.presentation_mode.innerHTML = "Error: Could not connect to presentation.";
	}

	_update() {
		if ((this._status == null) || (this._meta == null) || (this._active_presentation_time_secs == null)) {
			return;
		}

		const begin_time_secs = this._status.begin_ratio * this._active_presentation_time_secs;
		const end_time_secs = this._status.end_ratio * this._active_presentation_time_secs;
		const slide_time_allocation_secs = end_time_secs - begin_time_secs;
		const slide_time_remaining_secs = end_time_secs - this._status.timekeeper.started;
		const slide_time_used_secs = slide_time_allocation_secs - slide_time_remaining_secs;
		const remaining_presentation_time_secs = this._active_presentation_time_secs - this._status.timekeeper.started;

		/* The speed error is 0 as long as we're in the time window for that
		 * slide.
		 */
		let speed_error_secs = 0;
		if (this._status.timekeeper.started < begin_time_secs) {
			/* We're too fast. Speed error is positive. */
			speed_error_secs = begin_time_secs - this._status.timekeeper.started;
		} else if (this._status.timekeeper.started > end_time_secs) {
			/* We're too slow. Speed error is negative. */
			speed_error_secs = end_time_secs - this._status.timekeeper.started;
		}

		this._ui_elements.presentation_mode.className = this._status.presentation_mode;
		switch (this._status.presentation_mode) {
			case "started":
				this._ui_elements.presentation_mode.innerHTML = "<img src=\"media_play.svg\" class=\"media\">";
				break;

			case "stopped":
				this._ui_elements.presentation_mode.innerHTML = "<img src=\"media_stop.svg\" class=\"media\">";
				break;

			case "pause":
				this._ui_elements.presentation_mode.innerHTML = "<img src=\"media_pause.svg\" class=\"media\">";
				break;

			default:
				console.log("Error, unknown presentation mode:", this._status.presentation_mode);
				this._ui_elements.presentation_mode.innerHTML = "Error: Unknown presentation mode.";
		}
		this._ui_elements.spent_time.innerHTML = TimeTools.format_hms(this._status.timekeeper.started);
		this._ui_elements.slide_time_allocation.innerHTML = TimeTools.format_hms(slide_time_allocation_secs);
		this._ui_elements.slide_time_used.innerHTML = TimeTools.format_hms(slide_time_used_secs);
		this._ui_elements.slide_time_remaining.innerHTML = TimeTools.format_hms(slide_time_remaining_secs);
		this._ui_elements.remaining_time.innerHTML = TimeTools.format_hms(remaining_presentation_time_secs);

		this._ui_elements.main_indicator.className = "main_indicator";
		const delay_large_cutoff_secs = 300;
		const delay_small_cutoff_secs = 30;
		if (speed_error_secs < -delay_large_cutoff_secs) {
			this._ui_elements.main_indicator.classList.add("largely_behind");
		} else if (speed_error_secs < -delay_small_cutoff_secs) {
			this._ui_elements.main_indicator.classList.add("slightly_behind");
		} else if (speed_error_secs < delay_small_cutoff_secs) {
			this._ui_elements.main_indicator.classList.add("caught_up");
		} else if (speed_error_secs < delay_large_cutoff_secs) {
			this._ui_elements.main_indicator.classList.add("slightly_ahead");
		} else {
			this._ui_elements.main_indicator.classList.add("largely_ahead");
		}
	}

	_update_meta() {
		this._ui_elements.total_presentation_time.value = this._meta.total_presentation_time;
		this._ui_elements.pause_minutes.value = this._meta.pause_minutes;
		this._ui_change();
	}

	_tx_message(msg) {
		this._bc.postMessage(msg);
	}

	_rx_message(msg) {
		const data = msg.data;
		if ((this._session_id != null) && (this._session_id != data.session_id)) {
			/* Other presentation window open, ignore data. */
			return;
		}

		this._reset_timeout();
		if (data.type == "status") {
			if (this._session_id == null) {
				this._session_id = data.session_id;
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
