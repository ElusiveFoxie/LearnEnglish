import datetime
import random
import re
import sys
import sqlite3
import argparse
import requests
from bs4 import BeautifulSoup

version = "LeanEnglish v1.1 by ElusiveFox, matisec, Nomad618 (https://github.com/ElusiveFoxie/LearnEnglish)"
banner = """																				   
 __					   _____		 _ _	 _	  _		  _ _ _ _____ _____ ____  
|  |   ___ ___ ___ ___   |   __|___ ___| |_|___| |_   | |_ _ _   | | | |	 |_   _|	\\ 
|  |__| -_| .'|  _|   |  |   __|   | . | | |_ -|   |  | . | | |  | | | |  |  | | | |  |  |
|_____|___|__,|_| |_|_|  |_____|_|_|_  |_|_|___|_|_|  |___|_  |  |_____|_____| |_| |____/ 
								   |___|				  |___|									
"""

verbosity = 0
'''
Verbosity levels:
0 -> only critical messages (connection errors etc.)
1 -> info about ongoing operations
2 -> errors pointing to specific methods
'''

	
def getArguments():
	parser = argparse.ArgumentParser(description = "App to learn English words of the day")
	parser.add_argument("--version", dest="version", help="Print out version", action="store_true")
	parser.add_argument("-b", "--banner", dest="banner", help="Print out fancy banner", action="store_true")
	parser.add_argument("-v", "--verbosity", dest="verbosity", help="Increase verbosity level", action="count")

	getGroup = parser.add_mutually_exclusive_group()
	getGroup.add_argument("-t", "--get-today", dest="today", help="Print today's word of the day and add word to the database", action="store_true")
	getGroup.add_argument("-r", "--get-random", dest="random", help="Print radom word of the day and add word to the database", default=0, type=int)
	getGroup.add_argument("-f", "--get-from", dest="dateFrom", help="Print word from specified date <date format: yyyy:mm:dd>")
	
	parser.add_argument("-g", "--gen-test", dest="testLength", help="Generate test of random words from the dictionary", type=int)

	parser.add_argument("-s", "--show", dest="show", help="Show content of dictionary", action="store_true")
	parser.add_argument("-c", "--clear", dest="clear", help="Clear dictionary", action="store_true")
	
	options = parser.parse_args()

	if(not options.verbosity):
		options.verbosity = 0

	if(options.verbosity > 2):
		printMessage("[*] Max verbosity level is 2, changing...", 0)
		options.verbosity = 2
	
	#validate date from --get-from argument

	return options


def printMessage(msg, v):
	if(verbosity >= v):
		print(msg)



class Word:

	def __init__(self, word, partOfSpeech, transcript, definition):
		self.word = word
		self.partOfSpeech = partOfSpeech
		self.transcript = transcript
		self.definition = definition

	def show(self):
		print("### " + self.word + " ###")
		print("Part of speech: " + self.partOfSpeech)
		print("Transcript: " + self.transcript)
		print("Definition: " + self.definition + "\n")


