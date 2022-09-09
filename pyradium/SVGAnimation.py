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

import enum
import logging
from pyradium.Exceptions import UsageException
from pyradium.SVGTransformation import SVGTransformation

_log = logging.getLogger(__spec__.name)

class SVGAnimationMode(enum.Enum):
	Compose = "compose"				# Add new layers on top
	ComposeAll = "compose-all"		# Add new layers on top, but consider all layers from the start
	Replace = "replace"				# New layers replace lower layers

class SVGLayerTag(enum.Enum):
	NoStop = "nostop"				# Do not emit this layer
	Protect = "protect"				# Do not remove this layer on 'reset'
	Reset = "reset"					# Remove all but protected layers

class SVGAnimation():
	def __init__(self, svg_filename, animation_mode = None):
		if svg_filename is None:
			raise UsageException("SVG animation needs a source SVG filename, but none given.")
		if not svg_filename.lower().endswith(".svg"):
			raise UsageException(f"SVG animation only works with SVG input, but filename {svg_filename} does not end with '.svg'.")

		self._svg_filename = svg_filename
		if animation_mode is None:
			self._animation_mode = SVGAnimationMode.Compose
		else:
			try:
				self._animation_mode = SVGAnimationMode(animation_mode)
			except ValueError as e:
				raise UsageException(f"SVG animation mode '{animation_mode}' is  invalid (needs to be one of {SVGAnimationMode})") from e
		self._svg = SVGTransformation(svg_filename)

	def _determine_considered_layers(self) -> list[str]:
		if self._animation_mode == SVGAnimationMode.Compose:
			considered_layers = list(self._svg.visible_layer_ids)
		elif self._animation_mode in [ SVGAnimationMode.ComposeAll, SVGAnimationMode.Replace ]:
			considered_layers = list(self._svg.layer_ids)
		else:
			raise NotImplementedError(self._animation_mode)
		return considered_layers

	def _get_layer_tags(self, layer_id):
		tags = set()
		layer = self._svg.get_layer(layer_id)
		label = layer.label
		if ":" in label:
			(tags, _) = label.split(":", maxsplit = 1)
			for tag in tags:
				try:
					tag = SVGLayerTag(tag)
					tags.add(tag)
				except ValueError as e:
					_log.warning("Unknown layer tag in %s layer %s: %s", self._svg_filename, layer_id, tag)
		return tags

	def _show_layer(self, layer_id):
		self._svg_transforms.append({
			"cmd":			"show_layer",
			"layer_id":		layer_id,
		})
		if SVGLayerTag.Protect not in self._layer_tags[layer_id]:
			self._shown_unprotected_layers.add(layer_id)

	def _hide_layer(self, layer_id):
		self._svg_transforms.append({
			"cmd":			"hide_layer",
			"layer_id":		layer_id,
		})
		if layer_id in self._shown_unprotected_layers:
			self._shown_unprotected_layers.remove(layer_id)

	def _hide_all_layers(self):
		for layer_id in self._considered_layers:
			self._hide_layer(layer_id)

	def render(self):
		# Determine which layers we consider for the anymation in the first place
		self._considered_layers = self._determine_considered_layers()

		# Then get all the tags associated with those layers
		self._layer_tags = { layer_id: self._get_layer_tags(layer_id) for layer_id in self._considered_layers }

		# Find out which layers are protected
		self._protected_layer_ids = set(layer_id for (layer_id, layer_tags) in self._layer_tags.items() if SVGLayerTag.Protect in layer_tags)

		# Store commands to hide all layers first
		self._svg_transforms = [ ]
		self._shown_unprotected_layers = set()
		self._hide_all_layers()

		# Then go through the layers one-by-one and render then as appropriate
		previous_layer_id = None
		for layer_id in self._considered_layers:
			tags = self._layer_tags[layer_id]

			# Determine if slide is causing a reset, i.e. removal of below
			# layers which are unprotected
			if SVGLayerTag.Reset in tags:
				# Hide all below layers but those which are protected
				for below_layer_id in self._shown_unprotected_layers:
					self._hide_layer(below_layer_id)

			# Then show the current layer
			self._show_layer(layer_id)

			# If we're in a replacing mode, then hide the previous layer
			if (self._animation_mode == SVGAnimationMode.Replace) and (previous_layer_id is not None):
				self._hide_layer(previous_layer_id)

			# Emit it as a frame if it's not marked as "nostop"
			if SVGLayerTag.NoStop not in tags:
				yield self._svg_transforms
			previous_layer_id = layer_id
