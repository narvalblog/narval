'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

from core.Blog import Blog

class Author:
	"""Classe représentant un·e auteur·e."""
	def __init__(self):
		self._name = None
		self._slug = None
		self._mail = None
		self._website = None
		self._biography = None
		self._description = None
		self._image = None

	@property
	def name(self):
		return self._name

	@property
	def slug(self):
		return self._slug

	@property
	def mail(self):
		return self._mail

	@property
	def website(self):
		return self._website

	@property
	def biography(self):
		return self._biography

	@property
	def description(self):
		return self._description

	@property
	def image(self):
		return self._image

	@name.setter
	def name(self, value):
		if self._slug == None:
			self._slug = Blog._slugify(self, value)
		self._name = value

	@slug.setter
	def slug(self, value):
		self._slug = Blog._slugify(self, value)

	@mail.setter
	def mail(self, value):
		self._mail = value

	@website.setter
	def website(self, value):
		self._website = value

	@biography.setter
	def biography(self, value):
		if self._description == None:
			self._description = Blog.rmHTML(self, value)
		self._biography = value

	@description.setter
	def description(self, value):
		self._description = value

	@image.setter
	def image(self, value):
		self._image = value
