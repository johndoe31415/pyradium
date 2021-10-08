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

export class FeedbackSender {
	constructor(target_uri, options) {
		this._target_uri = target_uri;
		this._options = options;
		this._sources = [ ];
		this._buttons = [ ];
	}

	add_source(element) {
		this._sources.push(element);
	}

	add_button(element) {
		element.addEventListener("click", (event) => this.submit());
		this._buttons.push(element);
	}

	_collect_data() {
		let collected_data = { };
		this._sources.forEach((source) => {
			collected_data[source.name] = source.value;
		});
		return collected_data;
	}

	_data_is_empty(data_source) {
		for (const value of Object.values(data_source)) {
			if ((value != null) && (value != "")) {
				return false;
			}
		}
		return true;
	}

	_fire_handler(name, text) {
		const handler = this._options["on_" + name] || console.log;
		handler(text);
	}

	clear_form() {
		this._sources.forEach((source) => {
			source.value = "";
		});
	}

	_set_form_elements(disabled) {
		this._sources.forEach((source) => {
			source.disabled = disabled;
		});
		this._buttons.forEach((button) => {
			button.disabled = disabled;
		});
	}

	disable_form_elements() {
		this._set_form_elements(true);
		this._buttons.forEach((button) => {
			button.classList.add("loading");
		});
	}

	enable_form_elements() {
		this._set_form_elements(false);
		this._buttons.forEach((button) => {
			button.classList.remove("loading");
		});
	}

	submit() {
		this.disable_form_elements();

		const collected = this._collect_data();
		const is_empty = this._data_is_empty(collected);
		if (is_empty) {
			this._fire_handler("form_empty", "Form contains no data for submission.");
			this.enable_form_elements();
			return;
		}

		const post_data = {
			"static_info":	this._options["static_info"],
			"collected":	collected,
		};

		fetch(this._target_uri, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(post_data),
		}).then((response) => {
	        if (response.ok) {
				this._fire_handler("success", "Submission successful.");
			} else {
				this._fire_handler("error", "Server returned HTTP " + response.status + " error during submission.");
			}
		}).catch((error) => {
			this._fire_handler("error", "Network error during submission.");
		}).finally(() => {
			this.enable_form_elements();
		});
	}
}
