#	pybeamer - HTML presentation/slide show generator
#	Copyright (C) 2021-2021 Johannes Bauer
#
#	This file is part of pybeamer.
#
#	pybeamer is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pybeamer is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pybeamer; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import os
import contextlib
import hashlib
import json
import datetime
import base64
import collections

RenderedResult = collections.namedtuple("RenderedResult", [ "key", "keyhash", "from_cache", "data" ])

class BytesEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			return {
				"__internal_object__":	"6bbc5f9e-6aba-40f4-878c-1ce5f5f50055",
				"data":					base64.b64encode(obj).decode("ascii"),
			}
		return json.JSONEncoder.default(self, obj)

	@classmethod
	def load_object_hook(cls, obj):
		if isinstance(obj, dict) and ("__internal_object__" in obj):
			uuid = obj["__internal_object__"]
			if uuid == "6bbc5f9e-6aba-40f4-878c-1ce5f5f50055":
				# Uncompressed base64 bytes
				return base64.b64decode(obj["data"])
			else:
				raise Exception("Unable to decode special cached object with UUID %s." % (uuid))
		else:
			return obj

class BaseRenderer():
	@property
	def name(self):
		raise NotImplementedError(__class__.__name__)

	@property
	def properties(self):
		return { "version": 0 }

	def render(self, property_dict):
		raise NotImplementedError(__class__.__name__)

class RendererCache():
	def __init__(self, renderer):
		self._renderer = renderer
		self._directory = os.path.expanduser("~/.cache/pybeamer/" + self._renderer.name + "/")
		with contextlib.suppress(FileExistsError):
			os.makedirs(self._directory)

	@staticmethod
	def _hash_key(key):
		binkey = json.dumps(key, separators = (",", ":"), sort_keys = True).encode("utf-8")
		keyhash = hashlib.md5(binkey).hexdigest()
		return keyhash

	def _retrieve(self, keyhash):
		filename = self._directory + keyhash + ".json"
		try:
			with open(filename) as f:
				file_representation = json.load(f, object_hook = BytesEncoder.load_object_hook)
		except (FileNotFoundError, json.decoder.JSONDecodeError):
			return None

		return RenderedResult(key = file_representation["key"], keyhash = keyhash, from_cache = True, data = file_representation["object"])

	def _store(self, key, keyhash, object_data):
		file_representation = {
			"key":		key,
			"meta": {
				"rendered":	datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
				"keyhash":	keyhash,
				"objtype":	"bytes" if isinstance(object_data, bytes) else "plain",
			},
		}
		if isinstance(object_data, bytes):
			file_representation["object"] = "AAAA=="
		else:
			file_representation["object"] = object_data

		filename = self._directory + keyhash + ".json"
		with open(filename, "w") as f:
			json.dump(file_representation, f, separators = (",", ":"), cls = BytesEncoder)

	def render(self, property_dict):
		key = {
			"name":						self._renderer.name,
			"renderer_properties":		self._renderer.properties,
			"object_properties":		property_dict,
		}
		keyhash = self._hash_key(key)
		cached_object = self._retrieve(keyhash)
		if cached_object is not None:
			return cached_object
		else:
			object_data = self._renderer.render(property_dict)
			self._store(key, keyhash, object_data)
			return RenderedResult(key = key, keyhash = keyhash, from_cache = False, data = object_data)

if __name__ == "__main__":
	class LetterRenderer(BaseRenderer):
		@property
		def name(self):
			return "letter"

		@property
		def properties(self):
			return { "version": 1 }

		def render(self, property_dict):
			return {
				"text":		property_dict["letter"] * property_dict["count"],
				"data":		b"foobar",
			}

	cache = RendererCache(LetterRenderer())
	print("Result = ", cache.render({
		"letter":	"Q",
		"count":	10,
	}))
