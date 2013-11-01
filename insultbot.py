# Chance Snow
# Mar 31, 2013
# 2:00 AM
# irc handle: enigma
#######################
# An IRC bot that insults people
# Fetches insults from insultgenerator.org and randominsults.net
# handle: insultbot

import sys
import random
import urllib
import datetime
from os.path import expanduser
from HTMLParser import HTMLParser
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

HOST         = 'iss.cat.pdx.edu'
PORT         = 6697
NICK         = 'insultbot'
REAL_NAME    = ':Enigma\'s Insult Bot'
CHANNEL      = '#insultbot'

SERVICES     = ['http://www.randominsults.net/']

class Logger(object):
    def __init__(self, filename='insultbot.log', console=True):
        self.terminal = sys.stdout
        self.filename = filename
        self.console = console

    def write(self, message):
        self.log = open(self.filename, 'a')
        if self.console:
            self.terminal.write(message)
        self.log.write(message)
        self.log.close()

#print only to log file
sys.stdout = Logger(expanduser('~/.bots/insultbot.log'), False)

#read channels from config file
CHANNELS = []
cfgFile = open(expanduser('~/.bots/.insultbot'), 'r')
for line in cfgFile:
    line = line.strip()
    if not line.startswith('--'):
        if line.find(' ') != -1:
            line = line.split(' ')
            CHANNELS.append((line[0], line[1]))
        else:
            CHANNELS.append((line, None))

print '================================================'
print 'Connecting ' + NICK + ' on ' + HOST + ':' + str(PORT)
now = datetime.datetime.now()
print now.strftime("%a, %b %d, %Y - %I:%M:%S %p")
print '------------------------------------------------'

class InsultHTMLParser(HTMLParser):
    def __init__(self, service):
        HTMLParser.__init__(self)
        self.service = service
        self.tag = None
        self.attrs = None
        self.insult = None
        self.found = False

    def handle_starttag(self, tag, attrs):
        self.tag = str(tag)
        self.attrs = attrs
    def hendle_endtag(self, tag): return
    def handle_data(self, data):
        #print 'Data in ' + str(self.tag) + ' element: ' + str(data)
        if self.service == SERVICES[0]:
            if str(self.tag) == 'i' and not self.found:
                self.insult = str(data).strip()
                self.found = True


def connect_callback(client):
    #helpers.msg(client, "NickServ", "IDENTIFY", "password")
    
    for chan in CHANNELS:
        channel = chan[0]
        key = chan[1]
        if key is None:
            helpers.join(client, channel)
        else:
            helpers.join(client, channel, key)
        print 'Joined ' + channel

    print '------------------------------------------------'


class EnigmaBotHandler(DefaultCommandHandler):
    def say(self, msg, to=None):
        if to == None: to = self.channel
        helpers.msg(self.client, to, msg)
   
    def getnick(self, nick):
        bangIndex = nick.find('!')
        if bangIndex != -1:
            return nick[:bangIndex]
        else:
            return nick

    def getinsult(self):
        #From a random service
        service = random.choice(SERVICES)
        response = urllib.urlopen(service)
        html = response.read()
        parser = InsultHTMLParser(service)
        parser.feed(html)
        insult = parser.insult
        if insult:
            return insult
        else:
            return random.choice(['You suck!', 'Screw you!'])

    def insult(self, to, private=True):
        print 'Insulting ' + to
        msg = 'Hey ' + to + '! ' + self.getinsult()
        if private:
            self.say(msg, to)
        else:
            self.say(msg)

    def privmsg(self, nick, channel, msg):
        self.channel = channel
        nick = self.getnick(nick)
        msg = msg.decode()

        if nick == NICK:
            return
        
        #leave Bot message
        if msg.find('!' + NICK + ' leave') != -1:
            for chan in CHANNELS:
                if chan[0] == channel:
                    self.insult(nick, False)
                    print "Leaving " + channel
                    helpers.part(self.client, channel)
                    break
        
        #quit Bot message
        if msg.find('!' + NICK + ' quit') != -1:
            for chan in CHANNELS:
                if chan[0] == channel:
                    self.insult(nick, False)
                    print "Leaving " + channel
                    helpers.part(self.client, channel)
                    print "Quitting IRC"
                    helpers.quit(self.client, 'Quitting at request')
                    quit()
        
        #help Bot message
        if msg.find('!' + NICK + ' help') != -1:
            for chan in CHANNELS:
                if chan[0] == channel:
                    msg = 'Insultbot Help\n====================\nSay anything about insultbot and prepare to be insulted!\n \nDISCLAIMER: Some of the isults may be graphic in nature.\nBy using insultbot you are agreeing to the following terms:\n  The creator of insultbot (Chance Snow <enigma>) shall not be held liable for anything insultbot says to anyone.\n \nInsultbot Commands:\n----------\n\'!insultbot insult <nick>\'  - Insult someone privately\n\'insult: <nick>\'             - Insult someone privately\n\'!insultbot greet <nick>\'   - Insult someone publicly'
                    self.say(msg, nick)
                    return

        if msg.lower().find('hello') != -1 and msg.lower().find(NICK) != -1:
            self.insult(nick, False)
            return
        
        if msg.lower().find('hi') != -1 and msg.lower().find(NICK) != -1:
            self.insult(nick, False)
            return
        
        if msg.find('!' + NICK + ' greet ') != -1:
            to = msg.split('greet ')[1]
            if to.find(NICK) == -1:
                self.insult(to, False)
            else:
                self.insult(nick, False)
            return
        
        if msg.find('!' + NICK + ' insult ') != -1:
            to = msg.split('insult ')[1]
            if to.find(NICK) != -1:
                self.insult(to)
            else:
                self.insult(nick)
            return
        
        if msg.find('insult: ') != -1:
            to = msg.split(' ')[1]
            if to.find(NICK) != -1:
                self.insult(to)
            else:
                self.insult(nick)
            return

        if msg.find(NICK) != -1 and msg.find('!' + NICK) == -1:
            print 'Insulting ' + nick
            self.say('[Err] ' + random.choice(
                ['I\'m sorry, did you say something <NICK>?',
                'What did you call me <NICK>?',
                'Leave me alone <NICK>!',
                'Did your fatass cat fall on your keyboard <NICK>?']).replace('<NICK>', nick))
    
    def kick(self, channel, nick, reason):
        for chan in CHANNELS:
            if chan[0] == channel:
                print 'Rejoining ' + channel
                if chan[1] is None:
                    helpers.join(self.client, channel)
                else:
                    helpers.join(self.client, channel, chan[1])
                break


#Create client connection to The CAT's IRC server
client = IRCClient(EnigmaBotHandler,
        host=HOST, port=PORT, nick=NICK, real_name=REAL_NAME, blocking=True, ssl=True,
        connect_cb=connect_callback)

connection = client.connect()
while True:
    connection.next()
