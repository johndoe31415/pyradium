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
import urllib.parse
try:
	import aiohttp.web
except ModuleNotFoundError:
	aiohttp = None
import asyncio
from pyradium.Presentation import Presentation
from pyradium.Tools import XMLTools
from pyradium.CircuitJS import CircuitJSCircuit
from pyradium.CmdlineEscape import CmdlineEscape
from .BaseModifyCommand import BaseModifyCommand

_log = logging.getLogger(__spec__.name)
_empty_circuit_urlcomponent = "CQAgjCAMB0l3BWcMBMcUHYMGZIA4UA2ATmIxAUgpABZsKBTAWjDACgg"

@BaseModifyCommand.register
class CircuitJSRenderImages(BaseModifyCommand):
	_NAME = "circuitjs"
	_DESCRIPTION = "Render CircuitJS circuits"
	_VISIBLE = (aiohttp is not None)

	@classmethod
	def _gen_parser(cls, parser):
		parser.add_argument("-u", "--circuitjs-uri", metavar = "uri", default = "http://127.0.0.1:8123/circuitws.html", help = "URI that the websocket CircuitJS is hosted at. Defaults to %(default)s.")
		parser.add_argument("--websocket-port", metavar = "port", type = int, default = 3424, help = "Run websocket server on localhost at this port. Defaults to %(default)d.")
		parser.add_argument("-c", "--capture-circuit", action = "store_true", help = "Not only capture the SVG files, but also the circuits itself.")
		parser.add_argument("-t", "--settle-time", metavar = "secs", type = float, default = 1.0, help = "Simulate circuit for this duration before capturing it (defaults to %(default).1f seconds).")
		parser.add_argument("--no-xdg-open", action = "store_true", help = "Do not call xdg-open automatically to start the process.")
		parser.add_argument("--no-svg-postprocessing", action = "store_true", help = "Do not call Inkscape to adapt the returned SVG canvas size.")
		parser.add_argument("--no-shutdown", action = "store_true", help = "Keep CircuitJS running after everything is rendered; do not cause it to shut down.")
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

		async def tx_rx(msg, expect_response = True):
			self._msgid += 1
			used_msgid = self._msgid
			msg["msgid"] = used_msgid
			_log.trace("Sending: %s", msg)
			await ws.send_json(msg)
			while expect_response:
				answer = await ws.receive_json()
				if ("msgid" in answer) and (answer["msgid"] == used_msgid):
					_log.trace("Response: %s", answer)
					return answer
				else:
					_log.trace("Response with different/no message ID: %s", answer)



		# Wait for connection to become available; otherwise, reloading too
		# soon has no effect.
		await tx_rx({ "cmd": "wait_available" })

		# TODO: This is not a pretty hack. But apparently the JS portion is
		# not fully ready even when it shows it's ready at startup.
		await asyncio.sleep(0.5)

		try:
			circuit_params = None
			for (cno, circuit) in enumerate(self._circuits, 1):
				_log.debug("Processing circuit %d of %d: %s", cno, len(self._circuits), circuit.get_presentation_parameter("name"))
				if circuit.circuit_params() != circuit_params:
					circuit_params = circuit.circuit_params()
					circuit_params["ctz"] = _empty_circuit_urlcomponent
					_log.debug("Circuit parameters changed, forcing reload of circuit simulator")
					await tx_rx({ "cmd": "reload", "args": circuit_params })

					# Wait for the simulator to become available again
					await tx_rx({ "cmd": "wait_available" })

					# TODO: This is not a pretty hack. But apparently the JS portion is
					# not fully ready even when it shows it's ready at startup.
					await asyncio.sleep(0.5)

				# Load circuit
				await tx_rx({ "cmd": "circuit_import", "circuit": circuit.circuit_text })

				# Wait for simulation to settle
				# TODO actually determine simulation time
				t0 = await tx_rx({ "cmd": "status" })
				await asyncio.sleep(self._args.settle_time)
				t1 = await tx_rx({ "cmd": "status" })

				# Then make a snapshot of the SVG
				svg = await tx_rx({ "cmd": "get_svg" })

				# Create the output SVG file
				output_filename_svg = f"{self._args.output_dir}/circuit_{circuit.get_presentation_parameter('name')}.svg"
				with open(output_filename_svg, "w") as f:
					f.write(svg["data"])

				# Postprocess the SVG file
				if not self._args.no_svg_postprocessing:
					cmd = [ "inkscape", "-g", "--verb=FitCanvasToDrawing;FileSave;FileQuit", output_filename_svg ]
					_log.debug("Fitting SVG to canvas: %s", CmdlineEscape().cmdline(cmd))
					subprocess.check_call(cmd, stdout = _log.subproc_target, stderr = _log.subproc_target)

				if self._args.capture_circuit:
					# The circuit may have modified after it's settled. Retrieve it if user requests it.
					exported_circuit = await tx_rx({ "cmd": "circuit_export" })
					output_filename_circuit = f"{self._args.output_dir}/circuit_{circuit.get_presentation_parameter('name')}.txt"
					with open(output_filename_circuit, "w") as f:
						f.write(exported_circuit["data"])


		finally:
			if not self._args.no_shutdown:
				# Shutdown the simulator
				_log.debug("Shutting down the simulator")
				await tx_rx({ "cmd": "shutdown" }, expect_response = False)
		raise aiohttp.web_runner.GracefulExit()


	def _parse_circuits(self):
		circuits = [ ]
		(dom, presentation) = Presentation.parse_xml(self._args.infile)
		for slide in XMLTools.findall(presentation, "slide"):
			for circuit_node in XMLTools.findall(slide, "s:circuit"):
				circuit = CircuitJSCircuit.from_xml(circuit_node)
				if circuit.has_presentation_parameter("name"):
					circuits.append(circuit)
				else:
					_log.warning("Unnamed circuit will not be rendered to SVG.")
		return circuits

	def run(self):
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
		return 0
