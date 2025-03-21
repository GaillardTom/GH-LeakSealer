import html
import pymongo.errors
import requests 
import itertools
import string
from dotenv import load_dotenv
import os
import json
import re
import time
import pymongo
from push_issue import push_issue_to_gh, CheckIfIssueExists, connect_to_mongodb


def setup(): 
    global session
    session = requests.session()
    load_dotenv()
    global counter
    counter = 0
    
def getMongoURL(code): 
    #use regex to get the mongo url from the code snippet which is a string
    #Starts with mongodb+srv:// and ends .net/ or .com/
    pattern = r"mongodb\+srv:\/\/[^\/\s]+"
    # Search for all matches with the regex pattern and returns them all
    match = re.search(pattern, code)
    # print(match.string)
    if match: 
        return match.group(0) if match.group(0) else None
    else: 
        return None

def TestConnectionAndListDatabases(url):
    #Test the connection to the mongodb server and list all the databases
    #Use the pymongo library to connect to the mongodb server
    #Use the pymongo library to list all the databases
    #Return the list of databases
    if url == "" or url == None: 
        return None
    print(f"Trying to connect to {url}")
    try: 
        client = pymongo.MongoClient(url+"/?retryWrites=true&w=majority")
        databases = client.list_database_names()
        client.close()
        return databases
    except Exception as e:
        pass
            
def ResetDict(userDict):
    #Reset the dictionary to None
    userDict['mongo_url'] = None
    userDict['repos_id'] = None
    userDict['code'] = None
    userDict['repos_url'] = []
    userDict['owner'] = None
    userDict['repos_file_url'] = None
    return userDict
def getResultForPage(page_number):
    global counter 
    own_db = connect_to_mongodb(os.getenv('mongo_url')) 
    res = []
    #In the search query, we are searching for mongodb+srv://{any character} NOT is:archived
    #Include all the characters in the search query to get all the results
    #Also include numbers in the search query 
    #Also include special characters in the search query
    vuln_repos = {"owner": "", "repos_url": "", "code": "", "mongo_url": [], "repos_id": ""}
    chars = string.ascii_letters + string.digits + "!"
    combinations = ["".join(c) for c in itertools.product(chars, repeat=2)]
    for ch in combinations:
        query_params = {"q": f"mongodb+srv://{ch}", 
                         "per_page": 100, 
                         "sort": "indexed",
                         "order": "asc",
                         "page": page_number
                        }
        # time.sleep(1)
        headers = {'Authorization': 'Bearer ' + os.getenv("GH_API_TOKEN")}
        url = f"https://api.github.com/search/code"
        response = session.get(url, headers=headers, params=query_params)
        # print(response)
        if response.status_code == 403: 
            print("Rate limit exceeded waiting for 1 min...")
            time.sleep(61)
            response = session.get(url, headers=headers, params=query_params)
        if response.status_code != 200:
            return Exception(f"Failed to get pages with ch {ch}")
        print(f"Getting pages with ch {ch}")
        page = json.loads(response.content)
        if not page.get('items'):
            return Exception(f"Failed to get items from response with ch {ch}")
        for item in page['items']:
            owner = item['repository']['owner']['login']
            repos_url = item['repository']['html_url']
            repos_file_url = item['html_url']
            repos_id = item['repository']['node_id']
            if CheckIfIssueExists(repos_id, own_db):
                print(f"Issue already exists in repos {repos_url}")
                continue
            code = session.get(repos_file_url, headers=json.loads(os.getenv('burp0_headers')), cookies=json.loads(os.getenv('burp0_cookies')))
            if not code.status_code == 200 or not code or not code.text or code == None:
                print("Failed to get code snippet from: " + repos_file_url)
                continue
            # code.encoding = 'utf-8'
            possMongoUrl = html.unescape(getMongoURL(code.text).encode().decode('unicode_escape'))
            # print(f"Possible Mongo URL: {possMongoUrl}")
            if possMongoUrl and possMongoUrl != None:
                db = TestConnectionAndListDatabases(possMongoUrl)
                if db and not db == None:
                    counter += 1
                    print(f"Counter: {counter}")
                    print(f"Owner: {owner}, repos: {repos_url}, ,connection_string: {possMongoUrl}")
                    vuln_repos['owner'] = owner
                    vuln_repos['repos_url'] = repos_url
                    vuln_repos['repos_file_url'] = repos_file_url
                    vuln_repos['code'] = code.text if code.text else None
                    vuln_repos['mongo_url'] = possMongoUrl
                    vuln_repos['repos_id'] = repos_id
                    #Push the issue to github with the message
                    push_issue_to_gh(vuln_repos, db, session, own_db)
                    res.append(vuln_repos)
                    vuln_repos = ResetDict(vuln_repos)
                else: 
                    vuln_repos = ResetDict(vuln_repos)
                    pass
    
if __name__ == '__main__':
    #Start http session
    session = requests.session()
    #Load the env variables
    load_dotenv()
    #Counter to count all valid mongodb urls that I can connect to
    global counter
    counter = 0
    all_results = []
    for i in range(1, 5):
        res = getResultForPage(i)
        all_results.append(res)
        
    print(f"Total results: {counter}")