'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

from core.Blog import Blog

class Page:
	"""Classe représentant une page. Une page peut être un post."""
	def __init__(self):
		self._title = None
		self._date = None
		self._content = None
		self._slug = None
		self._modified = ""
		self._categories = []
		self._introduction = ""
		self._description = ""
		self._authors = []
		self._image = ""
		self._template = ""
		self._status = "pubished"

	@property
	def title(self):
		return self._title

	@property
	def date(self):
		return self._date

	@property
	def content(self):
		return self._content

	@property
	def slug(self):
		return self._slug

	@property
	def modified(self):
		return self._modified

	@property
	def categories(self):
		return self._categories

	@property
	def introduction(self):
		return self._introduction

	@property
	def description(self):
		return self._description

	@property
	def authors(self):
		return self._authors

	@property
	def image(self):
		return self._image

	@property
	def template(self):
		return self._template

	@property
	def status(self):
		return self._status

	@title.setter
	def title(self, value):
		if self._slug == None:
			self._slug = Blog._slugify(self, value)
		self._title = value

	@date.setter
	def date(self, value):
		self._date = Blog._isoDate(self, value)

	@content.setter
	def content(self, value):
		self._content = value

	@slug.setter
	def slug(self, value):
		self._slug = Blog._slugify(self, value)

	@modified.setter
	def modified(self, value):
		self._modified = Blog._isoDate(self, value)

	@categories.setter
	def categories(self, value):
		self._categories = value

	@introduction.setter
	def introduction(self, value):
		if self._description == "":
			self._description = Blog.rmHTML(self, value)
		self._introduction = value

	@description.setter
	def description(self, value):
		self._description = value

	@authors.setter
	def authors(self, value):
		self._authors = value

	@image.setter
	def image(self, value):
		self._image = value

	@template.setter
	def template(self, value):
		self._template = value

	@status.setter
	def status(self, value):
		self._status = value
