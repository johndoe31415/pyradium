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

import {TimeTools, MathTools} from "./pyradium_tools.js";

const TimerMode = {
	STOPPED: 0,
	ARMED: 1,
	STARTED: 2,
}

class SlideSubset {
	constructor(begin_slide, end_slide) {
		this._begin_slide = begin_slide;
		this._end_slide = end_slide;
	}

	get begin_slide() {
		return this._begin_slide;
	}

	get end_slide() {
		return this._end_slide;
	}
}

class SlideSubsetSelector {
	constructor(slide_ratios) {
		this._slide_ratios = slide_ratios;
		this._cumulative_ratios = [ ];

		let cumulative_ratio = 0;
		for (let slide_ratio of this._slide_ratios) {
			cumulative_ratio += slide_ratio;
			this._cumulative_ratios.push(cumulative_ratio);
		}
	}

	get_ratio_of_subset(slide_subset) {
		const begin_ratio = (slide_subset.begin_slide == 1) ? 0 : this._cumulative_ratios[slide_subset.begin_slide - 2];
		const end_ratio = this._cumulative_ratios[slide_subset.end_slide - 1];
		return end_ratio - begin_ratio;
	}

	_find_slide_ratio(ratio, begin_slide = 1) {
		for (let i = begin_slide - 1; i < this._cumulative_ratios.length; i++) {
			const cumulative_ratio = this._cumulative_ratios[i];
			if (cumulative_ratio >= ratio) {
				return i + 1;
			}
		}
		return this.slide_count;
	}

	get slide_count() {
		return this._slide_ratios.length;
	}

