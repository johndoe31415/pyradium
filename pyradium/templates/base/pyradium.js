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

const CursorStyle = {
	CURSOR_OFF: 0,
	CURSOR_DEFAULT: 1,
	CURSOR_CIRCLE: 2,
	CURSOR_ARROW: 3,
	INVALID: 4,
}

export class Presentation {
	constructor(ui_elements, parameters, presentation_meta) {
		this._ui_elements = ui_elements;
		this._parameters = parameters;
		this._presentation_meta = presentation_meta;
		this._cursor = {
			style:		CursorStyle.CURSOR_OFF,
			size:		0,
			last_uri:	null,
			last_svg:	null,
		};
		this._enumerate_slides();
		this._internal_slide_index = 0;
		this._resize_obs = new ResizeObserver((event) => this.event_resize(event));
		this._resize_obs.observe(this._ui_elements.full_screen_div);
		this._intersect_obs = new IntersectionObserver((event) => this.event_scroll_in_viewport(event), {
			"threshold":	0.75,
		});
		this._ui_elements.slides.forEach((slide) => {
			this._intersect_obs.observe(slide);
		});
		this._session_id = Math.random().toString(36).substr(2);
		this._bc = new BroadcastChannel("presentation");
		this._bc.addEventListener("message", (msg) => this._rx_message(msg));
		this._debugging = false;
		setInterval(() => this._tx_slide_info(), 3000);
	}

	_log(...args) {
		if (this._debugging) {
			console.log(...args);
		}
	}

	get session_id() {
		return this._session_id;
	}

	get presentation_meta() {
		return this._presentation_meta
	}

	get slide_count() {
		return this._ui_elements.slides.length;
	}

	get current_slide() {
		return this._ui_elements.slides[this._internal_slide_index];
	}

	get fullscreen_mode() {
		return document.fullscreenElement != null;
	}

	_tx_start_presentation() {
		const msg = {
			"type":						"start_presentation",
			"session_id":				this._session_id,
		};
		this._bc.postMessage(msg);
	}

	_tx_slide_info() {
		const msg = {
			"type":						"slide_info",
			"session_id":				this._session_id,
			"data": {
				"current_slide":		this.current_slide.getAttribute("slide_no") | 0,
			},
		};
		this._bc.postMessage(msg);
	}

	_tx_presentation_meta() {
		const msg = {
			"type":					"presentation_meta",
			"session_id":			this._session_id,
			"data":					this.presentation_meta,
		};
		this._bc.postMessage(msg);
	}

	_rx_message(msg) {
		const data = msg.data;
		if (data["type"] == "query_slide_info") {
			this._tx_slide_info();
		} else if (data["type"] == "query_presentation_meta") {
			this._tx_presentation_meta();
		}
	}

	_enumerate_slides() {
		this._ui_elements.slides.forEach(function(slide, index) {
			slide.setAttribute("internal_slide_index", index);
		});
	}

	_hide_full_screen_div() {
		this._ui_elements.full_screen_div.style.display = "none";
	}

	_set_scaled_cursor(svg_data, offsetx, offsety) {
		const scale_factor = Math.pow(1.1, this._cursor.size);

		const doc = new DOMParser().parseFromString(svg_data, "application/xml");
		const svg = doc.getElementById("scale_svg");
		svg.setAttribute("width", svg.getAttribute("width") * scale_factor);
		svg.setAttribute("height", svg.getAttribute("height") * scale_factor);

		const layer = doc.getElementById("scale_layer");
		layer.setAttribute("transform", "scale(" + scale_factor + "), " + layer.getAttribute("transform"));

		const scaled_offsetx = (scale_factor * offsetx) | 0;
		const scaled_offsety = (scale_factor * offsety) | 0;
		const cursor_svg = new XMLSerializer().serializeToString(doc);
		this._ui_elements.full_screen_div.style.cursor = "url(\"data:image/svg+xml," + encodeURIComponent(cursor_svg) + "\") " + scaled_offsetx + " " + scaled_offsety + ", auto";
	}

	_load_cursor_svg(uri, offsetx, offsety) {
		if (this._cursor.last_uri != uri) {
			fetch(uri).then((response) => {
				if (response.ok) {
					return response.text();
				}
			}).then((svg_data) => {
				this._cursor.last_uri = uri;
				this._cursor.last_svg = svg_data;
				this._set_scaled_cursor(svg_data, offsetx, offsety);
			});
		} else {
			this._set_scaled_cursor(this._cursor.last_svg, offsetx, offsety);
		}
	}

	_set_cursor_style() {
		switch (this._cursor.style) {
			case CursorStyle.CURSOR_OFF:
				this._ui_elements.full_screen_div.style.cursor = "none";
				break;

			case CursorStyle.CURSOR_DEFAULT:
				this._ui_elements.full_screen_div.style.cursor = "inherit";
				break;

			case CursorStyle.CURSOR_CIRCLE:
				this._load_cursor_svg(this._parameters.preuri + "template/base/cursor_circle.svg", 25, 25);
				break;

			case CursorStyle.CURSOR_ARROW:
				this._load_cursor_svg(this._parameters.preuri + "template/base/cursor_arrow.svg", 0, 0);
				break;
		}
	}

