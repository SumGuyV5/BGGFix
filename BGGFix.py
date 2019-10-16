#!/usr/bin/python
import os
from BGGModule.ReadXML import ReadXML
from BGGFixBase import BGGFixBase


class BGGFix(BGGFixBase):
    def __init__(self):
        super().__init__()
        self.change_from = '1'  # the name to be search for and found.
        self.change_to = '0'  # what name should be renamed to.
        self.change_attrib = 'nowinstats'
        self.player = False

        self.play_nums = []  # list of play numbers to fix

    def main(self):
        """

        :return: None
        """
        # self.retrieve_xml()  # downloads all the xml files with the info we need
        self.read_xml()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.
        self.login_bgg()  # login
        self.play_edit_all()

    def edit_attrib(self, form):
        for key, value in form.items():
            if key == self.change_attrib and value == self.change_from:
                form[key] = self.change_to
                print(f'{key} = {value} to {key} = {self.change_to}')

    def found_attrib(self, x):
        if x.attrib["name"] == self.change_attrib and x.attrib["value"] == self.change_from:
            return True
        else:
            return False

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
                if str(play.__getattribute__(self.change_attrib)) == self.change_from:
                    self.play_nums.append(play.id)
        print(self.play_nums)


if __name__ == "__main__":
    bgg_fix = BGGFix()
    bgg_fix.main()
