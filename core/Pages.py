'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

class Pages:
	"""Classe listant toutes les pages, leurs catégories et leurs autheurs."""
	def __init__(self):
		self._list = []
		self._categories = []
		self._authors = []

	@property
	def list(self):
		return self._list

	@property
	def categories(self):
		return self._categories

	@property
	def authors(self):
		return self._authors

	@list.setter
	def list(self, value):
		self._list = value

	@categories.setter
	def categories(self, value):
		self._categories = value

	@authors.setter
	def authors(self, value):
		self._authors = value
