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

export class ButtonCheckbox {
	constructor(button_checkbox_group) {
		this._button_checkbox_group = button_checkbox_group;
		this._button_checkbox_group.querySelectorAll("input").forEach((element) => {
			element.addEventListener("change", (event) => this._button_event(event));
			element.checked = false;
		});
		this._value = null;
		this._disabled = false;
	}

	get name() {
		return this._button_checkbox_group.getAttribute("name");
	}

	get value() {
		return this._value;
	}

	set value(value) {
		let any_checked = false;
		this._value = value;
		this._button_checkbox_group.querySelectorAll("input").forEach((element) => {
			element.checked = (element.value == this._value);
			if (element.checked) {
				any_checked = true;
			}
		});
		if (!any_checked) {
			this._value = null;
		}
	}

	get disabled() {
		return this._disabled;
	}

	set disabled(value) {
		this._disabled = !!value;
		this._button_checkbox_group.querySelectorAll("input").forEach((element) => {
			element.disabled = value;
		});
	}

	_disable_others() {
		this._button_checkbox_group.querySelectorAll("input").forEach((element) => {
			if (element.value != this._value) {
				element.checked = false;
			}
		});
	}

	_button_event(event) {
		const element = event.srcElement;
		if (element.checked) {
			/* Enable element */
			this._value = element.value;
			this._disable_others();
		} else {
			/* Disable element */
			if (this._value == element.value) {
				this._value = null;
			}
		}
	}
}
