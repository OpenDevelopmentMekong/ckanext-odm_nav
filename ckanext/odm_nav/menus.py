import requests
import json
import collections

# cache the rendered versions
rendered = {}

def extract_wp_menu(wp_site_url, language_code=None):
    result = {}

    if not language_code:
        url = wp_site_url+'/wp-json/odm/menu'
    else:
        url = wp_site_url+'/'+language_code+'/wp-json/odm/menu'

    response = requests.get(url)
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


def _parse_menu(menu_items, language_code):
    nav_item_meta = collections.OrderedDict()

    # Convert list object to dictionary with key as items ID
    for item in menu_items:
        nav_item_meta[str(item['ID'])] = item

    # Add a new empty list all the items to hold its children item
    for item in menu_items:
        item['child_menus'] = []
        # also add the title in a translated item.
        item['title_translated'] = {language_code: item['title']}

    # Attach child corresponding to its parent ID
    for item in menu_items:
        if item['menu_item_parent'] != "0":
            nav_item_meta[item['menu_item_parent']]['child_menus'].append(item)

    # Extract root elements - which is nested dic/list containing its children
    return [item for item in nav_item_meta.values() if item['menu_item_parent'] == '0'], nav_item_meta


def get_menu(wp_site_url, language_codes=None):
    """
    :param wp_site_url: a url to the wordpress site
    :param language_codes: optional array of language codes, use falsy for default language (en)
    :returns: nested array of menu item dicts.
    """
    if not language_codes:
        language_codes = [None]

    main_menu = {}
    main_flattened = {}

    for lang in language_codes:
        menu_items = extract_wp_menu(wp_site_url, lang)
        lang = lang or 'en'
        nav, flat_nav = _parse_menu(menu_items, lang)
        if lang == 'en':
            main_menu = nav
            main_flattened = flat_nav
        else:
            for mid, item in flat_nav.items():
                main_flattened[mid]['title_translated'].update(item['title_translated'])

    if main_menu:
        return main_menu

    return nav
