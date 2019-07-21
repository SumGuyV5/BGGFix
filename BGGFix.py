#!/usr/bin/python
import configparser
import os
import sys

import lxml.html
import requests

from BGGModule.DownloadXML import DownloadXML
from BGGModule.ReadXML import ReadXML

import BGGModule.Functions

sys.path.append('BGGModule.zip')


class BGGFix:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("creds")

        self.name = "Richard"  # the name to be search for and found.
        self.name_to = "Richard Allen"  # what name should be renamed to.
        self.bgg_user = config.get('BGG', 'user')  # board game geek username that all the plays are recorded under.
        self.bgg_password = config.get('BGG', 'pass')  # board game geek password.
        self.pagesize = 100  # how many plays per xml file. 100 is the max.
        self.play_num = []  # list of play numbers to fix
        self.s = None
        self.dryRun = True  # if True don't change the name this is just a dry run.
        # how many xml files do we need to download
        self.count_to = BGGModule.Functions.play_count(self.bgg_user, self.pagesize)

    def main(self):
        self.retrieve_xml()  # downloads all the xml files with the info we need
        self.read_xml()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.

    def login_bgg(self):
        """Logins in to BGG using username and password."""
        self.s = requests.session()

        login = self.s.get('https://www.boardgamegeek.com/login')
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

        form['username'] = self.bgg_user
        form['password'] = self.bgg_password

        response = self.s.post('https://www.boardgamegeek.com/login', data=form)

        if self.bgg_user in response.text:
            print("%s is logged in." % self.bgg_user)
        else:
            print("%s could not be logged in." % self.bgg_user)
            quit()

    def play_edit(self):
        page = self.s.get('https://www.boardgamegeek.com/play/edit/35817904')

        if self.bgg_user in page.text:
            print(f'{self.bgg_user} is logged in.')
        else:
            print(f'{self.bgg_user} is not logged in.')
            quit()

        page_html = lxml.html.fromstring(page.text)

        hidden_inputs = page_html.xpath(r'//form[@id="quickplay_form1"]//input')
        form = {}

        for x in hidden_inputs:
            try:
                if x.attrib["type"] == "checkbox" and x.attrib["checked"] == "checked":
                    # if it's a checkbox and it is checked add it
                    form[x.attrib["name"]] = x.attrib["value"]
                else:
                    if x.attrib["value"] == self.name:
                        form[x.attrib["name"]] = self.name_to
                    else:
                        form[x.attrib["name"]] = x.attrib["value"]
            except KeyError:
                print('Error %s' % x.attrib["name"])

        print(form)
        # response = self.s.post('https://www.boardgamegeek.com/geekplay.php', data=form)

    def retrieve_xml(self):
        url = f'http://www.boardgamegeek.com/xmlapi2/plays?username={self.bgg_user}&pagesize={str(self.pagesize)}&page='
        download_xml = DownloadXML()
        download_xml.download_all(url, "plays", self.count_to)

    def read_xml(self):
        read_xml = ReadXML()
        read_xml.read_xml_all(os.path.join(os.getcwd(), "plays"), self.count_to)

        for play in read_xml.plays:
            idx = play.find_player_by_name(self.name)
            if idx != -1:
                self.play_num.append(play.id)
        print(self.play_num)


if __name__ == "__main__":
    bgg_fix = BGGFix()
    bgg_fix.main()