	parse(selector) {
		/* Special keywords 'all' or '*' */
		if ((selector.toLowerCase() == "all") || (selector == "*")) {
			if (this.slide_count != null) {
				return new SlideSubset(1, this.slide_count);
			} else {
				return null;
			}
		}

		/* Range in the form of "begin - end" where
		 *     a prefix of '#' means: count-based instead of time-based
		 *     any value of 'begin' or 'end' can be a percent value by using a '%' suffix
		 */
		{
			const match = selector.match(/^\s*(?<count>#\s*)?((?<lhs>(?<lhs_num>\d+)(?<lhs_percent>\s*%)?))?\s*-\s*((?<rhs>(?<rhs_num>\d+)(?<rhs_percent>\s*%)?))?\s*$/);
			if (match) {
				const count_based = (match.groups.count != null);
				let begin_slide = 1;
				if (match.groups.lhs != null) {
					const lhs_percent = (match.groups.lhs_percent != null);
					const lhs_value = match.groups.lhs_num | 0;

					if (!lhs_percent) {
						/* Plain value like '5', always count-based */
						begin_slide = lhs_value;
					} else {
						if (count_based) {
							/* Percent value like '33%', count-based */
							begin_slide = Math.round(lhs_value / 100 * (this.slide_count - 1)) + 1;
						} else {
							/* Percent value like '33%', time-based */
							begin_slide = this._find_slide_ratio(lhs_value / 100);
						}
						if (begin_slide > 1) {
							/* We want to start offset one, so that for 100 slides,
							 * 0% - 50%   =>   1 - 50
							 * 50% - 100% =>   51 - 100
							 */
							begin_slide += 1;
						}
					}
				}
				begin_slide = MathTools.clamp(begin_slide, 1, this.slide_count);


				let end_slide = this.slide_count;
				if (match.groups.rhs != null) {
					const rhs_percent = (match.groups.rhs_percent != null);
					const rhs_value = match.groups.rhs_num | 0;

					if (!rhs_percent) {
						/* Plain value like '15', always count-based */
						end_slide = match.groups.rhs_num | 0;
					} else {

						if (count_based) {
							/* Percent value like '66%', count-based */
							end_slide = Math.round(rhs_value / 100 * (this.slide_count - 1)) + 1;
						} else {
							/* Percent value like '66%', time-based */
							end_slide = this._find_slide_ratio(rhs_value / 100, begin_slide);
						}
					}
				}
				end_slide = MathTools.clamp(end_slide, 1, this.slide_count);

				if (begin_slide <= end_slide) {
					return new SlideSubset(begin_slide, end_slide);
				} else {
					return null;
				}
			}
		}

		/* Fraction in the form of n/m */
		{
			const match = selector.match(/^\s*(?<count>#\s*)?(?<numerator>\d+)\s*\/\s*(?<denominator>\d+)\s*$/);
			if (match) {
				const count_based = (match.groups.count != null);
				const numerator = match.groups.numerator | 0;
				const denominator = match.groups.denominator | 0;
				if (numerator < 1) {
					return null;
				} else if (denominator < numerator) {
					return null;
				}

				let begin_slide, end_slide;
				if (count_based) {
					begin_slide = Math.round((numerator - 1) / denominator * this.slide_count) + 1;
					end_slide = Math.round(numerator / denominator * this.slide_count);
				} else {
					begin_slide = this._find_slide_ratio((numerator - 1) / denominator);
					end_slide = this._find_slide_ratio(numerator / denominator, begin_slide) - 1;
				}

				begin_slide = MathTools.clamp(begin_slide, 1, this.slide_count);
				end_slide = MathTools.clamp(end_slide, 1, this.slide_count);

				if (begin_slide <= end_slide) {
					return new SlideSubset(begin_slide, end_slide);
				} else {
					return null;
				}
			}
		}


		return null;
	}
}


export class PresentationTimer {
	constructor(ui_elements) {
		this._ui_elements = ui_elements;
		this._bc = new BroadcastChannel("presentation");
		this._bc.addEventListener("message", (msg) => this._rx_message(msg));
		this._nominal_presentation_duration_secs = null;
		this._slide_subset_selector = null;
		this._session_id = null;
		this._status = null;
		this._meta = null;
		this._tx_message({ "type": "query_status" });
		this._tx_message({ "type": "query_presentation_meta" });
		this._timer_mode = TimerMode.STOPPED;
		this._timeout_handle = null;
		this._active_timer = null;
		this._reset_timeout();
		this._initialize_ui();
	}

	_initialize_ui() {
		this._ui_elements.slide_subset.value = "all";
		this._ui_elements.presentation_end_time.addEventListener("input", (event) => this._ui_update_everything());
		this._ui_elements.slide_subset.addEventListener("input", (event) => this._ui_update_everything());
		this._ui_elements.btn_arm_timer.addEventListener("click", (event) => this.arm_timer());
		this._ui_elements.btn_start_stop_timer.addEventListener("click", (event) => this.start_stop_timer());
		this._ui_update_everything();
	}

	_ui_update_input_fields() {
		this._presentation_end_time = TimeTools.parse_timestamp(this._ui_elements.presentation_end_time.value);
		if (this._presentation_end_time == null) {
			this._ui_elements.presentation_end_time.classList.add("parse-error");
		} else {
			this._ui_elements.presentation_end_time.classList.remove("parse-error");
		}

		if (this._slide_subset_selector != null) {
			this._slide_subset = this._slide_subset_selector.parse(this._ui_elements.slide_subset.value, (this._meta == null) ? null : this._meta.slide_count);
			if (this._slide_subset == null) {
				this._ui_elements.slide_subset.classList.add("parse-error");
			} else {
				this._ui_elements.slide_subset.classList.remove("parse-error");
			}
		}

		let duration_secs = null;
		if (this._presentation_end_time != null) {
			const end_ts = this._presentation_end_time.compute(this._nominal_presentation_duration_secs);
			const hh_mm_str = end_ts.getHours() + ":" + end_ts.getMinutes().toString().padStart(2, "0");
			const now = new Date();
			duration_secs = (end_ts.getTime() - now.getTime()) / 1000;
			this._ui_elements.presentation_end_time_display.innerText = hh_mm_str;
			this._ui_elements.presentation_duration_display.innerText = TimeTools.format_hm(duration_secs);
		} else {
			this._ui_elements.presentation_end_time_display.innerText = "-";
			this._ui_elements.presentation_duration_display.innerText = "-";
		}

		let nominal_slide_duration_secs = null;
		if (this._slide_subset != null) {
			nominal_slide_duration_secs = this._compute_nominal_slide_duration_secs();
			this._ui_elements.slide_subset_display.innerText = this._slide_subset.begin_slide + " - " + this._slide_subset.end_slide;
			this._ui_elements.slide_count_display.innerText = this._slide_subset.end_slide - this._slide_subset.begin_slide + 1;
			this._ui_elements.nominal_slide_duration_display.innerText = TimeTools.format_hm(nominal_slide_duration_secs);
		} else {
			this._ui_elements.slide_subset_display.innerText = "-";
			this._ui_elements.slide_count_display.innerText = "-";
			this._ui_elements.nominal_slide_duration_display.innerText = "-";
		}
		if ((this._presentation_end_time != null) && (this._slide_subset != null)) {
			const pace_percent = nominal_slide_duration_secs / duration_secs * 100;
			this._ui_elements.presentation_pace_display.innerText = pace_percent.toFixed(0) + "%";
		} else {
			this._ui_elements.presentation_pace_display.innerText = "-";
		}
	}

	_ui_update_buttons() {
		const time_and_slides_set = (this._presentation_end_time != null) && (this._slide_subset != null);
		switch (this._timer_mode) {
			case TimerMode.STOPPED:
				this._ui_elements.btn_arm_timer.innerText = "Arm Timer";
				this._ui_elements.btn_start_stop_timer.innerText = "Start Timer";
				this._ui_elements.btn_arm_timer.disabled = !time_and_slides_set;
				this._ui_elements.btn_start_stop_timer.disabled = !time_and_slides_set;
				this._ui_elements.presentation_end_time.disabled = false;
				this._ui_elements.slide_subset.disabled = false;
				break;

			case TimerMode.ARMED:
				this._ui_elements.btn_arm_timer.disabled = false;
				this._ui_elements.btn_arm_timer.innerText = "Disarm Timer";
				this._ui_elements.btn_start_stop_timer.innerText = "Start Timer";
				this._ui_elements.btn_arm_timer.disabled = false;
				this._ui_elements.btn_start_stop_timer.disabled = false;
				this._ui_elements.presentation_end_time.disabled = true;
				this._ui_elements.slide_subset.disabled = true;
				break;

			case TimerMode.STARTED:
				this._ui_elements.btn_arm_timer.innerText = "Arm Timer";
				this._ui_elements.btn_start_stop_timer.innerText = "Stop Timer";
				this._ui_elements.btn_arm_timer.disabled = true;
				this._ui_elements.btn_start_stop_timer.disabled = false;
				this._ui_elements.presentation_end_time.disabled = true;
				this._ui_elements.slide_subset.disabled = true;
				break;
		}
	}

	_ui_update_display() {
		switch (this._timer_mode) {
			case TimerMode.STARTED:
				this._ui_elements.presentation_mode_display.innerHTML = "<img src=\"media_play.svg\" class=\"media\">";
				break;

			case TimerMode.STOPPED:
				this._ui_elements.presentation_mode_display.innerHTML = "<img src=\"media_stop.svg\" class=\"media\">";
				break;

			case TimerMode.ARMED:
				this._ui_elements.presentation_mode_display.innerHTML = "<img src=\"media_pause.svg\" class=\"media\">";
				break;

			default:
				console.log("Error, unknown presentation mode:", this._status.presentation_mode);
				this._ui_elements.presentation_mode_display.innerHTML = "Error: Unknown presentation mode.";
		}


		if ((this._status == null) || (this._meta == null) || (this._active_timer == null)) {
			return;
		}

		console.log(this._active_timer);
		const now = new Date();
		const remaining_presentation_time_secs = (this._active_timer.presentation_end.getTime() - now.getTime()) / 1000;
		const elapsed_time_secs = (now.getTime() - this._active_timer.presentation_start.getTime()) / 1000;

		this._ui_elements.presentation_time_display.innerText = TimeTools.format_hms(this._active_timer.presentation_duration_secs);
		this._ui_elements.elapsed_time_display.innerText = TimeTools.format_hms(elapsed_time_secs);
		this._ui_elements.remaining_time_display.innerText = TimeTools.format_hms(remaining_presentation_time_secs);

		return;

		const begin_time_secs = this._status.begin_ratio * this._active_presentation_time_secs;
		const end_time_secs = this._status.end_ratio * this._active_presentation_time_secs;
		const slide_time_allocation_secs = end_time_secs - begin_time_secs;
		const slide_time_remaining_secs = end_time_secs - this._status.timekeeper.started;
		const slide_time_used_secs = slide_time_allocation_secs - slide_time_remaining_secs;
		//const remaining_presentation_time_secs = this._active_presentation_time_secs - this._status.timekeeper.started;

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

	_ui_update_everything() {
		this._ui_update_input_fields();
		this._ui_update_buttons();
		this._ui_update_display();
	}

	_compute_nominal_slide_duration_secs() {
		if (this._slide_subset == null) {
			return null;
		}
		const ratio = this._slide_subset_selector.get_ratio_of_subset(this._slide_subset);
		return ratio * this._nominal_presentation_duration_secs;
	}

	_reset_timeout() {
		if (this._timeout_handle != null) {
			window.clearTimeout(this._timeout_handle);
		}
		this._timeout_handle = window.setTimeout(() => this._connection_lost(), 5000);
	}

	_connection_lost() {
		console.log("Connection to presentation lost.");
		this._ui_elements.presentation_mode_display.innerHTML = "<img src=\"media_error.svg\" class=\"media\" title=\"Error: Could not connect to presentation.\">"
	}

	_update_meta() {
		if (this._meta.presentation_time != null) {
			this._ui_elements.presentation_end_time.value = "+" + this._meta.presentation_time;
			this._nominal_presentation_duration_secs = TimeTools.parse_hh_mm(this._meta.presentation_time) * 60;
		}
		this._slide_subset_selector = new SlideSubsetSelector(this._meta.slide_ratios);
		this._ui_update_everything();
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

			this._ui_update_display();
		} else if (data.type == "presentation_meta") {
			if (this._meta == null) {
				this._meta = data.data;
				this._update_meta();
			}
		}
	}

	start_timer() {
		if (this._timer_mode == TimerMode.STARTED) {
			return;
		}

		this._timer_mode = TimerMode.STARTED;
		this._active_timer = {
			presentation_start: new Date(),
			presentation_end: TimeTools.parse_timestamp(this._ui_elements.presentation_end_time.value).compute(this._nominal_presentation_duration_secs),
			slide_subset: this._slide_subset_selector.parse(this._ui_elements.slide_subset.value, (this._meta == null) ? null : this._meta.slide_count),
		};

		this._active_timer.presentation_duration_secs = (this._active_timer.presentation_end.getTime() - this._active_timer.presentation_start.getTime()) / 1000;
	}

	start_timer_if_armed() {
		if (this._timer_mode == TimerMode.ARMED) {
			this.start_timer();
			this._ui_update_everything();
		}
	}

	arm_timer() {
		console.log("Arm timer.");
		if (this._timer_mode == TimerMode.ARMED) {
			/* Disarm timer */
			this._timer_mode = TimerMode.STOPPED;
			this._active_timer = null;
		} else {
			/* Arm timer */
			this._timer_mode = TimerMode.ARMED;
		}
		this._ui_update_everything();
	}

	start_stop_timer() {
		console.log("Start timer.");

		if ((this._timer_mode == TimerMode.STOPPED) || (this._timer_mode == TimerMode.ARMED)) {
			/* Starting timer */
			this.start_timer();
		} else if (this._timer_mode == TimerMode.STARTED) {
			/* Stopping timer */
			this._timer_mode = TimerMode.STOPPED;
		}
		this._ui_update_everything();
	}
}
