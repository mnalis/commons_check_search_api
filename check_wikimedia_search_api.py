#!/usr/bin/python3
# for finding best solution to Wikimedia Commons category search at  https://github.com/commons-app/apps-android-commons/issues/3179
# by mnalis, released under CC0 - version 20240603.2

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
    # Replace "%search_term%" in params with the actual search term
    params = {k: (v.replace("%search_term%", search_term) if isinstance(v, str) else v) for k, v in params.items()}
    result, full_url = call_api(base_url, params)
    matches = find_full_matches(result, f'Category:{expected_result}')
    # hover-over "title" tooltip
    tooltip = ', '.join(matches) if matches else '---'
    display_text = 'match' if matches else 'no'
    good_or_bad = ':heavy_check_mark:' if ((matches and not must_not_match) or (not matches and must_not_match)) else ':x:'
    return good_or_bad, display_text, tooltip, full_url

def main():
    WM_API = "https://commons.wikimedia.org/w/api.php"
    apis = [
        {
            "name": "HotCat",
            "url": WM_API,
            "params": {
                "format": "json",
                "action": "query",
                "list": "allpages",
                "apnamespace": 14,
                "aplimit": 90,
                "apfrom": "%search_term%",  # Placeholder for the search term
                "apprefix": "%search_term%"  # Placeholder for the search term
            }
        },
        {
            "name": "Special:UW",
            "url": WM_API,
            "params": {
                "format": "json",
                "action": "opensearch",
                "formatversion": 2,
                "namespace": 14,
                "limit": 90,
                "search": "%search_term%"  # Placeholder for the search term
            }
        },
        {
            "name": "app1",
            "url": WM_API,
            "params": {
                "format": "json",
                "action": "query",
                "formatversion": 2,
                "generator": "search",
                "gsrnamespace" : 14,
                "gsrlimit": 90,
                "gsroffset": 0,
                "gsrsearch": "%search_term%"  # Placeholder for the search term
            }
        },
        {
            "name": "gsr_intitle",
            "url": WM_API,
            "params": {
                "format": "json",
                "action": "query",
                "formatversion": 2,
                "generator": "search",
                "gsrnamespace" : 14,
                "gsrlimit": 90,
                "gsroffset": 0,
                "gsrsearch": "intitle:%search_term%"  # Placeholder for the search term
            }
        },
        {
            "name": "app2",
            "url": WM_API,
            "params": {
                "format": "json",
                "action": "query",
                "formatversion": 2,
                "generator": "allcategories",
                "gaclimit": 90,
                "gacoffset": 0,
                "gacprefix": "%search_term%"  # Placeholder for the search term
            }
        },
# not used, see https://github.com/commons-app/apps-android-commons/issues/3179#issuecomment-2144416029
#        {
#            "name": "app3",
#            "url": WM_API,
#            "params": {
#                "format": "json",
#                "action": "query",
#                "formatversion": 2,
#                "generator": "categorymembers",
#                "gcmtype": "subcat",
#                "prop": "info", 
#                "gcmlimit": 500,
#                "gcmtitle": "Category:%search_term%"  # Placeholder for the search term
#            }
#        },
#        {
#            "name": "app4",
#            "url": WM_API,
#            "params": {
#                "format": "json",
#                "action": "query",
#                "formatversion": 2,
#                "generator": "categories",
#                "prop": "info", 
#                "gcllimit": 500,
#                "titles": "%search_term%"  # Placeholder for the search term
#            }
#        },
    ]
    
    results = []
    # format of input.csv is: search_term|expected_result|must_not_match
    # must_not_match inverts the logic; with default "0" our search_term must much expected_results, but with "1" it must not match it (e.g. for testing failing to match hidden categories)
    with open('input.csv', 'r') as file:
        reader = csv.reader(file, delimiter='|', quotechar=None)
        for row in reader:
            expected_result, search_term, must_not_match, description = row
            must_not_match=bool(int(must_not_match))
            tooltip_description = description.replace('"', r'\"')
            category_url = f'https://commons.wikimedia.org/wiki/Category:{expected_result}'
            row_result = [f'[{expected_result}]({category_url}) "{tooltip_description}"']
            row_result.append(search_term)
            for api in apis:
                good_or_bad, display_text, tooltip_matches, full_url = process_api(api['name'], api['url'], api['params'], search_term, expected_result, must_not_match)
                tooltip_matches = tooltip_matches.replace('"', r'\"')
                row_result.append(f'{good_or_bad} [{display_text}]({full_url} "{tooltip_matches}")')
            results.append(row_result)

    header = ["Expected Result", "Search Term"] + [api["name"] for api in apis]
    
    with open('output.md', 'w') as file:
        file.write('| ' + ' | '.join(header) + ' |\n')
        file.write('| ' + ' | '.join(['---'] * len(header)) + ' |\n')
        for row in results:
            file.write('| ' + ' | '.join(row) + ' |\n')

if __name__ == "__main__":
    main()
