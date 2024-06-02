import requests
import csv
import urllib.parse

def call_api(base_url, params):
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    response = requests.get(full_url)
    return response.json(), full_url

def check_match(result, expected_result):
    return 'yes' if expected_result in str(result) else 'no'

def process_api(api_name, base_url, params, search_term, expected_result):
    result, full_url = call_api(base_url, params)
    was_match_found = check_match(result, expected_result)
    return [api_name, expected_result, search_term, was_match_found, full_url]

def main(search_term, expected_result):
    apis = [
        {
            "name": "query_apfrom",
            "url": "https://commons.wikimedia.org/w/api.php",
            "params": {
                "format": "json",
                "action": "query",
                "list": "allpages",
                "apnamespace": 14,
                "aplimit": 30,
                "apfrom": search_term,
                "apprefix": search_term
            }
        },
        {
            "name": "Special:UploadWizard",
            "url": "https://commons.wikimedia.org/w/api.php",
            "params": {
                "action": "opensearch",
                "format": "json",
                "formatversion": 2,
                "namespace": 14,
                "limit": 10,
                "search": search_term
            }
        }
    ]
    
    results = []
    for api in apis:
        result = process_api(api['name'], api['url'], api['params'], search_term, expected_result)
        results.append(result)
    
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(["API", "Expected Result", "Search Term", "Was Match Found", "API URL"])
        writer.writerows(results)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process API calls and check for expected results.")
    parser.add_argument("search_term", type=str, help="The term to search for")
    parser.add_argument("expected_result", type=str, help="The expected result to match")

    args = parser.parse_args()

    main(args.search_term, args.expected_result)
