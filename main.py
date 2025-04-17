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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global counter for valid MongoDB connections
valid_connection_count = 0

def setup_session():
    """Initialize the HTTP session and load environment variables."""
    session = requests.sessions.Session()
    load_dotenv()

    # Validate environment variables
    gh_api_token = os.getenv('GH_API_TOKEN')
    mongo_uri = os.getenv('mongo_uri')

    if not gh_api_token:
        logging.error("GH_API_TOKEN is not set in the .env file.")
        raise ValueError("GH_API_TOKEN is required.")

    if not mongo_uri:
        logging.error("mongo_uri is not set in the .env file.")
        raise ValueError("mongo_uri is required.")

    logging.info("Environment variables validated successfully.")
    return session

def extract_mongo_url(code: str) -> str | None:
    """Extract MongoDB URL from the given code snippet."""
    pattern = r"mongodb\+srv:\/\/[^\/\s]+"
    match = re.search(pattern, code)
    return match.group(0) if match else None

def test_mongo_connection(url: str) -> list | None:
    global valid_connection_count
    """Test the connection to the MongoDB server and list all databases."""
    if not url:
        logging.error("MongoDB URL is empty.")
        return None

    if url.endswith("."):
        url = url[:-1]
    try:
        client = pymongo.MongoClient(f"{url}/?retryWrites=true&w=majority")
        databases = client.list_database_names()
        client.close()
        valid_connection_count += 1  # Increment the counter for valid connections
        logging.info(f"Successfully connected to MongoDB: {url}")
        return databases

    except Exception as e:
        pass

    return None

def reset_vuln_repo(vuln_repo: dict) -> dict:
    """Reset the vulnerability repository dictionary."""
    return {
        'mongo_url': None,
        'repos_id': None,
        'code': None,
        'repos_url': [],
        'owner': None,
        'repos_file_url': None
    }

def fetch_page(session: requests.Session, ch: str, page_number: int) -> requests.Response:
    """Fetch a page of search results from the GitHub API."""
    logging.info(f"Fetching page {page_number} with prefix '{ch}', this may take a while...")
    query_params = {
        "q": f"mongodb+srv://{ch}",
        "per_page": 100,
        "sort": "indexed",
        "order": "asc",
        "page": page_number
    }
    headers = {'Authorization': f"Bearer {os.getenv('GH_API_TOKEN')}"}
    url = "https://api.github.com/search/code"

    response = session.get(url, headers=headers, params=query_params)
    if response.status_code == 403:
        logging.warning("Rate limit exceeded. Waiting for 1 minute...")
        time.sleep(61)
        response = session.get(url, headers=headers, params=query_params)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch page {page_number} with prefix '{ch}'. Status code: {response.status_code}")

    return response

def process_page_results(session: requests.Session, page_number: int, db_connection) -> list:
    global valid_connection_count
    """Process the results of a single page of search results."""
    vuln_repos = reset_vuln_repo({})
    results = []
    chars = string.ascii_lowercase + string.digits + "!"
    combinations = ["".join(c) for c in itertools.product(chars, repeat=2)]

    for ch in combinations:
        try:
            response = fetch_page(session, ch, page_number)
            page = response.json()

            if not page.get('items'):
                continue

            for item in page['items']:
                owner = item['repository']['owner']['login']
                repos_url = item['repository']['html_url']
                repos_file_url = item['html_url']
                repos_id = item['repository']['node_id']

                if CheckIfIssueExists(repos_id, db_connection):
                    continue

                code_response = session.get(repos_file_url)
                if code_response.status_code != 200:
                    logging.error(f"Failed to fetch code snippet from {repos_file_url}")
                    continue

                code_text = code_response.text
                mongo_url = extract_mongo_url(code_text)

                if not mongo_url or "localhost" in mongo_url or "127.0.0.1" in mongo_url:
                    continue

                databases = test_mongo_connection(mongo_url)
                if databases:
                    logging.info(f"Number: {valid_connection_count} Valid MongoDB URL found: {mongo_url} in repos {repos_url} with databases: {databases}")
                    vuln_repos.update({
                        'owner': owner,
                        'repos_url': repos_url,
                        'repos_file_url': repos_file_url,
                        'code': code_text,
                        'mongo_url': mongo_url,
                        'repos_id': repos_id
                    })
                    results.append(vuln_repos.copy())
                    vuln_repos = reset_vuln_repo(vuln_repos)

        except Exception as e:
            logging.error(f"Error processing prefix '{ch}': {e}")

    return results

def main():
    global valid_connection_count
    session = setup_session()
    db_connection = connect_to_mongodb(os.getenv('mongo_uri'))
    if not db_connection:
        logging.error("Failed to connect to own MongoDB instance.")
        return
    all_results = []

    for page_number in range(1, 5):
        results = process_page_results(session, page_number, db_connection)
        all_results.extend(results)

    logging.info(f"Total valid MongoDB URLs found: {len(all_results)}")
    logging.info(f"Total valid MongoDB connections established: {valid_connection_count}")

if __name__ == '__main__':
    main()