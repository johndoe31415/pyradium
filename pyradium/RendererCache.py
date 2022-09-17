#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2021-2022 Johannes Bauer
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

import os
import contextlib
import hashlib
import datetime
import collections
import json
from .ExtendedJSONEncoder import ExtendedJSONEncoder

RenderedResult = collections.namedtuple("RenderedResult", [ "key", "keyhash", "from_cache", "data" ])

class RendererCache():
	def __init__(self, renderer):
		self._renderer = renderer
		self._directory = os.path.expanduser("~/.cache/pyradium/" + self._renderer.name + "/")
		with contextlib.suppress(FileExistsError):
			os.makedirs(self._directory)

	@staticmethod
	def _hash_key(key):
		binkey = ExtendedJSONEncoder.dumps(key, minify = True, sort_keys = True).encode("utf-8")
		keyhash = hashlib.md5(binkey).hexdigest()
		return keyhash

	def _retrieve(self, keyhash):
		filename = self._directory + keyhash + ".json"
		try:
			with open(filename) as f:
				file_representation = ExtendedJSONEncoder.load(f)
		except (FileNotFoundError, json.decoder.JSONDecodeError):
			return None

		return RenderedResult(key = file_representation["key"], keyhash = keyhash, from_cache = True, data = file_representation["object"])

	def _store(self, key, keyhash, object_data):
		file_representation = {
			"key":		key,
			"meta": {
				"rendered":	datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
				"keyhash":	keyhash,
			},
			"object": object_data,
		}

		filename = self._directory + keyhash + ".json"
		with open(filename, "w") as f:
			ExtendedJSONEncoder.dump(file_representation, f, minify = True)

	def render(self, property_dict):
		key = {
			"name":						self._renderer.name,
			"renderer_properties":		self._renderer.properties,
			"object_properties":		property_dict,
			"additional_key":			self._renderer.rendering_key(property_dict),
		}
		attempt_cache = property_dict.get("cache", True)

		keyhash = self._hash_key(key)
		cached_object = self._retrieve(keyhash)
		if attempt_cache and (cached_object is not None):
			return cached_object
		else:
			object_data = self._renderer.render(property_dict)
			if attempt_cache:
				self._store(key, keyhash, object_data)
			return RenderedResult(key = key, keyhash = keyhash, from_cache = False, data = object_data)
