'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-
try:
	import markdown
except ImportError:
	pass
import os, filecmp, re, random, webbrowser, shutil, time
from pathlib import Path, PurePath
from datetime import datetime, timezone
from operator import itemgetter, attrgetter, methodcaller
from shutil import copyfile

from core.Blog import Blog
from core.Author import Author
from core.Category import Category
from core.Page import Page
from core.Pages import Pages
from core.journal import Log

dC = 'content/'
dPo = 'posts/'
dPa = 'pages/'
dAt = 'attachments/'
dTh = 'themes/'
dTe = 'templates/'
fCONF = 'CONFIG'
fCATS = 'CATEGORIES'
fAUTHORS = 'AUTHORS'

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
		if os.path.exists(file) == False and file != dC+dPo+fAUTHORS and file != dC+dPo+fCATS and file != dC+dPa+fAUTHORS and file != dC+dPa+fCATS:
			Log.niceprint("Path `{}` doesn't exist.".format(file), "FAIL")


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
										Log.niceprint("Category `{}` (found in `{}`) is not presents in `{}`.".format(item, file, fCATS), "INFO")
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
										Log.niceprint("Author `{}` (found in `{}`) is not presents in `{}`.".format(item, file, fAUTHORS), "INFO")
										newAuthor = Author()
										newAuthor.name = item
										newAuthors.append(newAuthor)
										pageAuthors.append(newAuthor)
								val = pageAuthors

							setattr(instance, attr, val) # => same as instance.attr = val
							isFound = True
							break
					if isFound == False:
						Log.niceprint("Key `{}` is not recognized in {}".format(key, file), "WARN")

				# contrôle des clefs obligatoires
				if of == 'Category':
					if instance.title == None:
						Log.niceprint("La clef `title` est manquante ou erronée dans `{}`".format(file), "FAIL")
				elif of == 'Author':
					if instance.name == None:
						Log.niceprint("La clef `name` est manquante ou erronée dans `{}`".format(file), "FAIL")
				elif of == 'Blog':
					if instance.title == None:
						Log.niceprint("La clef `title` est manquante ou erronée dans `{}`".format(file), "FAIL")
					elif instance.date == None:
						Log.niceprint("La clef `date` est manquante ou erronée dans `{}`".format(file), "FAIL")
				elif of == 'Page':
					if instance.date == None:
						Log.niceprint("La clef `date` est manquante ou erronée dans `{}`".format(file), "FAIL")
					elif instance.title == None:
						Log.niceprint("La clef `title` est manquante ou erronée dans `{}`".format(file), "FAIL")
					elif instance.content == None:
						Log.niceprint("Le contenu est manquant dans `{}`".format(file), "FAIL")

				if file.lower().endswith(('.md', '.markdown')):
					try:
						instance.content = markdown.markdown(instance.content)
					except Exception:
						niceprint("Le markdown du fichier `{}` ne peut être converti en HTML, car le module Markdown est manquant. La documentation (rubrique `pages/`) indique comment l'installer : https://narvalblog.github.io/documentation-complete.html#pagesFolder.".format(file), "WARN")

				arr.append(instance)
		return [arr, newCategories, newAuthors] # retourner aussi newCategories et newAuthors

	def getInstanceOfPages(path):
		categoriesUsed, authorsUsed = [], []
		categories = getInstancesOf('Category', path + fCATS)[0]
		authors = getInstancesOf('Author', path + fAUTHORS)[0]
		plist = []
		if os.path.exists(path) == False:
			Log.niceprint("Path `{}` doesn't exist.".format(path), "FAIL")
		for fileName in os.listdir(path):
			if os.path.isfile(path + fileName) and fileName != fCATS and fileName != fAUTHORS:
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
		if os.path.exists(src) == False:
			Log.niceprint("Path `{}` doesn't exist.".format(src), "FAIL")
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

	posts = getInstanceOfPages(dC+dPo)
	pages = getInstanceOfPages(dC+dPa)
	blog = getInstancesOf('Blog', dC+fCONF)[0][0]
	blog.posts = posts
	blog.pages = pages

	if isLocal == True:
		blog.folder = blog.folder + '-local'
		blog.url = os.path.join(os.path.abspath(''), blog.folder)

	# Suppression du dossier du blog généré avant de le recréer
	shutil.rmtree(blog.folder)

	### Build tree (folders & files)

	os.mkdir(blog.folder)
	copyAll(dC+dTh, os.path.join(blog.folder, dTh))
	copyAll(dC+dAt, os.path.join(blog.folder, dAt))

	# Categories of posts
	for c in blog.posts.categories:
		path = os.path.join(blog.folder, c.slug)
		os.mkdir(path)
		postsFiltred = []
		for p in blog.posts.list:
			if c in p.categories: postsFiltred.append(p)
		ranges = [postsFiltred[i:i+blog.itemsbypage] for i in range(0, len(postsFiltred), blog.itemsbypage)]
		i, nbRanges = 1, len(ranges)
		for r in ranges:
			if i == 1:
				with open(os.path.join(path, 'index.html'), 'w') as render:
					render.write(blog.viewPosts(r, [i, nbRanges], c))
			else:
				with open(os.path.join(path, 'page' + str(i) + '.html'), 'w') as render:
					render.write(blog.viewPosts(r, [i, nbRanges], c))
			i += 1

	# Categories of pages
	for c in blog.pages.categories:
		path = os.path.join(blog.folder, c.slug)
		os.mkdir(path)
		pagesFiltred = []
		for p in blog.pages.list:
			if c in p.categories: pagesFiltred.append(p)
		ranges = [pagesFiltred[i:i+blog.itemsbypage] for i in range(0, len(pagesFiltred), blog.itemsbypage)]
		i, ranges = 1, len(ranges)
		for r in ranges:
			if i == 1:
				with open(os.path.join(path, 'index.html'), 'w') as render:
					render.write(blog.viewPages(r, [i, nbRanges], c))
			else:
				with open(os.path.join(path, 'page' + str(i) + '.html'), 'w') as render:
					render.write(blog.viewPages(r, [i, nbRanges], c))
			i += 1

	# RSS
	with open(os.path.join(blog.folder, 'RSSfeed.xml'), 'w') as render:
		render.write(blog.viewRss())

	# Readme
	with open(os.path.join(blog.folder, 'README.md'), 'w') as render:
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
		with open(os.path.join(blog.folder, p.slug + '.html'), 'w') as render:
			render.write(blog.viewPost(p))

	# Page
	for p in blog.pages.list:
		with open(os.path.join(blog.folder, p.slug + '.html'), 'w') as render:
			render.write(blog.viewPage(p))

	# Archives
	with open(os.path.join(blog.folder, 'archives.html'), 'w') as render:
		render.write(blog.viewArchives())

	return blog.folder

startTime = time.time()
build()
Log.show = False
path = build(True)
Log.show = True
Log.niceprint("Blog généré avec succés en {} secondes !".format(round(time.time() - startTime, 3)))

res = input("Voir le blog local ? (O/n) ").lower()
if res != 'n':
	webbrowser.open(path + '/index.html', new=2)
