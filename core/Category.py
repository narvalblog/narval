'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

from core.Blog import Blog

class Category:
	"""Classe représentant une catégorie."""
	def __init__(self):
		self._title = None
		self._slug = None
		self._definition = ''
		self._description = ''
		self._image = None
		self._template = ''
		self._color = None

	@property
	def title(self):
		return self._title

	@property
	def slug(self):
		return self._slug

	@property
	def definition(self):
		return self._definition

	@property
	def description(self):
		return self._description

	@property
	def image(self):
		return self._image

	@property
	def template(self):
		return self._template

	@property
	def color(self):
		return self._color

	@title.setter
	def title(self, value):
		if self._slug == None:
			self._slug = Blog._slugify(self, value)
		self._title = value

	@slug.setter
	def slug(self, value):
		self._slug = Blog._slugify(self, value)

	@definition.setter
	def definition(self, value):
		if self._description == '':
			self._description = Blog.rmHTML(self, value)
		self._definition = value

	@description.setter
	def description(self, value):
		self._description = value

	@image.setter
	def image(self, value):
		self._image = value

	@template.setter
	def template(self, value):
		self._template = value

	@color.setter
	def color(self, value):
		self._color = value
