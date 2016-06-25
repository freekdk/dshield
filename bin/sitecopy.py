#!/usr/bin/python

# this script will connect to a web server and it is able to emulate different browsers.
# It will retrieve and save the response for later replay as part of a honeypot.

import sys
import httplib
import sqlite3
from urlparse import urlparse

if len(sys.argv) > 1:
    urlstring = sys.argv[1]
    url = urlparse(urlstring)
else:
    sys.exit('URL is required')

if len(sys.argv)>2:
    browser = sys.argv[2]
else:
    browser = 'default'

print urlstring
method = 'GET'

print browser

browserclone = {}

browserclone['default'] = {'HTTPVersion': '1.1'}

browserclone['safari807mavericks'] = {
    'HTTPVersion': '1.1',
    'Host': '%hostname%',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12',
    'Accept-Language': 'en-us',
    'Accept-Encoding': 'gzip, deflate'
};

browserclone['msiewindows8.1'] = {
    'HTTPVersion': '1.1',
    'Accept': 'application/javascript, */*;q=0.8',
    'Referer': '%referer%',
    'Accept-Language': 'en-US',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Accept-Encoding': 'gzip, deflate',
    'Host': '%hostname%',
    'Connection': 'Keep-Alive',
    'Cookie': '%cookie%'
}

browserclone['chromeonwin8.1'] = {
    'HTTPVersion': '1.1',
    'Host': '%host%',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36',
    'Referer': '%referer%',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8'
}


conn = httplib.HTTPConnection(url.netloc, timeout=10)
conn.request(method, url.path)
re = conn.getresponse()
header = re.getheaders()
body = re.read()
print body



con = sqlite3.connect('honeypot.db')

c = con.cursor()

#Creates table for SITES unique values - RefID will be  RefID
c.execute('''CREATE TABLE IF NOT EXISTS sites
            (
                ID integer primary key,
                site text,
                CONSTRAINT site_unique UNIQUE (site)
            )
        ''')
#Creates table for response HEADERS based on useragents.RefID will be IndexID
c.execute('''CREATE TABLE IF NOT EXISTS headers
            (
                RID integer,
                HeaderField text,
                dataField text
            )
        ''')

#c.execute('''CREATE TABLE IF NOT EXISTS body(ID integer primary key,RefID integer,body tag text,)''')
c.execute('''CREATE TABLE IF NOT EXISTS body
            (
                RID integer,
                body text
            )
        ''')
try:
    c.execute("INSERT INTO sites VALUES(NULL,'" + urlstring + "')")
    RefID = c.execute("SELECT ID FROM sites WHERE site='" + urlstring + "'").fetchone()
    print('Body and URL uploaded to database')
    for i in header:
        c.execute("INSERT INTO headers VALUES('" + str(RefID[0]) + "','" + i[0] + "','" + i[1] + "')")
    print('Headers uploaded to database for ' + urlstring)

    c.execute("INSERT INTO body VALUES('" + str(RefID[0]) + "','" + str(body) + "')")

except sqlite3.IntegrityError:
    print("Header and body has been uploaded already for " + urlstring)

finally:
    con.commit()


