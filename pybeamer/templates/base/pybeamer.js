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

export class Presentation {
	constructor(ui_elements) {
		this._ui_elements = ui_elements;
		this._enumerate_slides();
		this._internal_slide_index = 0;
	}

	get slide_count() {
		return this._ui_elements.slides.length;
	}

	get current_slide() {
		return this._ui_elements.slides[this._internal_slide_index];
	}

	get presentation_mode() {
		return document.fullscreenElement != null;
	}

	_enumerate_slides() {
		this._ui_elements.slides.forEach(function(slide, index) {
			slide.setAttribute("internal_slide_index", index);
		});
	}

	_prepare_full_screen_div() {
		const size_container = this.current_slide.parentElement;
		this._ui_elements.full_screen_div.innerHTML = size_container.innerHTML;
	}

	start() {
		console.log("Presentation started.");
		this._prepare_full_screen_div();
		this._ui_elements.full_screen_div.requestFullscreen();
	}

	_find_slide(selector) {
		return [].filter.call(this._ui_elements.slides, (slide) => slide.matches(selector));
	}

	_update() {
		this.current_slide.scrollIntoView();
		const slide_no = this.current_slide.getAttribute("slide_no") | 0;
		const sub_slide_index = this.current_slide.getAttribute("sub_slide_index") | 0;
		if (sub_slide_index == 0) {
			this._ui_elements.slide;
		}
		if (this.presentation_mode) {
			this._prepare_full_screen_div();
		}
	}

	event_keypress(event) {
		if (event.key == "g") {
			this.goto_slide();
		} else {
			console.log(event);
		}
	}

	event_wheel(event) {
		const scroll_up = event.deltaY > 0;
		if (this.presentation_mode) {
			if (scroll_up) {
				this.next_slide();
			} else {
				this.prev_slide();
			}
		}
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
		this._goto_slide(internal_slide_index);

	}

	_goto_slide(slide_index) {
		if ((slide_index >= 0) && (slide_index < this.slide_count) && (slide_index != this._internal_slide_index)) {
			this._internal_slide_index = slide_index;
			this._update();
		}
	}

	next_slide() {
		this._goto_slide(this._internal_slide_index + 1);
	}

	prev_slide() {
		this._goto_slide(this._internal_slide_index - 1);
	}

	toggle_mode() {
		if (this._mode == "stop") {
			this.start();
		} else {
			this.stop();
		}
	}
}
