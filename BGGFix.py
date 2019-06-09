#!/usr/bin/python
import requests, lxml.html
from getpass import getpass

bggusername = "SumGuyV5"
bggpassword = ""

s = None

def readFile():
    rtn = ""
    
    try:
        f = open("passwd.txt","r")
        rtn = f.read()
        f.close()
    except FileNotFoundError:
        print("Password file not found.")
    return rtn

def passwordCheck():
    global bggpassword
    if not bggpassword:
        bggpassword = readFile()
        print (bggpassword)
        if not bggpassword:
            print("Please enter your bgg password : ")
            bggpassword = getpass()
    else:
        print("password hard coded")

def loginBGG():
    global s
    global bggusername
    global bggpassword
    s = requests.session()

    login = s.get('https://www.boardgamegeek.com/login')
    login_html = lxml.html.fromstring(login.text)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
    form = { x.attrib["name"]: x.attrib["value"] for x in hidden_inputs }

    form['username'] = bggusername
    form['password'] = bggpassword

    response = s.post('https://www.boardgamegeek.com/login', data=form)

    if (bggusername in response.text) == True:
        print("%s is logged in." % bggusername )
    else:
        print("%s could not be logged in." % bggusername)
        quit()

def playEdit():
    global s
    global bggusername
    global bggpassword
    page = s.get('https://www.boardgamegeek.com/play/edit/35817904')
    
    if (bggusername in page.text) == True:
        print("%s is logged in." % bggusername )
    else:
        print("%s could not be logged in." % bggusername)
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
                if x.attrib["value"] == "Richard Allen":
                    form[x.attrib["name"]] = "Richard Allan"
                else:
                    form[x.attrib["name"]] = x.attrib["value"]
        except KeyError:
            print('Error %s' % x.attrib["name"])

    print(form)
    response = s.post('https://www.boardgamegeek.com/geekplay.php', data=form)

if __name__ == "__main__":
    passwordCheck()    

    loginBGG()

    playEdit()   


    