	_prepare_full_screen_div() {
		const size_container = this.current_slide.parentElement;
		const zoom_factor = this._ui_elements.full_screen_div.offsetWidth / this.current_slide.offsetWidth;
		this._ui_elements.full_screen_div.style.display = "";
		this._set_cursor_style()
		this._ui_elements.full_screen_div.innerHTML = size_container.innerHTML;
	}

	start_presentation() {
		this._log("Presentation started.");
		if (this.fullscreen_mode) {
			/* If armed and presentation is duplicate started, this means start
			 * timer. */
			this._tx_start_presentation();
		}
		this._cursor.style = 0;
		this._prepare_full_screen_div();
		this._ui_elements.full_screen_div.requestFullscreen();
	}

	_find_slide(selector) {
		return [].filter.call(this._ui_elements.slides, (slide) => slide.matches(selector));
	}

	_update(scroll_to_slide) {
		if (scroll_to_slide) {
			this.current_slide.scrollIntoView();
			window.scrollBy(0, -100);
		}
		const slide_no = this.current_slide.getAttribute("slide_no") | 0;
		const sub_slide_index = this.current_slide.getAttribute("sub_slide_index") | 0;
		const slide_designator = (sub_slide_index == 0) ? slide_no : (slide_no + "." + (sub_slide_index + 1));
		this._ui_elements.slideno_text.value = slide_designator;
		if (this.fullscreen_mode) {
			this._prepare_full_screen_div();
		}
	}

	_should_capture_event(event) {
		const tag_name = event.target.tagName;
		return (tag_name != "INPUT") && (tag_name != "TEXTAREA");
	}

	event_keypress(event) {
		if (!this._should_capture_event(event)) {
			return;
		}
		if (event.key == "g") {
			this._log("Keypress: 'g' -> goto");
			this.goto_slide();
		} else if (event.key == "f") {
			this._log("Keypress: 'f' -> full screen presentation");
			this.start_presentation();
		} else if (event.key == "c") {
			this._log("Keypress: 'c' -> toggle cursor");
			this.cursor_cycle_type();
		} else if (event.key == "+") {
			this._log("Keypress: '+' -> increase cursor size");
			this.cursor_size_change(1);
		} else if (event.key == "-") {
			this._log("Keypress: '-' -> decrease cursor size");
			this.cursor_size_change(-1);
		} else if ((event.key == "X") && (event.ctrlKey) && (event.shiftKey)) {
			this._debugging = true;
			this._log("Debugging mode enabled.");
		} else if ((event.key == "i") && (event.ctrlKey)) {
			if (this._ui_elements.info_modal != null) {
				this._log("Show info window.");
				this._ui_elements.info_modal.pyradium_modal.show();
			} else {
				this._log("Info window functionality not implemented.");
			}
		} else {
			this._log("Keypress other: ", event);
		}
	}

	event_keydown(event) {
		if (!this._should_capture_event(event)) {
			return;
		}
		if ((event.key == "PageDown") || (event.key == "ArrowDown") || (event.key == "ArrowRight")) {
			this._log("Keydown: 'PageDown' -> next slide");
			this.goto_next_slide();
			event.preventDefault();
		} else if ((event.key == "PageUp") || (event.key == "ArrowUp") || (event.key == "ArrowLeft")) {
			this._log("Keydown: 'PageUp' -> previous slide");
			this.goto_prev_slide();
			event.preventDefault();
		} else if (event.key == "Home") {
			this._log("Keydown: 'Home' -> first slide");
			this.goto_first_slide();
			event.preventDefault();
		} else if (event.key == "End") {
			this._log("Keydown: 'End' -> last slide");
			this.goto_last_slide();
			event.preventDefault();
		} else {
			this._log("Keydown other: ", event);
		}
	}

	event_wheel(event) {
		const scroll_up = event.deltaY < 0;
		if (this.fullscreen_mode) {
			if (scroll_up) {
				this._log("Wheel: 'ScrollUp' -> previous slide");
				this.goto_prev_slide();
			} else {
				this._log("Wheel: 'ScrollDown' -> next slide");
				this.goto_next_slide();
			}
		}
	}

	event_scroll_in_viewport(events) {
		if (this.fullscreen_mode) {
			return;
		}
		events.forEach((event) => {
			if (event.isIntersecting) {
				const slide = event.target;
				const internal_slide_index = slide.getAttribute("internal_slide_index") | 0;
				this._log("Viewport event -> goto index " + internal_slide_index);
				this._goto_slide(internal_slide_index, false);
			}
		});
	}

	event_fullscreen(event) {
		if (!this.fullscreen_mode) {
			this._hide_full_screen_div();
		}
	}

