export class Presentation {
	constructor() {
		this._mode = "stop";
		this._slideno = 1;
	}

	start() {
		this._mode = "run";
		console.log("Presentation started.");
	}

	stop() {
		this._mode = "stop";
		console.log("Presentation stopped.");
	}

	next_slide() {
	}

	prev_slide() {
	}

	toggle_mode() {
		if (this._mode == "stop") {
			this.start();
		} else {
			this.stop();
		}
	}
}