class MyDictionary(object):
	def __init__(self, filepath):
		self.filepath = filepath
		self.type = ""
		
		self.initDatabase()
			

	#### DATABASE OPERATIONS ####

	def initDatabase(self):
		conn = sqlite3.connect(self.filepath)
		c = conn.cursor()

		try:
			if (c.execute("SELECT * FROM sqlite_master WHERE name ='dictionary' and type='table'").fetchone()):
				printMessage("[+] Dictionary found",1)
			else:
				c.execute("""CREATE TABLE dictionary (
					id integer primary key autoincrement, 
					word text, 
					partOfSpeech text, 
					transcript text, 
					definition, text);
				""")
				conn.commit()
				printMessage("[+] Created dictionary table",1)
		except:
			printMessage("[-] Something went wrong in 'initDatabase' method",2)
		conn.close()

	def selectWholeDatabase(self):
		conn = sqlite3.connect(self.filepath)
		c = conn.cursor()

		newWords = []
		try:
			for row in c.execute("SELECT word, partOfSpeech, transcript, definition FROM dictionary;"):
				newWordObj = Word(row[0], row[1], row[2], row[3])
				newWords.append(newWordObj)
		except:
			printMessage("[-] Something went wrong in 'selectWholeDatabase' method", 2)
			self.initDatabase()

		conn.close()
		return newWords

	def insertWordIntoDatabase(self, wordObj):
		conn = sqlite3.connect(self.filepath)
		c = conn.cursor()
		try:
			if (c.execute("SELECT word FROM dictionary WHERE word='" + wordObj.word + "';").fetchone()):
				print("[+] Word " + wordObj.word + " already exists in the database")
			else:
				c.execute("""
					INSERT INTO dictionary (
						word, 
						partOfSpeech, 
						transcript, 
						definition) 
					VALUES( """
						+ "'" + wordObj.word + "', "
						+ "'" + wordObj.partOfSpeech + "', "
						+ "'" + wordObj.transcript + "', "
						+ "'" + wordObj.definition 
					+ "')"
				)
				conn.commit()
				printMessage("[+] Word " + wordObj.word + " added to the database", 1)
		except:
			printMessage("[-] Something went wrong in 'insertWordIntoDatabase' method", 2)
		conn.close()

	def purgeDatabase(self):
		conn = sqlite3.connect(self.filepath)
		c = conn.cursor()
		try:
			c.execute("DROP TABLE dictionary")
			conn.commit()
		except:
			printMessage("[-] Something went wrong in 'purgeDatabase' method", 2)
		conn.close()
		printMessage("[+] Database purged", 1)


	#### DISPLAY METHODS ####

	def show(self):	
		printMessage("[*] Showing database...\n", 1)
		wordsList = self.selectWholeDatabase()
		for i in range(len(self.selectWholeDatabase())):
			wordsList[i].show()
	

	#### SCRAP METHODS ####

	def appendWord(self, wordObj):
		self.insertWordIntoDatabase(wordObj)

	def scrapWordOfTheDay(self, date):
		return None

	def getDefinition(self, word):
		return ""

	def scrapWordOfToday(self):
		return self.scrapWordOfTheDay(str(datetime.date.today()))

	def scrapAllWordsFrom(self, dateFrom):
		now = datetime.date.today()
		dateFrom = dateFrom.split("-")
		dateFrom = datetime.date(int(dateFrom[0]), int(dateFrom[1]), int(dateFrom[2]))
		delta = now - dateFrom
		
		newWordsList = []
		for i in range(delta.days + 1):
			day = dateFrom + datetime.timedelta(days=i)
			newWordObj = self.scrapWordOfTheDay(day)
			self.appendWord(newWordObj)
			newWordsList.append(newWordObj)
		
		return newWordsList
		
	def scrapRandomWordOfTheDay(self):
		return self.scrapWordOfTheDay(self.getRandomDate())
	

	#### OTHER METHODS ####	
	
	def getRandomDate(self):
		d1 = datetime.datetime.strptime('2007-01-01', '%Y-%m-%d')
		d2 = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
		
		delta = d2 - d1
		intDelta = delta.days
		randomDays = random.randrange(intDelta)

		return (str(d1 + datetime.timedelta(days=randomDays)).replace(" 00:00:00", ""))


class MyEnglishDictionary(MyDictionary):

	def __init__(self, filepath):
		super(MyEnglishDictionary, self).__init__(filepath)
		self.type = "English"

	def scrapWordOfTheDay(self, date):
		response = requests.get('https://www.merriam-webster.com/word-of-the-day/' + str(date))

		if response:
			# print('Success!')
			html_doc = response.text
			soup = BeautifulSoup(html_doc, 'html.parser')

			# WORD -> H1 tag
			newWord = soup.find('h1').text.capitalize()

			# PART OF SPEECH -> span z class="main-attr"
			newPartOfSpeech = soup.find("span", {"class": "main-attr"})

			# TRANSCRIPT -> span z class="word-syllables"
			newTranscript = soup.find("span", {"class": "word-syllables"})

			# Definition
			s = soup
			d = s.find("div", {"class": "wod-definition-container"})
			c = d.findChildren()

			# list of nodes between first two <h2> tags
			l = c[c.index(d.findAll('h2')[0])+1:c.index(d.findAll('h2')[1])]
			results = []
			for i in l:
				if i.name == 'p':
					f = i.findChild('strong')
					if f:
						f.extract()
					results.append(i.text.strip())
			if(len(results)>0):
				newDefinition = results[0]
			else:
				printMessage("[-] Could not find definition for word " + newWord, 1)
				newDefinition = "definition not found"


			newWordObj = Word(
				newWord, 
				newPartOfSpeech.text.strip(), 
				newTranscript.text.strip(), 
				newDefinition
			)
			
			self.appendWord(newWordObj)
			return newWordObj

		else:
			printMessage('[-] A connection error to "merriam-webster" has occurred. Status code:' + response.status_code, 0)
			return None


args = getArguments()
if(args):
	verbosity = args.verbosity
	if(args.banner):
		print(banner)
	if(args.version):
		print(version)


	myDict = MyEnglishDictionary("EnglishDictionary.db")
	if(args.today):
		myDict.scrapWordOfToday()
	elif(args.random):
		for i in range(args.random):
			myDict.scrapRandomWordOfTheDay()
	elif(args.dateFrom):
		myDict.scrapWordOfTheDay(args.dateFrom)
	if(args.show):
		myDict.show()
	if(args.clear):
		answer = input("[?] Do you really want to purge the database? [Y/N]: ")
		if(answer == "Y" or answer == "y"):
			myDict.purgeDatabase()


