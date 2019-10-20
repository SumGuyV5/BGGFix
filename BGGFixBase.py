import time
import requests
import configparser
import lxml.html
import BGGModule.Functions
from BGGModule.DownloadXML import DownloadXML


class BGGFixBase:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("creds")

        self.bgg_user = config.get('BGG', 'user')  # board game geek username that all the plays are recorded under.
        self.bgg_password = config.get('BGG', 'pass')  # board game geek password.

        self.pagesize = 100  # how many plays per xml file. 100 is the max.
        self.session = None
        self.dryRun = True  # if True don't change the name this is just a dry run.
        # how many xml files do we need to download
        self.count_to = BGGModule.Functions.count_to(self.bgg_user, self.pagesize)

        self.play_nums = []  # list of play numbers to fix
        self.current_play = None

    def run(self):
        """

        :return: None
        """
        # self.retrieve_xml()  # downloads all the xml files with the info we need
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

    @staticmethod
    def player_count(form):
        count = 0
        for key, value in form.items():
            try:
                if 'username' in key:
                    count += 1
            except KeyError:
                print(f'Error {value}')
        return count

    @staticmethod
    def checkbox_check(x):
        found = False
        value = '0'
        if x.attrib['type'] == 'checkbox':
            found = True
            if 'checked' in x.attrib:
                value = '1'

        return found, value

    def edit_attrib(self, form):
        pass

    def found_attrib(self, x):
        return True

    def found_play(self, play_num):
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
                found_check, value = self.checkbox_check(x)
                if found_check:
                    form[x.attrib["name"]] = value
                else:
                    form[x.attrib["name"]] = x.attrib["value"]
                if not found:
                    found = self.found_attrib(x)
            except KeyError:
                form[x.attrib["name"]] = ''
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
        found, form = self.found_play(play_num)
        if found:
            print(f'{play_num} was found.')
        else:
            print(f'{play_num} was Not found.')
            return

        self.edit_attrib(form)

        if self.dryRun:
            print('This is a dry run. We will stop here.')
            return  # this is a dry run so stop here and don't save the changes.

        time.sleep(2)  # lets not hit the server to hard
        self.session.post('https://www.boardgamegeek.com/geekplay.php', data=form)

        found, form = self.found_play(play_num)
        if found:
            print(f'{play_num} was found.')
        else:
            print(f'{play_num} was Not found.')

    def play_edit_all(self):
        """
        Prints out the total number of play records to be edit and the current play being edited.
        :return:
        """
        for idx, play_num in enumerate(self.play_nums):
            print('====================================')
            print(f'Play {idx + 1} of {len(self.play_nums)}')
            print('====================================')
            self.current_play = play_num
            self.play_edit(play_num.id)

    def retrieve_xml(self):
        """
        Download all the plays from board game geek.

        :return: None
        """
        url = f'http://www.boardgamegeek.com/xmlapi2/plays?username={self.bgg_user}&pagesize={str(self.pagesize)}&page='
        download_xml = DownloadXML()
        download_xml.download_all(url, "plays", self.count_to)

    def read_xml(self):
        pass
