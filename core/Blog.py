'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-
import re, os, time, tenjin
import locale
from datetime import datetime, timezone
from tenjin.helpers import *
from tenjin.html import *
pp = [
	tenjin.TrimPreprocessor(),			# trim spaces before tags
	tenjin.PrefixedLinePreprocessor(),	# convert ':: ...' into '<?py ... ?>'
]
engine = tenjin.Engine(path=['content/templates/Minimal/'], pp=pp)

class Blog:
	"""Classe représentant le blog."""
	def __init__(self):
		self._modified = datetime.now(timezone.utc).astimezone().isoformat()
		self._url = None
		self._title = None
		self._subtitle = ""
		self._date = None
		self._description = ""
		self._itemsbypage = 10
		self._folder = "_Narval"
		self._author = None
		self._theme = "Minimal"
		self._template = "Minimal"
		self._lang = "fr"
		self._disqus = ""
		self._posts = []
		self._pages = []
		self._engine = tenjin.Engine(path=['content/templates/Minimal/'], pp=pp)

	@property
	def modified(self):
		return self._modified

	@property
	def url(self):
		return self._url

	@property
	def title(self):
		return self._title

	@property
	def subtitle(self):
		return self._subtitle

	@property
	def date(self):
		return self._date

	@property
	def description(self):
		return self._description

	@property
	def itemsbypage(self):
		return self._itemsbypage

	@property
	def folder(self):
		return self._folder

	@property
	def author(self):
		return self._author

	@property
	def theme(self):
		return self._theme

	@property
	def template(self):
		return self._template

	@property
	def lang(self):
		return self._lang

	@property
	def disqus(self):
		return self._disqus

	@property
	def posts(self):
		return self._posts

	@property
	def pages(self):
		return self._pages

	@property
	def engine(self):
		return self._engine

	@modified.setter
	def modified(self, value):
		self._modified = value

	@url.setter
	def url(self, value):
		self._url = value

	@title.setter
	def title(self, value):
		self._title = value

	@subtitle.setter
	def subtitle(self, value):
		if self._description == None:
			self._description = Blog.rmHTML(self, value)
		self._subtitle = value

	@date.setter
	def date(self, value):
		self._date = Blog._isoDate(self, value)

	@description.setter
	def description(self, value):
		self._description = value

	@itemsbypage.setter
	def itemsbypage(self, value):
		self._itemsbypage = int(value)

	@folder.setter
	def folder(self, value):
		self._folder = value

	@author.setter
	def author(self, value):
		self._author = value

	@theme.setter
	def theme(self, value):
		self._theme = value

	@template.setter
	def template(self, value):
		self._template = value
		self._engine = tenjin.Engine(path=['content/templates/' + value + '/'], pp=pp)

	@lang.setter
	def lang(self, value):
		if value == 'fr' or value == 'en':
			self._lang = value

	@disqus.setter
	def disqus(self, value):
		self._disqus = value

	@posts.setter
	def posts(self, value):
		self._posts = value

	@pages.setter
	def pages(self, value):
		self._pages = value


	# VIEWS

	# parts
	def viewHead(self, category='', author='', page=''):
		return engine.render('head.pyhtml', {
			'blog': self,
			'category': category,
			'author': author,
			'page': page
		})
	def viewHeader(self):
		return engine.render('header.pyhtml', {'blog': self})
	def viewFooter(self):
		return engine.render('footer.pyhtml', {'blog': self})
	def viewPaging(self, paging):
		return engine.render('paging.pyhtml', {'blog': self, 'currentPage': paging[0], 'totalPages': paging[1]})
	def viewCategories(self, categories):
		return engine.render('categories.pyhtml', {'blog': self, 'categories': categories})
	# full
	def viewRss(self):
		return engine.render('rss.pyhtml', {'blog': self})
	def viewReadme(self):
		return engine.render('readme.pyhtml', {'blog': self})
	def viewPosts(self, selection, paging, category='', author=''):
		#blog, r, (i, nbRanges)
		url = 'posts.pyhtml'
		if category != '':
			tmp = (category.template + '/') if category.template != '' else ''
			if tmp != '': url = (tmp + url) if os.path.exists('content/templates/' + tmp + url) else url
		return engine.render(url, {
			'blog': self,
			'selection': selection,
			'paging': paging,
			'category': category,
			'author': author
		})
	def viewPost(self, post):
		return engine.render('post.pyhtml', {'blog': self, 'post': post})
	def viewPage(self, page):
		return engine.render('page.pyhtml', {'blog': self, 'page': page})
	def viewArchives(self):
		return engine.render('archives.pyhtml', {'blog': self})

	# TOOLS
	def _isoDate(self, str):
		completePrecision = 	r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}\+\d{2}:\d{2}"
		noMilliseconds = 		r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
		noSeconds = 			r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"
		noHoursMinutes = 		r"\d{4}-\d{2}-\d{2}"
		str = re.sub(' ', 'T', str)
		if re.search(completePrecision, str):
			dateISO = str
		elif re.search(noMilliseconds, str):
			dateISO = str + ".000000+00:00"
		elif re.search(noSeconds, str):
			dateISO = str + ":00.000000+00:00"
		elif re.search(noHoursMinutes, str):
			dateISO = str + "T00:00:00.000000+00:00"
		else:
			niceprint("Format de date invalide détecté : `{}`.".format(str), "FAIL")

		return dateISO

	def convertDate(self, dateISO, format="%Y-%m-%d"):
		# make your own format : https://docs.python.org/3/library/time.html#time.strftime
		if self.lang == 'fr':
			print('fr hihi')
			locale.setlocale(locale.LC_ALL, 'fr_FR.utf8')
		d = time.strptime(''.join(dateISO.rsplit(':', 1)), "%Y-%m-%dT%H:%M:%S.%f%z")
		return time.strftime(format, d)

	def _slugify(self, title):
		title = Blog.rmHTML(self, title).lower().strip()
		replaceChars = "àáãäâèéëêìíïîòõóöôùúüûñç·/_,:;"
		toChars      = "aaaaaeeeeiiiiooooouuuunc------"
		i = 0
		for r in replaceChars:
			title = re.sub(r, toChars[i], title)
			i += 1
		title = re.sub('[^a-z0-9 -]+', '', title)
		title = re.sub('\s+', '-', title)
		title = re.sub('-+', '-', title)
		title = re.sub("^-", "", title)
		title = re.sub("-$", "", title)
		return title

	def rmHTML(self, strHTML, md=False):
		'''
			Supprime le HTML d'une chaine. Si le second
			paramètre vaut True, alors les emphases et le code
			sont changés en markdown. Utile pour le fichier README.md !
		'''
		if md == True:
			tags = [
				{'tag': 'em', 'md': '_'},
				{'tag': 'strong', 'md': '**'},
				{'tag': 'code', 'md': '`'}
			]
			for t in tags:
				regex = re.compile('<' + t['tag'] + '>(.*?)<\/' + t['tag'] + '>')
				strHTML = re.sub(regex, t['md'] + '\\1' + t['md'], strHTML)

		tags = [
			{'regex': r"<.*?>", 'substitute': ''}, # tags
			{'regex': r"&nbsp;", 'substitute': ' '}, # &nbsp;
			{'regex': r"&[a-bA-B]{4};", 'substitute': ' '} # tous les html entities
		]
		for t in tags:
			strHTML = re.sub(t['regex'], t['substitute'], strHTML)

		return strHTML
