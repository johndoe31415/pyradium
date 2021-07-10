# This class is in its own file.
class Foo():
	def __init__(self, moo):
		self._moo = moo

	@property
	def moo(self):
		return self._moo
