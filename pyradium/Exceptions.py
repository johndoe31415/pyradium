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

class PyRadiumException(Exception): pass

class ConfigurationException(PyRadiumException): pass

class CallingProcessException(PyRadiumException): pass

class XMLFileNotFoundException(PyRadiumException): pass
class MalformedJSONInputException(PyRadiumException): pass
class MalformedXMLInputException(PyRadiumException): pass
class MalformedStyleConfigurationException(PyRadiumException): pass

class SlideException(PyRadiumException): pass
class UndefinedContentException(SlideException): pass
class TemplateErrorException(SlideException): pass
class TimeSpecificationError(SlideException): pass
class UsageException(SlideException): pass

class XMLHookRegistryException(PyRadiumException): pass
class RendererRegistryException(PyRadiumException): pass

class InvalidTransformationException(PyRadiumException): pass

class DuplicateOrderException(PyRadiumException): pass
class InvalidBooleanValueException(PyRadiumException): pass
class InvalidValueNodeException(PyRadiumException): pass
class FailedToLookupFileException(PyRadiumException): pass
class InvalidTeXException(PyRadiumException): pass
class UnknownSlideTypeException(PyRadiumException): pass
class ImageRenderingException(PyRadiumException): pass
class CodeHighlightingException(PyRadiumException): pass
class UnknownParameterException(PyRadiumException): pass
class MissingParameterException(PyRadiumException): pass
class InvalidBooleanExpressionException(PyRadiumException): pass

class AcronymException(PyRadiumException): pass
class InvalidAcronymFileException(AcronymException): pass
class DuplicateAcronymException(AcronymException): pass

class AgendaException(PyRadiumException): pass
class IllegalAgendaSyntaxException(AgendaException): pass
class UndefinedAgendaTimeException(AgendaException): pass
class UnresolvableWeightedEntryException(AgendaException): pass
class AgendaTimeMismatchException(AgendaException): pass

class FailedToExecuteSubprocessException(PyRadiumException): pass

class SpellcheckerException(PyRadiumException): pass

class StyleParameterException(PyRadiumException): pass
class InvalidStyleParameterDefinitionException(StyleParameterException): pass
class InvalidStyleParameterValueException(StyleParameterException): pass
