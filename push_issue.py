import pymongo.database
import requests 
import json 
import os  
from dotenv import load_dotenv
import pymongo
from bs4 import BeautifulSoup








burp0_data = "------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\nTEst#2 \r\n\r\n#1 \r\n\r\n\r\n# PLAY IT SAFE\r\n\r\n\r\n- test\r\n- local\r\n- admin\r\n\r\n # /[link](google.ca)\r\n\r\n> [!WARNING]\r\n> your mongoDB instance is exposed \r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"issue\"\r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"repository\"\r\n\r\n947519875\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"project\"\r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"subject_type\"\r\n\r\nIssue\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd--\r\n"

load_dotenv()

def get_repos_id(userDict, currentSession: requests.sessions): 
    
    response = currentSession.get(f"{userDict.get('repos_url')}", headers=json.loads(os.getenv('burp0_headers')), cookies=json.loads(os.getenv('burp0_cookies')))
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # First find the react-partial element
    react_partial = soup.find('react-partial', {
        "partial-name": "repos-overview",
        "data-ssr": "true",
        "data-attempted-ssr": "true"
    })
    
    # Then find the nested script element inside react-partial
    if react_partial:
        script_element = react_partial.find('script', {
            'type': 'application/json',
            'data-target': 'react-partial.embeddedData'
        })
        
        # Extract the JSON content from the script tag
        if script_element:
            json_content = script_element.string
            # Parse the JSON content
            data = json.loads(json_content)
            # Access the repository ID from the nested structure
            repository_id = data.get('props', {}).get('initialPayload', {}).get('repo', {}).get('id')
            print(f"Repository ID: {repository_id}")
            return repository_id
        else:
            return Exception("Script element not found within react-partial")
    else: 
        return Exception("No react-partial element found")

def connect_to_mongodb(url):
    try:
        client = pymongo.MongoClient(os.getenv('MONGO_URL'))
        return client
    except Exception as e:
        return None

def push_issue_to_gh(userDict, dabaseScanned: pymongo.database, currentSession: requests.sessions): 


    data = "------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"text\"\r\n\r\nTEst#2 \r\n\r\n#1 \r\n\r\n\r\n# PLAY IT SAFE\r\n\r\n\r\n- test\r\n- local\r\n- admin\r\n\r\n # /[link](google.ca)\r\n\r\n> [!WARNING]\r\n> your mongoDB instance is exposed \r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"issue\"\r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"repository\"\r\n\r\n947519875\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"project\"\r\n\r\n\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd\r\nContent-Disposition: form-data; name=\"subject_type\"\r\n\r\nIssue\r\n------geckoformboundaryb7d48b7e2f24481eab18cb4c1f2031fd--\r\n"
    currentSession.post("https://github.com:443/preview", headers=os.getenv("burp0_headers"), cookies=os.getenv('burp0_cookies'), data=data)
    

# Could add unit test later on in another file just did that temporarily to test the function
def test_get_repos_id():
    userDict = {
        "owner": "test",
        "repos_url": "https://github.com/GaillardTom/GH-LeakSealer"
    }
    session = requests.sessions.Session()
    id = get_repos_id(userDict, session)
    return id == 947519875 
if __name__ == "__main__": 
    try:
        print(test_get_repos_id())
    except Exception as e:
        print(e)
        