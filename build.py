'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os, filecmp, re, random, webbrowser, shutil, time, sys
from pathlib import Path, PurePath
from datetime import datetime, timezone
from operator import itemgetter, attrgetter, methodcaller
from shutil import copyfile

from core.Blog import Blog
from core.Author import Author
from core.Category import Category
from core.Page import Page
from core.Pages import Pages
from core.journal import niceprint

def build(isLocal=False):

	def readFile(path, isPage=False):
		'''Read Narval files PAGES (with isPage = True), CONFIG, CATEGORIES, AUTHORS and get values.'''
		arr, pair = [], {}
		emptyLine = 0
		if os.path.isfile(path):
			with open(path, 'r') as f:
				while 1:
					if emptyLine == 1 and isPage == True:
						arr[0]['content'] = f.read().strip()
						break
					line = f.readline().replace('\t', '').rstrip('\n\r')
					elts = line.split(':')
					key = elts[0].strip()
					value = ':'.join(elts[1:]).strip()
					separator = '⟨∴⊕≡⊕∴⟩'
					line = key + separator + value
					if len(line) >= len(separator) + 2:
						emptyLine = 0
						elts = line.split(separator)
						key = elts[0]
						value = elts[1]
						x = key.lower()
						pair[x] = value
					elif emptyLine == 0:
						arr.append(pair)
						pair = {}
						emptyLine = 1
					else:
						break
		return(arr)

	def getInstancesOf(of, file, categories=[], authors=[]): # of = Category, Author, Blog or Page
		fileResult = readFile(file, True if of=='Page' else False)
		arr, newCategories, newAuthors = [], [], []
		if fileResult != []:
			for pair in fileResult:
				if of == 'Category':
					attrs = ('title', 'slug', 'definition', 'description', 'image', 'template', 'color')
					instance = Category()
				elif of == 'Author':
					attrs = ('name', 'slug', 'mail', 'website', 'biography', 'description', 'image')
					instance = Author()
				elif of == 'Blog':
					attrs = ('url', 'title', 'subtitle', 'date', 'description', 'itemsbypage',
						'folder', 'author', 'theme', 'template', 'lang', 'disqus', 'posts', 'pages')
					instance = Blog()
				elif of == 'Page':
					attrs = ('title', 'date', 'content', 'slug', 'modified', 'categories', 'introduction',
						'description', 'authors', 'image', 'template', 'status')
					instance = Page()
				else: return arr
				for key in pair:
					val = pair[key]
					isFound = False
					for attr in attrs:
						if key == attr:
							if attr == 'categories':
								pageCategories = []
								items = val.split('+')
								for item in items:
									item = item.strip()
									isPresent = False
									for c in categories:
										if item == c.title:
											isPresent = True
											pageCategories.append(c)
									if isPresent == False:
										niceprint("Category `{}` (found in `{}`) is not presents in `CATEGORIES`".format(item, file), "INFO")
										newCategory = Category()
										newCategory.title = item
										newCategories.append(newCategory)
										pageCategories.append(newCategory)
								val = pageCategories
							elif attr == 'authors':
								pageAuthors = []
								items = val.split('+')
								for item in items:
									item = item.strip()
									isPresent = False
									for a in authors:
										if item == a.name:
											isPresent = True
											pageAuthors.append(a)
									if isPresent == False:
										niceprint("Author `{}` (found in `{}`) is not presents in `AUTHORS`".format(item, file), "INFO")
										newAuthor = Author()
										newAuthor.name = item
										newAuthors.append(newAuthor)
										pageAuthors.append(newAuthor)
								val = pageAuthors

							setattr(instance, attr, val) # => same as instance.attr = val
							isFound = True
							break
					if isFound == False:
						niceprint("Key `{}` is not recognized in {}".format(key, file), "WARN")
				arr.append(instance)
		return [arr, newCategories, newAuthors] # retourner aussi newCategories et newAuthors

	def getInstanceOfPages(path):
		categoriesUsed, authorsUsed = [], []
		categories = getInstancesOf('Category', path + 'CATEGORIES')[0]
		authors = getInstancesOf('Author', path + 'AUTHORS')[0]
		plist = []
		for fileName in os.listdir(path):
			if os.path.isfile(path + fileName) and fileName != 'CATEGORIES' and fileName != 'AUTHORS':
				pageResult = getInstancesOf('Page', path + fileName, categories, authors)
				page = pageResult[0][0] # le premier [0] indique le tableau d'instances, le second indique le 1er et seul élément de ce tableau : une instance de Page
				categories += pageResult[1]
				authors += pageResult[2]
				plist.append(page)
				if page.categories != None:
					for c in page.categories:
						add = True
						for cat in categoriesUsed:
							if cat.title == c.title:
								add = False
								break
						if add == True:
							categoriesUsed.append(c)
				if page.authors != None:
					for a in page.authors:
						add = True
						for aut in authorsUsed:
							if aut.name == a.name:
								add = False
								break
						if add == True:
							authorsUsed.append(a)

		# tri des posts par date (le plus récent en premier)
		plist = sorted(plist, key=attrgetter('date'), reverse=True)
		# tri des catégories utilisées
		categoriesUsed = sorted(categoriesUsed, key=attrgetter('title'))
		# tri des auteurs ayant écrits
		authorsUsed = sorted(authorsUsed, key=attrgetter('name'))

		pages = Pages()
		pages.list = plist
		pages.categories = categoriesUsed
		pages.authorsUsed = authorsUsed
		return pages

	def copyAll(src, dst):
		if os.path.isdir(dst) == False: os.mkdir(dst)
		paths = PurePath(dst).parts
		rootFolder = paths[0] # blog.folder (_NARVAL)
		# ajout des dossiers
		for p in Path().glob(src + '**/*'):
			if p.is_dir():
				p = PurePath(p).parts
				folder = os.path.join(rootFolder, '/'.join(p[1:]))
				if os.path.isdir(folder) == False:
					os.mkdir(folder)
		# ajout des fichiers
		for p in Path().glob(src + '**/*'):
			if p.is_file():
				p1 = PurePath(p).parts
				file = os.path.join(rootFolder, '/'.join(p1[1:]))
				if os.path.isfile(file) == True:
					if filecmp.cmp(p, file) == False:
						copyfile(p, file)
				else:
					copyfile(p, file)
		# suppression des dossiers de la destination non présents dans la source
		for p in Path().glob(dst + '**/*'):
			if p.is_dir():
				p1 = PurePath(p).parts
				folder = os.path.join(src, '/'.join(p1[2:])) # 2 car src est un chemin de 2 dossiers
				if os.path.isdir(folder) == False:
					shutil.rmtree(p)
		# suppression des fichiers de la destination non présents dans la source
		for p in Path().glob(dst + '**/*'):
			if p.is_file():
				p1 = PurePath(p).parts
				file = os.path.join(src, '/'.join(p1[2:])) # 2 car src est un chemin de 2 dossiers
				if os.path.isfile(file) == False:
					os.remove(p)

	posts = getInstanceOfPages('content/posts/')
	pages = getInstanceOfPages('content/pages/')

	blog = getInstancesOf('Blog', 'content/CONFIG')[0][0]
	blog.posts = posts
	blog.pages = pages

	if isLocal == True:
		blog.folder = blog.folder + '-local'
		blog.url = os.path.abspath('') + '/' + blog.folder

	### Build tree (folders & files)

	# si le dossier du blog généré n'existe pas, on le crée
	if os.path.isdir(blog.folder) == False: os.mkdir(blog.folder)
	copyAll('content/themes/', blog.folder + '/themes/')
	copyAll('content/attachments/', blog.folder + '/attachments/')

	# Categories of posts
	for c in blog.posts.categories:
		path = os.path.join(blog.folder, c.slug)
		if os.path.isdir(path) == False: os.mkdir(path)
		postsFiltred = []
		for p in blog.posts.list:
			if c in p.categories: postsFiltred.append(p)
		ranges = [postsFiltred[i:i+blog.itemsbypage] for i in range(0, len(postsFiltred), blog.itemsbypage)]
		i, nbRanges = 1, len(ranges)
		for r in ranges:
			if i == 1:
				with open(path + '/index.html', 'w') as render:
					render.write(blog.viewPosts(r, [i, nbRanges], c))
			else:
				with open(path + '/page' + str(i) + '.html', 'w') as render:
					render.write(blog.viewPosts(r, [i, nbRanges], c))
			i += 1

	# Categories of pages
	for c in blog.pages.categories:
		path = os.path.join(blog.folder, c.slug)
		if os.path.isdir(path) == False: os.mkdir(path)
		pagesFiltred = []
		for p in blog.pages.list:
			if c in p.categories: pagesFiltred.append(p)
		ranges = [pagesFiltred[i:i+blog.itemsbypage] for i in range(0, len(pagesFiltred), blog.itemsbypage)]
		i, ranges = 1, len(ranges)
		for r in ranges:
			if i == 1:
				with open(path + '/index.html', 'w') as render:
					render.write(blog.viewPages(r, [i, nbRanges], c))
			else:
				with open(path + '/page' + str(i) + '.html', 'w') as render:
					render.write(blog.viewPages(r, [i, nbRanges], c))
			i += 1

	# RSS
	with open(blog.folder + '/RSSfeed.xml', 'w') as render:
		render.write(blog.viewRss())

	# Readme
	with open(blog.folder + '/README.md', 'w') as render:
		render.write(blog.viewReadme())

	# Posts
	ranges = [blog.posts.list[i:i+int(blog.itemsbypage)] for i in range(0, len(blog.posts.list), int(blog.itemsbypage))]
	nbRanges, i = len(ranges), 1
	for r in ranges:
		path = '{}/index.html'.format(blog.folder) if i == 1 else '{}/page{}.html'.format(blog.folder, str(i))
		with open(path, 'w') as render:
			render.write(blog.viewPosts(r, [i, nbRanges]))
		i += 1

	# Post
	for p in blog.posts.list:
		with open(blog.folder + '/' + p.slug + '.html', 'w') as render:
			render.write(blog.viewPost(p))

	# Page
	for p in blog.pages.list:
		with open(blog.folder + '/' + p.slug + '.html', 'w') as render:
			render.write(blog.viewPage(p))

	# Archives
	with open(blog.folder + '/archives.html', 'w') as render:
		render.write(blog.viewArchives())

build()
build(True)
