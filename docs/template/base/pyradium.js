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

const CursorStyle = {
	CURSOR_OFF: 0,
	CURSOR_DEFAULT: 1,
	CURSOR_HIGHLIGHT: 2,
	INVALID: 3,
}

export class Presentation {
	constructor(ui_elements, presentation_meta) {
		this._ui_elements = ui_elements;
		this._presentation_meta = presentation_meta;
		this._cursor_style = CursorStyle.CURSOR_OFF;
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

	_set_cursor_style() {
		switch (this._cursor_style) {
			case CursorStyle.CURSOR_OFF:
				this._ui_elements.full_screen_div.style.cursor = "none";
				break;

			case CursorStyle.CURSOR_DEFAULT:
				this._ui_elements.full_screen_div.style.cursor = "inherit";
				break;

			case CursorStyle.CURSOR_HIGHLIGHT:
				this._ui_elements.full_screen_div.style.cursor = "url('template/base/cursor.svg'), auto";
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
		this._cursor_style = 0;
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
			this.toggle_cursor();
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
		if (event.key == "PageDown") {
			this._log("Keydown: 'PageDown' -> next slide");
			this.goto_next_slide();
			event.preventDefault();
		} else if (event.key == "PageUp") {
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

	toggle_cursor() {
		this._cursor_style += 1;
		if (this._cursor_style == CursorStyle.INVALID) {
			this._cursor_style = 0;
		}
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
}
