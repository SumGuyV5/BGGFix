import os
from BGGModule.ReadXML import ReadXML

from BGGFix import BGGFixBase


class BGGRestoreBackup(BGGFixBase):
    def __init__(self):
        super().__init__()
        self.backup = []
        self.current = []
        self.restore = []
        self.backup_dir = os.path.join(os.getcwd(), "Backup/plays")
        self.backup_count = 12

    def main(self):
        """

        :return: None
        """
        # self.retrieve_xml()  # downloads all the xml files with the info we need
        self.read_xml()  # reads the xml files and finds all the id's for the recorded plays that need to be fix.
        self.login_bgg()  # login
        self.play_edit_all()

    def edit_attrib(self, form):
        lst = ['dateinput', 'location', 'quantity', 'length', 'incomplete', 'nowinstats']
        lst2 = ['players[']
        for key, value in form.items():
            if key in lst[0]:
                if value != self.current_play.date:
                    form[key] = self.current_play.date_str()
            elif key in lst:
                val = self.current_play.__getattribute__(key)
                if type(val) is bool:
                    val = int(val)
                form[key] = str(val)
            elif key in lst2:
                pass

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
    main = BGGRestoreBackup()
    main.main()