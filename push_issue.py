import time
import pymongo.database
import requests 
import json 
import os  
from dotenv import load_dotenv
import pymongo








load_dotenv()

def get_repos_id(userDict, currentSession: requests.sessions): 
    gh_api_headers = {"Authorization": "token " + os.getenv('gh_token')}
    json_data = currentSession.get(f"https://api.github.com/repos/{userDict['owner']}/{userDict['repos_url'].split("/")[-1]}", headers=gh_api_headers, cookies=json.loads(os.getenv('burp0_cookies'))).json()
    # time.sleep(0.5)
    if json_data and json_data.get("node_id"): 
        return json_data.get("node_id")
    else: 
        raise Exception("Failed to get repos id")

def connect_to_mongodb(url):
    try:
        client = pymongo.MongoClient(url)
        return client
    except Exception as e:
        return None
def CheckIfIssueExists(repos_id, ownDBClient: pymongo.MongoClient):
    if ownDBClient:
        db = ownDBClient["GHLeakSealer"]
        collection = db["issues"]
        query = {"repos_id": str(repos_id)}
        result = collection.find(query)
        #Check if the result is not empty
        for res in result: 
            if res.get("repos_id") == str(repos_id):
                # print(f"Found issue in DB for repos {res.get('repos_id')} == {repos_id}")
                return True
        return False
    else: 
        return Exception("No connection to MongoDB")
    
def addIssueToDB(repos_id, ownDBClient: pymongo.MongoClient):
    if ownDBClient:
        db = ownDBClient["GHLeakSealer"]
        collection = db["issues"]
        query = {"repos_id": str(repos_id)}
        result = collection.insert_one(query)
        return result
    else:
        return Exception("No connection to MongoDB")
    
def push_issue_to_gh(userDict, dabaseScanned: list[str], currentSession: requests.sessions, db_client): 
    #Small func to convert the databases found to a string
    def url_to_string():
        if not userDict.get("mongo_url") or userDict.get("mongo_url") == []:
            return None
        url = userDict.get("mongo_url")
        # Just to get the cluster without the username and password to raise awareness
        url = url.split("@")[1]
        return url
    def db_to_string(): 
        return "\r\n- ".join(dabaseScanned)    

    print(f"Posting with theses databases \n- {db_to_string()} and these urls:  {url_to_string()}")
    repos_id = userDict.get("repos_id")
    json_data ={"query": "0c202ff06c8b13ded4c078a1440a8a58", "variables": {"fetchParent": False, "input": {"body": f"\n> [!WARNING]\n>  # You have an exposed mongoDB cluster containing multiple databases in this repository.\n#### Hey {userDict.get("owner")}, If you receive this issue don't panic, I am a friendly automated script looking around the internet and just to let you know that you have an **exposed mongoDB cluster in your code** that I got from this file {userDict.get("repos_file_url")}.\n\n### I was able to connect and expose those databases from your cluster: \r\n- {db_to_string()}\n\n\n\n **From these possible clusters: {url_to_string()}** \n\n\n\nA **malicious attacker could leak data and get credentials** to your or people's services/system, even if you know that no sensible information is stored inside it, it is still very dangerous. I do not know what kind of information your databases hold but a malicious attacker could easily dump all the content, please **make sure to follow these steps**: \n\n1. Put your secrets in a .env file\n2. Use a library like [dotenv](https://www.npmjs.com/package/dotenv) to load the environment variables from your file onto your code\n3. At this point, I would either suggest either using [github's tool ](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) to erase the history or you could delete the repos on Github, remove the .git folder locally and recreate a new repos with a clean history\n\nIn the future make sure to **not expose your secrets** especially your mongodb uri as it contains your username and password combination. Make sure to **create a .env file and load your environment variables into your code accordingly**.\n\n### If you like what I am doing for the community, please feel free to follow my github account @GaillardTom \n\n\n", "issueTypeId": None, "parentIssueId": None, "repositoryId": repos_id, "title": "Important: Exposed MongoDB cluster in your code"}}}
    currentSession.post("https://github.com:443/_graphql", headers=json.loads(os.getenv("burp0_headers_issue")), cookies=json.loads(os.getenv('burp0_cookies_issue')), json=json_data)
    res = addIssueToDB(repos_id, db_client)
    if res.inserted_id:
        print(f"Added issue to DB for repos {userDict.get('repos_url')}")
        return True
    else:
        print(f"Failed to add issue to DB for repos {userDict.get('repos_url')}")
        return False
    

# Could add unit test later on in another file just did that temporarily to test the function
def test_get_repos_id():
    userDict = {
        "owner": "test",
        "repos_url": "https://github.com/GaillardTom/GH-LeakSealer",
        "repos_id": "R_kgDOOHoBgw"
    }
    session = requests.sessions.Session()
    id = get_repos_id(userDict, session)
    return id ==  "R_kgDOOHoBgw"
def test_push_issue_to_gh():
    userDict = {
        "owner": "Tom",
        "repos_url": "https://github.com/GaillardTom/GH-LeakSealer",
        "repos_id": "R_kgDOOHoBgw"
        } 
    session = requests.sessions.Session()
    push_issue_to_gh(userDict, ["test", "test2", "test3"], session)

if __name__ == "__main__": 
    try:
        print(test_get_repos_id())
        test_push_issue_to_gh()
    except Exception as e:
        print(e)
        