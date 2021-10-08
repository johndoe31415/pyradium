#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2021 Johannes Bauer
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

import json
import enum
import zlib
import base64

class ExtendedJSONObjects(enum.Enum):
	UncompressedBytes = "6bbc5f9e-6aba-40f4-878c-1ce5f5f50055"
	ZLibCompressedBytes = "f12d83b4-b2dd-4968-8f14-e063970c66fd"

class ExtendedJSONEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, bytes):
			if len(obj) > 1000:
				# Try to compress first
				compressed = zlib.compress(obj)

				# Evaluate if it was worth it
				saved_size_bytes = len(obj) - len(compressed)
				saved_size_percent = 100 * saved_size_bytes / len(obj)

			if (len(obj) <= 1000) or (saved_size_bytes < 1000) or (saved_size_percent < 1):
				# Save raw, not worth it.
				return {
					"__internal_object__":	ExtendedJSONObjects.UncompressedBytes.value,
					"data":					base64.b64encode(obj).decode("ascii"),
				}
			else:
				# Save zlib compressed
				return {
					"__internal_object__":	ExtendedJSONObjects.ZLibCompressedBytes.value,
					"data":					base64.b64encode(compressed).decode("ascii"),
				}
		return json.JSONEncoder.default(self, obj)

	@classmethod
	def _load_object_hook(cls, obj):
		if isinstance(obj, dict) and ("__internal_object__" in obj):
			uuid = obj["__internal_object__"]
			obj_type = ExtendedJSONObjects(uuid)
			if obj_type == ExtendedJSONObjects.UncompressedBytes:
				return base64.b64decode(obj["data"])
			elif obj_type == ExtendedJSONObjects.ZLibCompressedBytes:
				return zlib.decompress(base64.b64decode(obj["data"]))
			else:
				raise NotImplementedError(obj_type)
		else:
			return obj

	@classmethod
	def dumps(cls, obj, minify = False, sort_keys = False, indent = None):
		separators = (",", ":") if minify else None
		return json.dumps(obj, cls = cls, separators = separators, sort_keys = sort_keys, indent = indent)

	@classmethod
	def dump(cls, obj, f, minify = False, sort_keys = False, indent = None):
		separators = (",", ":") if minify else None
		return json.dump(obj, f, cls = cls, separators = separators, sort_keys = sort_keys, indent = indent)

	@classmethod
	def load(cls, f):
		return json.load(f, object_hook = cls._load_object_hook)
