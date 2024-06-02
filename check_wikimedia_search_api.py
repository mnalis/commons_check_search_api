# for fiding best solution to https://github.com/commons-app/apps-android-commons/issues/3179
# by mnalis, released under CC0 - version 20240602.1

import requests
import csv
import urllib.parse

def call_api(base_url, params):
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    response = requests.get(full_url)
    return response.json(), full_url

def find_full_matches(data, expected_result):
    matches = []
    
    def search_any(v):
        if isinstance(v, dict):
            search_dict(v)
        elif isinstance(v, list):
            search_list(v)
        elif isinstance(v, str) and expected_result in v:
            matches.append(v)
    
    def search_dict(d):
        for k, v in d.items():
            search_any(v)

    def search_list(lst):
        for v in lst:
            search_any(v)
    
    search_any(data)
    return matches

def process_api(api_name, base_url, params, search_term, expected_result, must_not_match):
    # Replace None values in params with the search term
    params = {k: (search_term if v is None else v) for k, v in params.items()}
    result, full_url = call_api(base_url, params)
    matches = find_full_matches(result, expected_result)
    matched_text = ', '.join(f'"{match}"' for match in matches) if matches else None
    tooltip = matched_text if matches else '---'
    display_text = 'matched' if matches else 'no'
    good_or_bad = ':heavy_check_mark:' if ((matches and not must_not_match) or (not matches and must_not_match)) else ':x:'
    return good_or_bad, display_text, tooltip, full_url

def main():
    apis = [
        {
            "name": "HotCat90",
            "url": "https://commons.wikimedia.org/w/api.php",
            "params": {
                "format": "json",
                "action": "query",
                "list": "allpages",
                "apnamespace": 14,
                "aplimit": 50,
                "apfrom": None,  # Placeholder for the search term
                "apprefix": None  # Placeholder for the search term
            }
        },
        {
            "name": "Special:UploadWizard90",
            "url": "https://commons.wikimedia.org/w/api.php",
            "params": {
                "action": "opensearch",
                "format": "json",
                "formatversion": 2,
                "namespace": 14,
                "limit": 50,
                "search": None  # Placeholder for the search term
            }
        }
    ]
    
    results = []
    # format of input.csv is: search_term|expected_result|must_not_match
    # must_not_match inverts the logic; with default "0" our search_term must much expected_results, but with "1" it must not match it (e.g. for testing failing to match hidden categories)
    with open('input.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|')
        for row in reader:
            search_term, expected_result, must_not_match = row
            must_not_match=bool(int(must_not_match))
            row_result = [expected_result, search_term]
            for api in apis:
                good_or_bad, display_text, tooltip, full_url = process_api(api['name'], api['url'], api['params'], search_term, expected_result, must_not_match)
                tooltip = tooltip.replace('"', r'\"')
                row_result.append(f'{good_or_bad} [{display_text}]({full_url} "{tooltip}")')
            results.append(row_result)

    header = ["Expected Result", "Search Term"] + [api["name"] for api in apis]
    
    with open('output.md', 'w') as file:
        file.write('| ' + ' | '.join(header) + ' |\n')
        file.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
        for row in results:
            file.write('| ' + ' | '.join(row) + ' |\n')

if __name__ == "__main__":
    main()
