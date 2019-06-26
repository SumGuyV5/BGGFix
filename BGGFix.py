#!/usr/bin/python
import requests, lxml.html
import os
import sys
import configparser

sys.path.append('BGGModule.zip')

from BGGModule.DownloadXML import DownloadXML
from BGGModule.ReadXML import ReadXML

import BGGModule.Functions

class BGGFix:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("creds")
        
        self.name = "Richard"                           # the name to be search for and found.
        self.nameto = "Richard Allen"                   # what name should be renamed to.
        self.bggusername = config.get('BGG', 'user')    # board game geek username that all the plays are recorded under.
        self.bggpassword = config.get('BGG', 'pass')    # board game geek password. Put your password in passwd.txt or type it in when prompted.
        self.pagesize = 100                             # how many plays per xml file. 100 is the max.
        self.playnum = []                               # list of play numbers to fix
        self.s = None
        self.dryRun = True                              # if True don't chanage the name this is just a dry run.
        # how many xml files do we need to download
        self.countto = BGGModule.Functions.PlayCount(self.bggusername, self.pagesize)

    def Main(self):
        self.XMLRetrieve()  # downloads all the xml files with the info we need

        self.XMLRead()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.
        
    def loginBGG(self):
        """Logins in to BGG using username and password."""
        self.passwordCheck()
        
        self.s = requests.session()

        login = self.s.get('https://www.boardgamegeek.com/login')
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = { x.attrib["name"]: x.attrib["value"] for x in hidden_inputs }

        form['username'] = self.bggusername
        form['password'] = self.bggpassword

        response = s.post('https://www.boardgamegeek.com/login', data=form)

        if (self.bggusername in response.text) == True:
            print("%s is logged in." % self.bggusername )
        else:
            print("%s could not be logged in." % self.bggusername)
            quit()

    def playEdit(self):
        page = self.s.get('https://www.boardgamegeek.com/play/edit/35817904')
    
        if (self.bggusername in page.text) == True:
            print("%s is logged in." % self.bggusername )
        else:
            print("%s is not logged in." % self.bggusername)
            quit()
        
        page_html = lxml.html.fromstring(page.text)


        hidden_inputs = page_html.xpath(r'//form[@id="quickplay_form1"]//input')
        form = {}

        for x in hidden_inputs:
            try:
                if x.attrib["type"] == "checkbox" and x.attrib["checked"] == "checked":
                    #if it's a checkbox and it is checked add it
                    form[x.attrib["name"]] = x.attrib["value"] 
                else:
                    if x.attrib["value"] == self.name:
                        form[x.attrib["name"]] = self.nameto
                    else:
                        form[x.attrib["name"]] = x.attrib["value"]
            except KeyError:
                print('Error %s' % x.attrib["name"])

        print(form)
        response = self.s.post('https://www.boardgamegeek.com/geekplay.php', data=form)

    def XMLRetrieve(self):
        url = "http://www.boardgamegeek.com/xmlapi2/plays?username=" + self.bggusername + "&pagesize=" + str(self.pagesize) + "&page="
        downloadXML = DownloadXML()
        downloadXML.DownloadAll(url, "plays", self.countto)

    def XMLRead(self):
        readXML = ReadXML()
        readXML.ReadXMLAll(os.path.join(os.getcwd(), "plays"), self.countto)
        idx = 0
        for play in readXML.plays:
            idx = play.FindPlayerByName(self.name)
            if idx != -1:
                self.playnum.append(play.id)
        print (self.playnum)
    

if __name__ == "__main__":
    bggfix = BGGFix()
    bggfix.Main()


    