	event_resize(event) {
		if (this.fullscreen_mode) {
			const screen_width = screen.width;
			const screen_height = screen.height;

			const slide_width = this._ui_elements.slides[0].offsetWidth;
			const slide_height = this._ui_elements.slides[0].offsetHeight;
			const zoom_x = screen_width / slide_width;
			const zoom_y = screen_height / slide_height;
			const zoom = (zoom_x < zoom_y) ? zoom_x : zoom_y;

			this._log("Determined full screen to be " + screen_width + " x " + screen_height + ", slides " + slide_width + " x " + slide_height + "; zoom is " + zoom);
			this._ui_elements.full_screen_div.style.zoom = zoom;
		}
	}

	cursor_cycle_type() {
		this._cursor.style += 1;
		if (this._cursor.style == CursorStyle.INVALID) {
			this._cursor.style = 0;
		}
		this._set_cursor_style();
	}

	cursor_size_change(size_increment) {
		const min_cursor_size = -5;
		const max_cursor_size = 9;

		this._cursor.size += size_increment;
		if (this._cursor.size < min_cursor_size) {
			this._cursor.size = min_cursor_size;
		} else if (this._cursor.size > max_cursor_size) {
			this._cursor.size = max_cursor_size;
		}
		this._log("Cursor size now", this._cursor.size);
		this._set_cursor_style();
	}

	goto_slide() {
		const slide_input = window.prompt("Slide number: ");
		const match = slide_input.match(/(?<slide_no>\d+)(\.(?<sub_slide_no>\d+))?/);
		if (match == null) {
			alert("Invalid entry.");
			return;
		}
		const slide_no = match.groups["slide_no"] | 0;
		const sub_slide_index = (match.groups["sub_slide_no"] != null) ? ((match.groups["sub_slide_no"] | 0) - 1) : 0;
		const slide = this._find_slide("[slide_no=\"" + slide_no + "\"][sub_slide_index=\"" + sub_slide_index + "\"]");
		if (slide.length == 0) {
			alert("No such slide.");
			return;
		}

		const internal_slide_index = slide[0].getAttribute("internal_slide_index") | 0;
		this._goto_slide(internal_slide_index, true);
	}

	_goto_slide(slide_index, scroll_to_slide) {
		if ((slide_index >= 0) && (slide_index < this.slide_count) && (slide_index != this._internal_slide_index)) {
			this._internal_slide_index = slide_index;
			this._update(scroll_to_slide);
			if (this.fullscreen_mode) {
				this._tx_slide_info();
			}
		}
	}

	goto_first_slide() {
		this._goto_slide(0, true);
	}

	goto_last_slide() {
		this._goto_slide(this.slide_count - 1, true);
	}

	goto_next_slide() {
		this._goto_slide(this._internal_slide_index + 1, true);
	}

	goto_prev_slide() {
		this._goto_slide(this._internal_slide_index - 1, true);
	}

	toggle_mode() {
		if (this._mode == "stop") {
			this.start();
		} else {
			this.stop();
		}
	}

	_pause_tick(parameters) {
		const now_secs = new Date().getTime() / 1000;
		const expiry_secs = parameters.pause_start_secs + parameters.pause_duration_secs;
		const remaining_secs = expiry_secs - now_secs;
		parameters.pause_remaining_span.innerText = TimeTools.format_ms(remaining_secs);

		parameters.pause_remaining_span.classList.remove("plenty");
		parameters.pause_remaining_span.classList.remove("little");
		parameters.pause_remaining_span.classList.remove("none");
		if (remaining_secs >= 3 * 60) {
			parameters.pause_remaining_span.classList.add("plenty");
		} else if (remaining_secs >= 0) {
			parameters.pause_remaining_span.classList.add("little");
		} else {
			parameters.pause_remaining_span.classList.add("none");
		}

		if ((!parameters.expired) && (remaining_secs < 0)) {
			/* Expired now! */
			parameters.expired = true;
			new Audio(this._parameters.preuri + "template/base/presentation_pause_end.mp3").play();
		}
	}

	pause() {
		/** @type {HTMLDialogElement} */
		const modal = this._ui_elements.pause_modal;
		if (modal.open) {
			return;
		}

		const pause_duration_mins = window.prompt("Pause duration (minutes): ", "15");
		if (pause_duration_mins <= 0) {
			return;
		}

		let pause_parameters = {
			"pause_duration_secs":		pause_duration_mins * 60,
			"pause_start_secs":			new Date().getTime() / 1000,
			"pause_remaining_span":		modal.querySelector("#pause_remaining"),
			"expired":					false,
		}

		modal.querySelector("#pause_duration").innerText = pause_duration_mins;

		const pause_until = new Date((pause_parameters.pause_start_secs + pause_parameters.pause_duration_secs) * 1000);
		modal.querySelector("#pause_until").innerText = TimeTools.format_datetime(pause_until).hms

		this._pause_tick(pause_parameters);
		const interval_id = setInterval(() => this._pause_tick(pause_parameters), 1000);

		modal.addEventListener("close", () => clearInterval(interval_id));
		modal.showModal();
	}
}
