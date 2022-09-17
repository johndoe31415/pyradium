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

import collections
from pyradium.RendererCache import RendererCache
from pyradium.Exceptions import RendererRegistryException

class BaseRenderer():
	RendererResult = collections.namedtuple("RendererResult", [ "key", "data" ])
	_NAME = None
	_CACHE = True
	_RENDERER_CLASSES = { }
	_RENDERER_INSTANCES = { }

	@property
	def name(self):
		if self._NAME is None:
			raise NotImplementedError(__class__.__name__)
		return self._NAME

	@property
	def properties(self):
		return { "version": 0 }

	def rendering_key(self, property_dict):
		return None

	def render(self, property_dict):
		raise NotImplementedError(__class__.__name__)

	@classmethod
	def instanciate(cls, renderer_name, **kwargs):
		if renderer_name not in cls._RENDERER_INSTANCES:
			if renderer_name not in cls._RENDERER_CLASSES:
				raise RendererRegistryException(f"No renderer class registered for: {renderer_name}")
			renderer_class = cls._RENDERER_CLASSES[renderer_name]
			instance = renderer_class(**kwargs)
			if renderer_class._CACHE:
				instance = RendererCache(instance)
			cls._RENDERER_INSTANCES[renderer_name] = instance
		return cls._RENDERER_INSTANCES[renderer_name]

	@classmethod
	def register(cls, renderer_class):
		if renderer_class._NAME is None:
			raise RendererRegistryException("Class to be rendered needs to have a name.")
		if renderer_class._NAME in cls._RENDERER_CLASSES:
			raise RendererRegistryException(f"Duplicate renderer class name: {renderer_class._NAME}")
		cls._RENDERER_CLASSES[renderer_class._NAME] = renderer_class
		return renderer_class

if __name__ == "__main__":
	class DebugRenderer(BaseRenderer):
		@property
		def name(self):
			return "debug"

		@property
		def properties(self):
			return { "version": 1 }

		def render(self, property_dict):
			return {
				"text":		property_dict["letter"] * property_dict["count"],
				"bytes":	b"foobar" * 1000,
			}

	cache = RendererCache(DebugRenderer())
	print("Result = ", cache.render({
		"letter":	"Q",
		"count":	10,
	}))
