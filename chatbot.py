import MySQLdb
import sys
import json
import os
from chatterbot import ChatBot
from chatterbot.training.trainers import ChatterBotCorpusTrainer
from chatterbot.training.trainers import ListTrainer

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

chatbot = ChatBot("Sharron Cox")


chatbot.set_trainer(ChatterBotCorpusTrainer)

print "english"
# Train based on the english corpus
chatbot.train("chatterbot.corpus.english")

#print "greetings"
# Train based on english greetings corpus
#chatbot.train("chatterbot.corpus.english.greetings")

#print "convos"
# Train based on the english conversations corpus
#chatbot.train("chatterbot.corpus.english.conversations")


chatbot.set_trainer(ListTrainer)

try:
    con = MySQLdb.connect('rdsnext72.c6npskow0rt3.us-east-1.rds.amazonaws.com', 'next72', 'MT97rane', 'adam')
   
except _mysql.Error, e:
  
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

cur = con.cursor()
cur.execute("SELECT raw, id from full")

rows = cur.fetchall()

for row in rows:
	print row[1]
	parsed_json = json.loads(row[0])
	chat = []
	admin = 0
	if parsed_json['conversation_message']['author']['type'] != "admin":
		chat.append(strip_tags(parsed_json['conversation_message']['body']))
	else:
		admin = 1
	parts =  parsed_json['conversation_parts']['conversation_parts']
	for part in parts:
		if part['body']!=None:
			if part['author']['type']!="admin":
				if admin ==0:
					chat[-1]+=" "+strip_tags(part['body']).replace('\n', ' ').replace(u'\xa0', u' ')


				else:
					admin = 0
					if (len(chat)>1):
						print chat
						print "\n*********\n"
						chatbot.train(chat)
					chat= []
					chat.append(strip_tags(part['body']).replace('\n', ' ').replace(u'\xa0', u' '))
			else:
				if admin ==1:
					if (len(chat)>0):
						chat[-1]+=" "+strip_tags(part['body']).replace('\n', ' ').replace(u'\xa0', u' ')
					else:
						chat = strip_tags(part['body']).replace('\n', ' ').replace(u'\xa0', u' ')
				else:
					admin = 1
					chat.append(strip_tags(part['body']).replace('\n', ' ').replace(u'\xa0', u' '))
	if (len(chat)>1):
		print chat
		print "\n********************************\n"
		chatbot.train(chat)
	


n = raw_input("Say Something\n")
while True:    # infinite loop
	r = str(chatbot.get_response(n))+"\n"
	print "\n"
	n = raw_input(r)
