'''
	This file is part of Narval :
	an opensource and free rights static blog generator.
'''

#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys

class Log:
	show = True

	def niceprint(str, type="GOOD"):
		"""
			Met en forme les messages de la console suivant le "type".
			Type = GOOD, INFO, WARN or FAIL.
			Si le type est autre, on utilise le "print" sans le côté "nice" ;)
			https://gist.github.com/vratiu/9780109
		"""

		if Log.show == True:
			if type == "GOOD":
				print('\033[92m█▓▒▒░░░ ' + str + '\033[0m')
			elif type == "INFO":
				print('\033[33m?: ' + str + '\033[0m')
			elif type == "WARN":
				print('\033[93m!: ' + str + '\033[0m')
			elif type == "FAIL":
				print('\033[91m†: ' + str + '\033[0m')
				sys.exit(0)
			else: print(str)
