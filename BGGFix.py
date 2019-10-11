#!/usr/bin/python
import configparser
import os
import time

import lxml.html
import requests

from BGGModule.DownloadXML import DownloadXML
from BGGModule.ReadXML import ReadXML

import BGGModule.Functions


class BGGFix:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("creds")

        self.change_from = '1'  # the name to be search for and found.
        self.change_to = '0'  # what name should be renamed to.
        self.change_attrib = 'nowinstats'
        self.player = False
        self.bgg_user = config.get('BGG', 'user')  # board game geek username that all the plays are recorded under.
        self.bgg_password = config.get('BGG', 'pass')  # board game geek password.
        self.pagesize = 100  # how many plays per xml file. 100 is the max.
        self.play_nums = []  # list of play numbers to fix
        self.session = None
        self.dryRun = True  # if True don't change the name this is just a dry run.
        # how many xml files do we need to download
        self.count_to = BGGModule.Functions.play_count(self.bgg_user, self.pagesize)

    def main(self):
        """

        :return: None
        """
        self.retrieve_xml()  # downloads all the xml files with the info we need
        self.read_xml()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.
        self.login_bgg()  # login
        self.play_edit_all()

    def login_bgg(self):
        """
        Login to board game geek use self.bgg_user and self.bgg_password and checks that you logged in.
        If we can't login we tell the user and quit.

        :return: None
        """
        self.session = requests.session()

        login = self.session.get('https://www.boardgamegeek.com/login')
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

        form['username'] = self.bgg_user
        form['password'] = self.bgg_password

        response = self.session.post('https://www.boardgamegeek.com/login', data=form)

        if "GEEK.userid = 0;" in response.text:
            print(f'{self.bgg_user} could not be logged in.')
            quit()
        else:
            print(f'{self.bgg_user} is logged in.')

    def checkbox_check(self, x):
        found = False
        value = 0
        if x.attrib['type'] == 'checkbox':
            found = True
            try:
                x.attrib['checked']
                value = 1
            except KeyError:
                print(f'Error {x.attrib["name"]}')

        return found, value


    def play_key_found(self, play_num):
        """
        We check the play_num to see if the name we are looking to change is in the play record.

        :param play_num: The play number to check.
        :return: True if the name is found in the play record and dict containing the play data to alter.
        """
        found = False
        response = self.session.get(f'https://www.boardgamegeek.com/play/edit/{str(play_num)}')

        if "GEEK.userid = 0;" in response.text:
            print(f'{self.bgg_user} could not be logged in.')
            quit()
        else:
            print(f'{self.bgg_user} is logged in.')

        page_html = lxml.html.fromstring(response.text)

        hidden_inputs = page_html.xpath(r'//form[@id="quickplay_form1"]//input')
        form = {}

        for x in hidden_inputs:
            try:
                form[x.attrib["name"]] = x.attrib["value"]
                found_check, value = self.checkbox_check(x)
                if found_check:
                    form[x.attrib["name"]] = value
                if x.attrib["name"] == self.change_attrib and x.attrib["value"] == self.change_from:
                    found = True
            except KeyError:
                print(f'Error {x.attrib["name"]}')

        print(form)

        return found, form

    def play_edit(self, play_num):
        """
        We go to the play that is to be change and read the data off of the page.
        We then make the need change and pass the changes to geekplay.php to save.

        :param play_num: The play number to edit.
        :return: None
        """
        found, form = self.play_key_found(play_num)
        if found:
            print(f'{self.change_from} was found.')
        else:
            print(f'{self.change_from} was Not found.')
            return

        for key, value in form.items():
            if key == self.change_attrib and value == self.change_from:
                form[key] = self.change_to
                print(f'{key} = {value} to {key} = {self.change_to}')

        if self.dryRun:
            print('This is a dry run. We will stop here.')
            return  # this is a dry run so stop here and don't save the changes.

        time.sleep(2)  # lets not hit the server to hard
        self.session.post('https://www.boardgamegeek.com/geekplay.php', data=form)

        found, form = self.play_key_found(play_num)
        if found:
            print(f'{self.change_from} was found.')
        else:
            print(f'{self.change_from} was Not found.')
            return

    def play_edit_all(self):
        """
        Prints out the total number of play records to be edit and the current play being edited.
        :return:
        """
        for idx, play_num in enumerate(self.play_nums):
            print('====================================')
            print(f'Play {idx + 1} of {len(self.play_nums)}')
            print('====================================')
            self.play_edit(play_num)

    def retrieve_xml(self):
        """
        Download all the plays from board game geek.

        :return: None
        """
        url = f'http://www.boardgamegeek.com/xmlapi2/plays?username={self.bgg_user}&pagesize={str(self.pagesize)}&page='
        download_xml = DownloadXML()
        download_xml.download_all(url, "plays", self.count_to)

    def read_xml(self):
        """
        Reads all the xml files that were download by retrieve_xml

        :return: None
        """
        read_xml = ReadXML()
        read_xml.read_xml_all(os.path.join(os.getcwd(), "plays"), self.count_to)

        for play in read_xml.plays:
            if self.player:
                for player in play.players:
                    if player.__getattribute__(self.change_attrib) == self.change_from:
                        self.play_nums.append(play.id)
                        break
            else:
                if play.__getattribute__(self.change_attrib) == self.change_from:
                    self.play_nums.append(play.id)
        print(self.play_nums)


if __name__ == "__main__":
    bgg_fix = BGGFix()
    bgg_fix.main()
