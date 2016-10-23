'''
Author : Bhishan Bhandari
bbhishan@gmail.com

The algorithm/procedure:
A master file named domain.txt should house domain names in the format domain.* (* = com, net, org, etc). One domain 
in each line.

For each domain name in the master file, there should be a text file in the format domain.txt which has search 
keywords one in each line.

You could at anytime add a new search keyword in the domain.txt (should be added at the end of the file). The 
program is capable to acknowledging it and making changes to the spreadsheet accordingly.

A single spreadsheet will be used for this purpose with multiple worksheets. Worksheets will have the name of the 
domain.

The format of the sheet is
datetime	keyword1	keyword2 .......keyword n
2016:07:10:7:56	3		n/a		2 
2016:07:11:7:56	1		7		5

Here the values in the keyword columns are the page number at which the domain was found in google search for 
corresponding keyword

Any addition of keywords will add up a new column in the sheet.

Any addition of new domain in the master file and stuffing keywords in the respective domain.txt will add a new 
sheet to the spreadsheet.

The program uses a mechanism to randomly select a browser user-agent for each keyword's google search.
Additionally, the program also has mechanism for explicit waits.

Uses following python modules
json
datetime
time
random
gspread
oauth2client
mechanize

'''
import json
import datetime
import time
import random
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
from json import load
import mechanize

user_agents_list = [[("User-agent","Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")],

[("User-agent","Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201")],

[("User-agent","Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.0.9) Gecko/20061206")],

[("User-agent","Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16")],

[("User-agent","Mozilla/5.0 (Macintosh; U; Intel 80486Mac OS X; en-US) AppleWebKit/528.16 (KHTML, like Gecko, Safari/528.16) OmniWeb/v622.8.0.112916")],

[("User-agent","Mozilla/5.0 (Windows; U; Win 9x 4.90; SG; rv:1.9.2.4) Gecko/20101104 Netscape/9.1.0285")],

[("User-agent","Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")],

[("User-agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36")],

[("User-agent","Mozilla/4.0 (compatible; MSIE 8.0; AOL 9.7; AOLBuild 4343.27; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)")],

[("User-agent","Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.3a) Gecko/20021207 Phoenix/0.5")],

[("User-agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A")]]

br = mechanize.Browser()
br.set_handle_robots(False)
br.addheaders = [("User-agent","Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")]

def create_timestamp(seconds):
    '''
    Returns timestamp from seconds passed.
    '''
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts-seconds).strftime('%Y-%m-%d %H:%M:%S')
    return st


def connect_to_spreadsheet(s_keywords, page_ranks, domain):
    '''
    Uses oauthclient to connect to google spreadsheet service. Takes search keywords list, page ranks and domain 
name for an individual domain as parameters. Appends the data to respective domain sheet. In case domain sheet not 
available, creates one and appends the results.
    '''
    total_keywords = len(s_keywords)
    json_key = json.load(open('StartUpViz-5e0b6bb6f4e5.json'))
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
    gc = gspread.authorize(credentials)
    wks = gc.open("SeoTracker")
    try:
        worksheet = wks.worksheet(domain) 
        last_row = worksheet.row_count
        last_col = worksheet.col_count - 1
        to_add_cols = total_keywords - last_col
        if to_add_cols > 0:
            worksheet.add_cols(to_add_cols)
            for i in range(total_keywords - to_add_cols, total_keywords):
                worksheet.update_cell(1, i+2, s_keywords[i]) 
            #add new keywords to the column  
    except:
        worksheet = wks.add_worksheet(title=domain, rows="1", cols=total_keywords + 1)
        worksheet.update_cell(1, 1, 'date')
        col = 2
        for keyw in s_keywords:
            worksheet.update_cell(1, col, keyw)
            col += 1
    worksheet.append_row(page_ranks)

def find_position_in_google(s_keyword, domain):
    '''
    Takes search keyword and domain name as parameters. Uses mechanize to instantiate browser. Randomly chooses 
user agent for the session and makes google search. Iterates over 10 search result pages. If found returns the 
result page number. If not found returns -1
    '''
    search_position = 0
    domain = domain.replace("\n", "")
    #domain = 'http://' + domain
    s_keyword = s_keyword.replace(' ', '+')
    br = mechanize.Browser()
    br.set_handle_robots(False)
    rand_user_agent = random.choice(user_agents_list)
    br.addheaders = rand_user_agent
    for i in range(10):
        try:
            final_url = "https://www.google.com/search?q=" + s_keyword + "&start=" + str(i*10)
            google_result = br.open(final_url)
            result_content = google_result.read()
            if str(domain) in result_content:
                return i+1
            time.sleep(2)
        except:
            time.sleep(11)
            print "inside except"
            #print "failed to google search", s_keyword, domain
    return -1

def analyze_individual_domain(domain):
    '''
    Reads the keywords from domain text file passed onto this method. Iterates over each search keyword and passes
each search keyword to find_position_in_google method. At the end of the iterations, saves the output obtained to 
the respective domain sheet in the format timestamp position_for_keyword1 position_for_keyword2 ...
    '''
    page_ranks = []
    s_keywords = []
    date_today = create_timestamp(0)
    page_ranks.append(date_today)
    domain_name, _ = domain.split('.')
    with open(domain_name+'.txt', 'rb') as f:
        for s_keyword in f:
            s_keyword = s_keyword.replace('\n', '')
            result = find_position_in_google(s_keyword, domain)
            if result != -1:
                page_ranks.append(result)
            else:
                page_ranks.append('n/a')
            s_keywords.append(s_keyword)
            time.sleep(4)
    connect_to_spreadsheet(s_keywords, page_ranks, domain_name)


def main():
    '''
    Reads the master file containing domain records. Iterates over each domain file name and passes onto the 
analyze_individual_domain method.
    '''
    with open('domain.txt', 'rb') as f:
        for domain in f:
            analyze_individual_domain(str(domain))

if __name__ == '__main__':
    main()
