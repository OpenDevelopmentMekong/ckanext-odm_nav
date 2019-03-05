import requests
import json
import collections

# cache the rendered versions
rendered = {}

def extract_wp_menu(wp_site_url, language_code=None):
    result = {}
    
    if not language_code:
        response = requests.get(wp_site_url+'/wp-json/odm/menu')
    else:
        response = requests.get(wp_site_url+'/'+language_code+'/wp-json/odm/menu')

    response.raise_for_status()

    try:
        return response.json()
    except:
        # invalid json:
        pass
    text = response.text
    if text.startswith('<br'):
        text = text[text.index('[{"ID'):]
        return json.loads(text)

    raise Exception("Can't parse Json response")

def get_menu(wp_site_url, language_code=None):

    menu_items = extract_wp_menu(wp_site_url, language_code)

    nav_item_meta = collections.OrderedDict()

    # Convert list object to dictionary with key as items ID
    for item in menu_items:
        nav_item_meta[str(item['ID'])] = item

    # Add a new empty list all the items to hold its children item
    for item in menu_items:
        item['child_menus'] = []

    # Attach child corresponding to its parent ID
    for item in menu_items:
        if item['menu_item_parent'] != "0":
            nav_item_meta[item['menu_item_parent']]['child_menus'].append(item)

    # Extract root elements - which is nested dic/list containing its children
    nav = [item for item in nav_item_meta.values() if item['menu_item_parent'] == '0']

    return nav



