class Vector2D():
	def __init__(self, x = 0, y = 0):
		self._x = x
		self._y = y

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	def __iadd__(self, vector):
		return Vector2D(self.x + vector.x, self.y + vector.y)
