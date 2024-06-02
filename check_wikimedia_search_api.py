import requests
import csv
import urllib.parse
import re

def call_api(base_url, params):
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    response = requests.get(full_url)
    return response.json(), full_url

def find_matches(result, expected_result):
    result_str = str(result)
    matches = re.findall(re.escape(expected_result), result_str)
    return matches

def process_api(api_name, base_url, params, search_term, expected_result):
    # Replace None values in params with the search term
    params = {k: (search_term if v is None else v) for k, v in params.items()}
    result, full_url = call_api(base_url, params)
    matches = find_matches(result, expected_result)
    was_match_found = 'yes' if matches else 'no'
    matched_text = ', '.join(f'"{match}"' for match in matches)
    return [api_name, expected_result, search_term, was_match_found, matched_text, full_url]

def main():
    input_file = 'input.csv'
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
                "apfrom": None,  # Placeholder for the search term
                "apprefix": None  # Placeholder for the search term
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
                "search": None  # Placeholder for the search term
            }
        }
    ]
    
    results = []
    with open(input_file, 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            search_term, expected_result = row
            for api in apis:
                result = process_api(api['name'], api['url'], api['params'], search_term, expected_result)
                results.append(result)
    
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow(["API", "Expected Result", "Search Term", "Was Match Found", "Matched", "API URL"])
        writer.writerows(results)

if __name__ == "__main__":
    main()
