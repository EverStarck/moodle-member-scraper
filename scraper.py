import requests as r
import re
from bs4 import BeautifulSoup
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

urlLogin = os.environ.get("URL_LOGIN")       # Login url of your moodle page
urlScrape = os.environ.get("URL_SCRAPE")     # Page with the list of your class
defaultPass = os.environ.get("DEFAULT_PASS") # Default password to set. Ex: email:defaultPass


USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
headers = {"user-agent": USER_AGENT}

req = r.session()
usersLink = []

# Login to moodle page
def login():
    req.headers.update(headers)
    res = req.get(urlLogin)
    loginTokenRegex = re.compile(
        'type="hidden" name="logintoken" value="(\w*)"', re.IGNORECASE)
    Ltoken = loginTokenRegex.search(res.text).group(1)
    res2 = req.post(urlLogin, data={
        "ajax": True,
        "anchor": "",
        "logintoken": Ltoken,
        "username": os.environ.get("USERNAME"),
        "password": os.environ.get("PASSWORD"),
        "token": "",
    })
    print(res2.status_code)

# Get moodle user link
def getMemberList():
    for i in range(0, 3):
        html = req.get(f"{urlScrape}{i}", headers=headers).content
        table = str(BeautifulSoup(html, "html.parser").findAll('td', attrs={'class': 'cell'}))
        url = BeautifulSoup(table, "html.parser").findAll('a')

        # Save all page links in this array
        usersLinkPage = []
        for j in range(0, len(url)):
            urlString = str(url[j])
            aHref = BeautifulSoup(urlString, "html.parser").find('a')['href']
            usersLinkPage.append(aHref)

        # Combine all links into a single array
        global usersLink
        usersLink += usersLinkPage


def getEmail():
    for i in range(0, len(usersLink)):
        html = req.get(usersLink[i], headers=headers).content
        mailParent = BeautifulSoup(html, "html.parser").find('dd')
        mail = mailParent.find('a')
        if mail:
            mail = mail.text
            mail = re.sub("@.*", ":" + defaultPass, mail)
        else:
            mail = usersLink[i]

        # Check if file exist
        try:
            print("Getting emails...")
            with open("Output.txt", "a") as file:
                file.write(f'{mail}\n')
        except (IOError,):
            print("Creating file...")
            with open("Output.txt", "w") as file:
                file.write(f'{mail}\n')


login()
getMemberList()
getEmail()
