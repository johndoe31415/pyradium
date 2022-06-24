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

	get slide_count() {
		return this.end_slide - this.begin_slide + 1;
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

	get_cumulative_ratio_before(slide_no) {
		if (slide_no == 1) {
			return 0;
		} else {
			return this._cumulative_ratios[slide_no - 2];
		}
	}

	get_cumulative_ratio_after(slide_no) {
		return this._cumulative_ratios[slide_no - 1];
	}

	get_ratio_of(slide_no) {
		return this._slide_ratios[slide_no - 1];
	}

	get_ratio_of_subset(slide_subset) {
		const begin_ratio = this.get_cumulative_ratio_before(slide_subset.begin_slide);
		const end_ratio = this.get_cumulative_ratio_after(slide_subset.end_slide);
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
	constructor(ui_elements, session_id) {
		this._ui_elements = ui_elements;
		this._session_id = session_id;
		this._bc = new BroadcastChannel("presentation");
		this._bc.addEventListener("message", (msg) => this._rx_message(msg));
		this._nominal_presentation_duration_secs = null;
		this._presentation_duration_secs = null;
		this._slide_subset_selector = null;
		this._current_slide = null;
		this._meta = null;
		this._tx_message({ "type": "query_slide_info" });
		this._tx_message({ "type": "query_presentation_meta" });
		this._timer_mode = TimerMode.STOPPED;
		this._timeout_handle = null;
		this._have_connection = false;
		this._active_timer = null;
		this._dynamic_timer = null;
		this._reset_timeout();
		this._initialize_ui();
		setInterval(() => this._ui_update_display(), 1000);
	}

	_initialize_ui() {
		this._ui_elements.slide_subset.value = "all";
		this._ui_elements.presentation_end_time.addEventListener("input", (event) => this._ui_update_everything());
		this._ui_elements.slide_subset.addEventListener("input", (event) => this._ui_update_everything());
		this._ui_elements.btn_arm_timer.addEventListener("click", (event) => this.arm_timer());
		this._ui_elements.btn_start_timer.addEventListener("click", (event) => this.start_timer());
		this._ui_elements.main_indicator.addEventListener("click", (event) => this.stop_timer());
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

		if (this._presentation_end_time != null) {
			const end_ts = this._presentation_end_time.compute(this._nominal_presentation_duration_secs);
			const hh_mm_str = end_ts.getHours() + ":" + end_ts.getMinutes().toString().padStart(2, "0");
			const now = new Date();
			this._presentation_duration_secs = (end_ts.getTime() - now.getTime()) / 1000;
			this._ui_elements.presentation_end_time_display.innerText = hh_mm_str;
			this._ui_elements.presentation_duration_display.innerText = TimeTools.format_hm(this._presentation_duration_secs);
		} else {
			this._ui_elements.presentation_end_time_display.innerText = "-";
			this._ui_elements.presentation_duration_display.innerText = "-";
			this._presentation_duration_secs = null;
		}

		let nominal_subset_duration_secs = this._compute_nominal_subset_duration_secs();
		if (nominal_subset_duration_secs != null) {
			const average_slide_duration_secs = nominal_subset_duration_secs / this._slide_subset.slide_count;
			this._ui_elements.slide_subset_display.innerText = this._slide_subset.begin_slide + " - " + this._slide_subset.end_slide;
			this._ui_elements.slide_count_display.innerText = this._slide_subset.end_slide - this._slide_subset.begin_slide + 1;
			this._ui_elements.average_slide_duration_display.innerText = TimeTools.format_ms(average_slide_duration_secs);
		} else {
			this._ui_elements.slide_subset_display.innerText = "-";
			this._ui_elements.slide_count_display.innerText = "-";
			this._ui_elements.average_slide_duration_display.innerText = "-";
		}

		if ((this._presentation_end_time != null) && (this._slide_subset != null)) {
			const pace_percent = nominal_subset_duration_secs / this._presentation_duration_secs * 100;
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
				this._ui_elements.btn_arm_timer.disabled = !time_and_slides_set;
				this._ui_elements.presentation_end_time.disabled = false;
				this._ui_elements.slide_subset.disabled = false;
				this._ui_elements.timer_inactive_menu.style.display = "";
				break;

			case TimerMode.ARMED:
				this._ui_elements.btn_arm_timer.disabled = false;
				this._ui_elements.btn_arm_timer.innerText = "Disarm Timer";
				this._ui_elements.btn_arm_timer.disabled = false;
				this._ui_elements.presentation_end_time.disabled = true;
				this._ui_elements.slide_subset.disabled = true;
				this._ui_elements.timer_inactive_menu.style.display = "";
				break;

			case TimerMode.STARTED:
				this._ui_elements.btn_arm_timer.innerText = "Arm Timer";
				this._ui_elements.btn_arm_timer.disabled = true;
				this._ui_elements.presentation_end_time.disabled = true;
				this._ui_elements.slide_subset.disabled = true;
				this._ui_elements.timer_inactive_menu.style.display = "none";
				break;
		}
	}

	_ui_update_display() {
		const now_date = new Date();
		const now = now_date.getTime();
		const now_fmt = TimeTools.format_datetime(now_date);
		this._ui_elements.datetime_now.innerHTML = now_fmt.day + "<br/>" + now_fmt.hms;

		if (this._have_connection) {
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
					console.log("Error, unknown timer mode:", this._timer_mode);
					this._ui_elements.presentation_mode_display.innerHTML = "Error: Unknown timer mode.";
			}
		} else {
			this._ui_elements.presentation_mode_display.innerHTML = "<img src=\"media_error.svg\" class=\"media\" title=\"Error: Connection to presentation lost.\">"
		}

		if ((this._current_slide == null) || (this._meta == null) || (this._active_timer == null)) {
			return;
		}

		const remaining_presentation_time_secs = (this._active_timer.presentation_end.getTime() - now) / 1000;
		const nominal_elapsed_time_secs = (now - this._active_timer.presentation_start.getTime()) / 1000;
		const dynamic_elapsed_time_secs = (now - this._dynamic_timer.presentation_start.getTime()) / 1000;
		const position_based_on_time_percent = nominal_elapsed_time_secs / this._active_timer.presentation_duration_secs * 100;
		const remaining_slide_count = this._active_timer.slide_subset.slide_count - (this._current_slide - this._active_timer.slide_subset.begin_slide + 1);
		const presentation_end_hh_mm_str = this._active_timer.presentation_end.getHours() + ":" + this._active_timer.presentation_end.getMinutes().toString().padStart(2, "0");

		this._ui_elements.presentation_time_display.innerHTML = TimeTools.format_hms(this._active_timer.presentation_duration_secs) + "<br />until " + presentation_end_hh_mm_str;
		this._ui_elements.elapsed_time_display.innerHTML = TimeTools.format_hms(nominal_elapsed_time_secs) + "<br />" + position_based_on_time_percent.toFixed(0) + "%";
		this._ui_elements.remaining_display.innerHTML = TimeTools.format_hms(remaining_presentation_time_secs) + "<br />" + remaining_slide_count + " slides";

		const current_slide_ratio = this._slide_subset_selector.get_ratio_of(this._current_slide);
		const current_slide_nominal_duration_secs = current_slide_ratio / this._active_timer.subset_ratio * this._active_timer.presentation_duration_secs;
		const current_slide_dynamic_duration_secs = current_slide_ratio / this._dynamic_timer.subset_ratio * this._dynamic_timer.presentation_duration_secs;
		this._ui_elements.slide_time_display.innerHTML = "nominal " + TimeTools.format_hms(current_slide_nominal_duration_secs) + "<br />dynamic " + TimeTools.format_hms(current_slide_dynamic_duration_secs);

		const cumulative_current_slide_ratio = this._slide_subset_selector.get_cumulative_ratio_before(this._current_slide);

		const nominal_subset_begin_ratio = this._slide_subset_selector.get_cumulative_ratio_before(this._active_timer.slide_subset.begin_slide);
		const nominal_current_completion_ratio = (cumulative_current_slide_ratio - nominal_subset_begin_ratio) / this._active_timer.subset_ratio;
		const ideal_nominal_elapsed_time_secs = nominal_current_completion_ratio * this._active_timer.presentation_duration_secs;

		const dynamic_subset_begin_ratio = this._slide_subset_selector.get_cumulative_ratio_before(this._dynamic_timer.slide_subset.begin_slide);
		const dynamic_current_completion_ratio = (cumulative_current_slide_ratio - dynamic_subset_begin_ratio) / this._dynamic_timer.subset_ratio;
		const ideal_dynamic_elapsed_time_secs = dynamic_current_completion_ratio * this._dynamic_timer.presentation_duration_secs;

		const nominal_delta_time_secs = ideal_nominal_elapsed_time_secs - nominal_elapsed_time_secs + current_slide_nominal_duration_secs;
		const dynamic_delta_time_secs = ideal_dynamic_elapsed_time_secs - dynamic_elapsed_time_secs + current_slide_dynamic_duration_secs;
		if (this._current_slide <= this._dynamic_timer.slide_subset.end_slide) {
			this._ui_elements.dynamic_delta_time_display.innerText = TimeTools.format_hms(dynamic_delta_time_secs);
		} else {
			/* Dynamic timings do not make sense when exceeding the subset, so default to the nominal timing then */
			this._ui_elements.dynamic_delta_time_display.innerText = TimeTools.format_hms(nominal_delta_time_secs);
		}
		this._ui_elements.nominal_delta_time_display.innerText = TimeTools.format_hms(nominal_delta_time_secs);

		const current_slide_no_within_subset = this._current_slide - this._active_timer.slide_subset.begin_slide + 1;
		const position_based_on_slides = (this._current_slide - this._active_timer.slide_subset.begin_slide + 1) / this._active_timer.slide_subset.slide_count * 100;
		this._ui_elements.slide_position_display.innerHTML = current_slide_no_within_subset + "/" + this._active_timer.slide_subset.slide_count + "<br />" + position_based_on_slides.toFixed(0) + "%";

		let speed_error_secs = 0;
		if (nominal_delta_time_secs > current_slide_nominal_duration_secs) {
			/* We're too fast. Speed error is positive. */
			speed_error_secs = nominal_delta_time_secs - current_slide_nominal_duration_secs;
		} else if (nominal_delta_time_secs < 0) {
			/* We're too slow. Speed error is negative. */
			speed_error_secs = nominal_delta_time_secs;
		}

		this._ui_elements.main_indicator.className = "main_indicator";
		const delay_small_cutoff_secs = this._active_timer.presentation_duration_secs / 60;		/* at 30 minutes, this is 30 seconds */
		const delay_large_cutoff_secs = this._active_timer.presentation_duration_secs / 10;		/* at 30 minutes, this is 3 minutes */
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

	_compute_nominal_subset_duration_secs() {
		if ((this._slide_subset == null) || (this._presentation_duration_secs == null)) {
			return null;
		}
		const subset_ratio = this._slide_subset_selector.get_ratio_of_subset(this._slide_subset);
		const nominal_subset_duration_secs = subset_ratio * this._nominal_presentation_duration_secs;
		return nominal_subset_duration_secs;
	}

	_reset_timeout() {
		if (this._timeout_handle != null) {
			window.clearTimeout(this._timeout_handle);
		}
		this._timeout_handle = window.setTimeout(() => this._connection_lost(), 6000);
		const reconnected = !this._have_connection;
		if (reconnected) {
			console.log("Connection to presentation established.");
			this._have_connection = true;
			this._ui_update_display();
		}
	}

	_connection_lost() {
		console.log("Connection to presentation lost.");
		this._have_connection = false;
		this._ui_update_display();
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
		if (this._session_id != data.session_id) {
			/* Other presentation window open, ignore data. */
			//console.log("Warning: Conflicting presentation session detected.");
			return;
		}

		this._reset_timeout();
		if (data.type == "slide_info") {
			const update_ui = this._current_slide != data.data.current_slide;
			const slide_change = (this._current_slide != null) && update_ui;
			this._current_slide = data.data.current_slide;
			if (slide_change) {
				this.start_timer_if_armed();
				this._recompute_dynamic_timer();
			}
			if (update_ui) {
				this._ui_update_display();
			}
		} else if (data.type == "start_presentation") {
			this.start_timer_if_armed();
		} else if (data.type == "presentation_meta") {
			if (this._meta == null) {
				this._meta = data.data;
				this._update_meta();
			}
		}
	}

	_create_timer_object(is_dynamic_timer = false) {
		let timer_object = {
			presentation_start: new Date(),
		};
		if (!is_dynamic_timer) {
			timer_object.presentation_end = TimeTools.parse_timestamp(this._ui_elements.presentation_end_time.value).compute(this._nominal_presentation_duration_secs);
			timer_object.slide_subset = this._slide_subset_selector.parse(this._ui_elements.slide_subset.value, (this._meta == null) ? null : this._meta.slide_count);
		} else {
			timer_object.presentation_end = this._active_timer.presentation_end;
			timer_object.slide_subset = new SlideSubset((this._current_slide <= this._active_timer.slide_subset.end_slide) ? this._current_slide : this._active_timer.slide_subset.end_slide, this._active_timer.slide_subset.end_slide);
		}
		timer_object.presentation_duration_secs = (timer_object.presentation_end.getTime() - timer_object.presentation_start.getTime()) / 1000;
		timer_object.subset_ratio = this._slide_subset_selector.get_ratio_of_subset(timer_object.slide_subset);
		return timer_object;
	}

	_recompute_dynamic_timer() {
		this._dynamic_timer = this._create_timer_object(true);
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

	start_timer() {
		if (this._timer_mode == TimerMode.STARTED) {
			return;
		}

		console.log("Start timer.");
		this._timer_mode = TimerMode.STARTED;
		this._active_timer = this._create_timer_object();
		this._dynamic_timer = this._active_timer;
		this._ui_update_everything();
	}

	stop_timer() {
		console.log("Stop timer.");
		this._timer_mode = TimerMode.STOPPED;
		this._current_slide = null;
		this._active_timer = null;
		this._dynamic_timer = null;
		this._ui_update_everything();
	}
}
