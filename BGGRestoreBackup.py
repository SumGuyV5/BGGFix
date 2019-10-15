import os
import time
import lxml.html
import requests
import configparser
import BGGModule.Functions

from BGGModule.DownloadXML import DownloadXML
from BGGModule.ReadXML import ReadXML


class BGGRestoreBackup:
    def __init__(self):
        config = configparser.RawConfigParser()
        config.read("creds")

        self.backup = []
        self.current = []
        self.restore = []
        self.backup_dir = os.path.join(os.getcwd(), "Backup/plays")
        self.backup_count = 12
        self.bgg_user = config.get('BGG', 'user')  # board game geek username that all the plays are recorded under.
        self.bgg_password = config.get('BGG', 'pass')  # board game geek password.
        self.pagesize = 100  # how many plays per xml file. 100 is the max.
        self.play_nums = []  # list of play numbers to fix
        self.session = None
        self.dryRun = True  # if True don't change the name this is just a dry run.
        # how many xml files do we need to download
        self.count_to = BGGModule.Functions.count_to(self.bgg_user, self.pagesize)

    def main(self):
        """

        :return: None
        """
        #self.retrieve_xml()  # downloads all the xml files with the info we need
        self.read_xml()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.
        self.login_bgg()  # login
        self.play_restore_all()

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

        return found, str(value)

    def play_found(self, play_num):
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
            found = True

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
            except KeyError:
                form[x.attrib["name"]] = ''
                print(f'Error {x.attrib["name"]}')

        print(form)

        return found, form

    def play_restore(self, play):
        """
        We go to the play that is to be change and read the data off of the page.
        We then make the need change and pass the changes to geekplay.php to save.

        :param play: The play number to edit.
        :return: None
        """
        lst = ['location', 'quantity', 'length', 'incomplete', 'nowinstats']
        found, form = self.play_found(play.id)
        if found:
            print(f'{play.id} was found.')
        else:
            print(f'{play.id} was Not found.')
            return

        for key, value in form.items():
            if key == 'dateinput':
                if value != play.date:
                    form[key] = play.date_str()
            else:
                if key in lst:
                    val = play.__getattribute__(key)
                    if type(val) is bool:
                        val = int(val)
                    form[key] = str(val)


        print(form)

        if self.dryRun:
            print('This is a dry run. We will stop here.')
            return  # this is a dry run so stop here and don't save the changes.

        time.sleep(2)  # lets not hit the server to hard
        self.session.post('https://www.boardgamegeek.com/geekplay.php', data=form)

        found, form = self.play_found(play.id)
        if found:
            print(f'{self.change_from} was found.')
        else:
            print(f'{self.change_from} was Not found.')
            return

    def play_restore_all(self):
        """
        Prints out the total number of play records to be edit and the current play being edited.
        :return:
        """
        for idx, play in enumerate(self.restore):
            print('====================================')
            print(f'Play {idx + 1} of {len(self.restore)}')
            print('====================================')
            self.play_restore(play)

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
        self.current = read_xml.plays

        read_xml.read_xml_all(self.backup_dir, self.backup_count)
        self.backup = read_xml.plays

        for cur in self.current:
            for back in self.backup:
                if cur.id == back.id:
                    if cur != back:
                        self.restore.append(back)

if __name__ == "__main__":
    main = BGGRestoreBackup()
    main.main()