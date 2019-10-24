import os
import re
from BGGModule.ReadXML import ReadXML
from BGGFix import BGGFixBase


class BGGRestoreBackup(BGGFixBase):
    def __init__(self, dry_run=True):
        super().__init__(dry_run)
        self.backup = []
        self.current = []
        self.restore = []
        self.backup_dir = os.path.join(os.getcwd(), "Backup/plays")
        self.backup_count = 12

    def edit_attrib(self, form):
        """
        Take the edit data from board game geek edit form and replace the data with xml data were list in play_attrib
        and player_attrib.

        :param form: the form data from board game geek edit data.
        :return:
        """
        # play attributes to change
        play_attrib = ['dateinput', 'location', 'quantity', 'length', 'incomplete', 'nowinstats']
        # player attributes to change
        player_attrib = ['name', 'username', 'color', 'position', 'score', 'rating', 'new', 'win']
        player_names = {'Richard Allan': 'Richard Allen', 'Richard': 'Richard Allen', 'Demitre': 'Dimetre',
                        'Bula': 'Beulah', 'Plary5': 'Player 5', 'Anth': 'Anthony'}
        player_num = {}
        for key, value in form.items():
            if key in 'dateinput':
                if value != self.current_play.date:
                    form[key] = self.current_play.date_str()
            elif key in play_attrib:
                val = self.current_play.__getattribute__(key)
                if type(val) is bool:
                    val = int(val)
                form[key] = str(val)
            elif key[:7] in 'players':
                match = re.findall(r'(?<=\[).+?(?=\])', key)  # get everything between square brackets.
                player_num[match[0]] = self.current_play.players[int(match[0])]
                if player_num[match[0]] is None:
                    print('No Player Found? Was a new player add in the newer record?')
                else:
                    if match[1] == 'name':
                        if value != player_num[match[0]].name:
                            if player_names[player_num[match[0]].name] == value:
                                print(f'{value} {player_num[match[0]].name}')
                            else:
                                print('Error')
                                quit()
                    if match[1] in player_attrib:
                        if player_num[match[0]] is None:
                            print(match)
                        val = player_num[match[0]].__getattribute__(match[1])
                        if type(val) is bool:
                            val = int(val)
                        form[key] = str(val)

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
                        self.play_nums.append(back)


if __name__ == "__main__":
    bgg_fix = BGGRestoreBackup()
    bgg_fix.run()
    print([num.id for num in bgg_fix.play_nums])
    print('done')
