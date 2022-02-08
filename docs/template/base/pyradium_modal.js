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

export class ModalWindow {
	constructor(modal_div, options) {
		this._modal_div = modal_div;
		this._msg_div = modal_div.querySelector("div.msg");
		this._options = options || { };
		if (this._options.close_on_popup_click) {
			this._modal_div.addEventListener("click", (event) => this.close());
		} else {
			this._modal_div.querySelector("span.close").addEventListener("click", (event) => this.close());
		}
	}

	close() {
		this._modal_div.classList.remove("active");
	}

	show(modal_type, message) {
		this._modal_div.classList.remove("type-error");
		this._modal_div.classList.remove("type-success");
		this._modal_div.classList.add("type-" + modal_type);
		if (message != null) {
			this._msg_div.innerHTML = message;
		}
		this._modal_div.classList.add("active");
	}
}
