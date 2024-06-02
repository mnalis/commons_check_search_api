import requests
import csv
import urllib.parse

def call_api(base_url, params):
    full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    response = requests.get(full_url)
    return response.json(), full_url

def find_full_matches(data, expected_result):
    matches = []
    def search_dict(d):
        for k, v in d.items():
            if isinstance(v, dict):
                search_dict(v)
            elif isinstance(v, list):
                search_list(v)
            elif isinstance(v, str) and expected_result in v:
                matches.append(v)

    def search_list(lst):
        for item in lst:
            if isinstance(item, dict):
                search_dict(item)
            elif isinstance(item, list):
                search_list(item)
            elif isinstance(item, str) and expected_result in item:
                matches.append(item)
    
    if isinstance(data, dict):
        search_dict(data)
    elif isinstance(data, list):
        search_list(data)
    
    return matches

def process_api(api_name, base_url, params, search_term, expected_result):
    # Replace None values in params with the search term
    params = {k: (search_term if v is None else v) for k, v in params.items()}
    result, full_url = call_api(base_url, params)
    matches = find_full_matches(result, expected_result)
    matched_text = ', '.join(f'"{match}"' for match in matches) if matches else ":x:"
    return matched_text, full_url

def main():
    input_file = 'input.csv'
    apis = [
        {
            "name": "HotCat",
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
            row_result = [expected_result, search_term]
            for api in apis:
                matched_text, full_url = process_api(api['name'], api['url'], api['params'], search_term, expected_result)
                row_result.append(f'[{matched_text}]({full_url})')
            results.append(row_result)
    
    header = ["Expected Result", "Search Term", "HotCat", "Special:UploadWizard"]
    table = [header] + results
    
    with open('output.md', 'w') as file:
        file.write('| ' + ' | '.join(header) + ' |\n')
        file.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
        for row in results:
            file.write('| ' + ' | '.join(row) + ' |\n')

if __name__ == "__main__":
    main()
