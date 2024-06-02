import requests
import csv

def call_api(url, params):
    response = requests.get(url, params=params)
    return response.json()

def check_match(result, expected_result):
    return 'yes' if expected_result.lower() in (str(result).lower()) else 'no'

def process_api(url, params, search_term, expected_result):
    result = call_api(url, params)
    was_match_found = check_match(result, expected_result)
    return [url, expected_result, search_term, was_match_found]

def main(search_term, expected_result):
    apis = [
        {
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
        result = process_api(api['url'], api['params'], search_term, expected_result)
        results.append(result)
    
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(["API URL", "Expected Result", "Search Term", "Was Match Found"])
        writer.writerows(results)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process API calls and check for expected results.")
    parser.add_argument("search_term", type=str, help="The term to search for")
    parser.add_argument("expected_result", type=str, help="The expected result to match")

    args = parser.parse_args()

    main(args.search_term, args.expected_result)

