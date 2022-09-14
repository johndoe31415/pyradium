#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2022 Johannes Bauer
#
#	This file is part of pyradium.
#
#	pyradium is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pyradium is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pyradium; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import subprocess
import logging
import os
import contextlib
import enum
import shutil
import urllib.parse
try:
	import aiohttp.web
except ModuleNotFoundError:
	aiohttp = None
import asyncio
from pyradium.Presentation import Presentation
from pyradium.Tools import XMLTools, FileTools
from pyradium.CircuitJS import CircuitJSCircuit
from pyradium.CmdlineEscape import CmdlineEscape
from pyradium.FileLookup import FileLookup
from .BaseModifyCommand import BaseModifyCommand

_log = logging.getLogger(__spec__.name)
_empty_circuit_urlcomponent = "CQAgjCAMB0l3BWcMBMcUHYMGZIA4UA2ATmIxAUgpABZsKBTAWjDACgg"

class _WriteBack(enum.Enum):
	NoWriteback = "no"
	Inline = "inline"
	ExternalFile = "extfile"

@BaseModifyCommand.register
class CircuitJSRenderImages(BaseModifyCommand):
	_NAME = "circuitjs"
	_DESCRIPTION = "Render CircuitJS circuits"
	_VISIBLE = (aiohttp is not None)

	@classmethod
	def _gen_parser(cls, parser):
		parser.add_argument("-I", "--include-dir", metavar = "path", action = "append", default = [ ], help = "Specifies an additional include directory in which, for example, circuits are located which are referenced from the presentation. Can be issued multiple times.")
		parser.add_argument("-u", "--circuitjs-uri", metavar = "uri", default = "http://127.0.0.1:8123/circuitws.html", help = "URI that the websocket CircuitJS is hosted at. Defaults to %(default)s.")
		parser.add_argument("--websocket-port", metavar = "port", type = int, default = 3424, help = "Run websocket server on localhost at this port. Defaults to %(default)d.")
		parser.add_argument("-c", "--capture-circuit", action = "store_true", help = "Not only capture the SVG files, but also the circuits itself.")
		parser.add_argument("-t", "--settle-time", metavar = "secs", type = float, default = 1.0, help = "Simulate circuit for this duration before capturing it (defaults to %(default).1f seconds).")
		parser.add_argument("--no-xdg-open", action = "store_true", help = "Do not call xdg-open automatically to start the process.")
		parser.add_argument("--no-svg-postprocessing", action = "store_true", help = "Do not call Inkscape to adapt the returned SVG canvas size.")
		parser.add_argument("--no-shutdown", action = "store_true", help = "Keep CircuitJS running after everything is rendered; do not cause it to shut down.")
		parser.add_argument("--only-circuit", metavar = "name", action = "append", default = [ ], help = "Only process circuits with the given name. Can be specified multiple times. If not specified, all circuits are affected.")
		parser.add_argument("-w", "--write-back", metavar = "{" + ",".join(choice.value for choice in _WriteBack) + "}", choices = _WriteBack, type = _WriteBack, default = "no", help = "This option not only reads out the circuit after it has settled, but it also writes those changes back to the XML presentation file. This can either happen inline (directly as text) or as an external file reference.")
		parser.add_argument("-s", "--simulation-change", choices = [ "reset_params" ], action = "append", default = [ ], help = "Manipulate the circuit in a defined way. Right now there is only 'reset_params' supported, which resets timestep/simulation speed to the initial defaults. Can be supplied multiple times.")
		parser.add_argument("-o", "--output-dir", metavar = "path", default = "circuits/", help = "Output directory to store the circuit SVGs into.")
		parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increases verbosity. Can be specified multiple times to increase.")
		parser.add_argument("infile", help = "Input XML file of the presentation.")

	async def _on_startup(self, app):
		if not self._args.no_xdg_open:
			self._subproc = subprocess.Popen([ "xdg-open", self._target_uri ], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

	async def _websocket_handler(self, request):
		if self._connection:
			return
		self._connection = True

		_log.debug("Websocket client connected from %s: %s", request.remote, request)
		ws = aiohttp.web.WebSocketResponse()
		await ws.prepare(request)

		async def tx_rx(msg, expect_response = True, wait_for_event = None):
			self._msgid += 1
			used_msgid = self._msgid
			msg["msgid"] = used_msgid
			_log.trace("Sending: %s", msg)
			await ws.send_json(msg)
			while expect_response:
				answer = await ws.receive_json()
				if (wait_for_event is None) and ("msgid" in answer) and (answer["msgid"] == used_msgid):
					_log.trace("Response: %s", answer)
					return answer
				if (wait_for_event is not None) and (answer["type"] == "event") and (answer["code"] == wait_for_event):
					_log.trace("Response event: %s", answer)
					return answer
				else:
					_log.trace("Response with different/no message ID: %s", answer)



		# We do not know if the simulator is available yet. Test it out
		status = await tx_rx({ "cmd": "status" })
		if status["status"] == "error":
			# Initially, simulator is not available yet. Wait for it to become available.
			while True:
				answer = await ws.receive_json()
				if (answer["type"] == "event") and (answer["code"] == "reload_complete"):
					break

		try:
			circuit_params = None
			for (cno, circuit) in enumerate(self._circuits, 1):
				_log.info("Processing circuit %d of %d: %s", cno, len(self._circuits), circuit.get_presentation_parameter("name"))
				if circuit.circuit_params() != circuit_params:
					# TODO: Disregard "ctz" here.
					circuit_params = circuit.circuit_params()
					circuit_params["ctz"] = _empty_circuit_urlcomponent
					_log.debug("Circuit parameters changed, forcing reload of circuit simulator")
					await tx_rx({ "cmd": "reload", "args": circuit_params }, wait_for_event = "reload_complete")

				# Load circuit
				await tx_rx({ "cmd": "circuit_import", "circuit": circuit.circuit_text })

				# Wait for simulation to settle
				# TODO actually determine simulation time
				t0 = await tx_rx({ "cmd": "status" })
				await asyncio.sleep(self._args.settle_time)
				t1 = await tx_rx({ "cmd": "status" })

				# Then make a snapshot of the SVG
				svg = await tx_rx({ "cmd": "get_svg" }, wait_for_event = "svg_rendered")

				# Create the output SVG file
				output_filename_svg = f"{self._args.output_dir}/circuit_{circuit.get_presentation_parameter('name')}.svg"
				with open(output_filename_svg, "w") as f:
					f.write(svg["data"])

				# Postprocess the SVG file
				if not self._args.no_svg_postprocessing:
					cmd = [ "inkscape", "-g", "--verb=FitCanvasToDrawing;FileSave;FileQuit", output_filename_svg ]
					_log.debug("Fitting SVG to canvas: %s", CmdlineEscape().cmdline(cmd))
					subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)

				if self._args.capture_circuit or (self._args.write_back != _WriteBack.NoWriteback):
					# The circuit may have modified after it's settled. Retrieve it if user requests it.
					exported_circuit = await tx_rx({ "cmd": "circuit_export" })
					circuit.circuit_text = exported_circuit["data"]
					for change in self._args.simulation_change:
						if change == "reset_params":
							circuit.reset_presentation_parameters()
						else:
							raise NotImplementedError(change)

					if self._args.capture_circuit or (self._args.write_back == _WriteBack.ExternalFile):
						local_filename_circuit = circuit.automatic_filename
						output_filename_circuit = f"{self._args.output_dir}/{local_filename_circuit}"
						with open(output_filename_circuit, "w") as f:
							f.write(circuit.circuit_text)

					# Modify the presentation DOM
					if self._args.write_back == _WriteBack.Inline:
						self._dom_modified = circuit.modify_dom_source_inline() or self._dom_modified
					elif self._args.write_back == _WriteBack.ExternalFile:
						self._dom_modified = circuit.modify_dom_source_external_file("*") or self._dom_modified

		finally:
			if not self._args.no_shutdown:
				# Shutdown the simulator
				_log.debug("Shutting down the simulator")
				await tx_rx({ "cmd": "shutdown" }, expect_response = False)
		raise aiohttp.web_runner.GracefulExit()


	def _parse_circuits(self):
		circuits = [ ]
		(self._dom, presentation) = Presentation.parse_xml(self._args.infile)
		for slide in XMLTools.findall(presentation, "slide"):
			for circuit_node in XMLTools.findall(slide, "s:circuit"):
				circuit = CircuitJSCircuit.from_xml(circuit_node, find_file_function = self._lookup.lookup)
				name = circuit.get_presentation_parameter("name")
				if name is not None:
					if (len(self._args.only_circuit) == 0) or (name in self._args.only_circuit):
						circuits.append(circuit)
				else:
					_log.warning("Unnamed circuit will not be considered.")
		return circuits

	def run(self):
		self._lookup = FileLookup(self._args.include_dir)
		self._dom_modified = False
		self._connection = False
		self._msgid = 0
		self._circuits = self._parse_circuits()
		if len(self._circuits) == 0:
			_log.warning("No circuits found in presentation, nothing to do.")
			return 1

		with contextlib.suppress(FileExistsError):
			os.makedirs(self._args.output_dir)

		local_hostname = "127.0.0.1"
		local_uri = f"ws://{local_hostname}:{self._args.websocket_port}/ws"
		initial_config_args = {
			"ctz":	_empty_circuit_urlcomponent,
		}
		query = {
			"ws":			local_uri,
			"src":			f"circuitjs.html?{urllib.parse.urlencode(initial_config_args)}",
			"autoshutoff":	"1",
		}
		self._target_uri = f"{self._args.circuitjs_uri}?{urllib.parse.urlencode(query)}"
		if self._args.no_xdg_open:
			print(f"Point your browser to: {self._target_uri}")

		self._app = aiohttp.web.Application()
		self._app.on_startup.append(self._on_startup)

		self._app.router.add_route("GET", "/ws", self._websocket_handler)
		aiohttp.web.run_app(self._app, host = local_hostname, port = self._args.websocket_port)

		if self._dom_modified:
			rnd_filename = FileTools.base_random_file_on(self._args.infile)
			_log.debug("Writing modified presentation XML using tempfile %s", rnd_filename)
			with open(rnd_filename, "w") as f:
				self._dom.writexml(f)
			shutil.move(rnd_filename, self._args.infile)
		else:
			_log.debug("Presentation has not changed, not saving.")
		return 0
