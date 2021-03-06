#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import ckan
from urlparse import urlparse, urlunparse
from urllib import quote_plus
from dateutil.parser import parse
import os
import requests
from six import text_type

from ckan.common import config, _, c
from ckan import logic, model

from ckan.plugins import toolkit
from ckan.plugins.toolkit import request

from collections import OrderedDict
from webhelpers.html import tags

# This is to get the current language resource display name
from ckanext.odm_dataset_ext import helpers as dt_helpers
from ckanext.vectorstorer import wms as v_wms

from . import menus

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR)

class _helpers(object):
    def __getattr__(self, key):
        return toolkit.h[key]
helpers = _helpers()
h = helpers

taxonomy_dictionary = 'taxonomy'

DATASET_ICON_MAP =  OrderedDict([("dataset", " fa-database"),
                                 ("library_record", " fa-book"),
                                 ("laws_record", " fa-gavel"),
                                 ("agreement", " fa-handshake-o"),
                                 ("profile", " fa-briefcase"),
                                 ("map", " fa-map-marker fa-md")])


# memoization decorator from http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
# mit license
def memoize(f):
    class memoize(dict):
        def __missing__(self, key):
            ret = self[key] = f(key)
            return ret
    return memoize().__getitem__

def localize_resource_url(url):
    '''Converts a absolute URL in a relative, chopping out the domain'''

    try:
        p = urlparse(url)
        return urlunparse(('','',p.path, p.params, p.query, p.fragment))
    except:
        return url

def thumbnail_img_url(url):
    return url.replace('/download/', '/thumbnail/')

def get_tag_dictionaries(vocab_id):
    '''Returns the tag dictionary for the specified vocab_id'''

    try:
        tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': vocab_id})
        return tag_dictionaries
    except toolkit.ObjectNotFound:
        return []


def get_taxonomy_dictionary():
    '''Returns the tag dictionary for the taxonomy'''

    return get_tag_dictionaries(taxonomy_dictionary)


def get_localized_tag(tag):
    '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

    lang = request.environ['CKAN_LANG']
    return _get_localized_tag((tag, lang))

@memoize
def _get_localized_tag((tag, lang)):
    '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

    log.debug('odm_nav_get_localized_tag: %s', tag)

    translations = ckan.logic.action.get.term_translation_show(
        {'model': ckan.model},
        {'terms': (tag)})

    for translation in translations:
        if translation['lang_code'] == lang:
            return translation['term_translation']
        # This is for fall back to english
        elif translation['lang_code'] == "en":
            return translation['term_translation']

    return tag

def get_localized_tag_string(tags_string):
    '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

    lang = request.environ['CKAN_LANG']

    return ",".join([_get_localized_tag((tag.strip(), lang))
                     for tag in tags_string.split(',')])


def tag_for_topic(topic):
    '''Return the name of the tag corresponding to a top topic'''

    log.debug('tag_for_topic')

    tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
    return tag_name if len(tag_name)<=100 else tag_name[0:99]

def popular_groups():
    '''Return a sorted list of the groups with the most datasets.'''

    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'packages desc', 'all_fields': True})

    groups = groups[:10]
    return groups

def popular_datasets(limit):
    '''Return a sorted list of the most popular datasets.'''

    result_dict = toolkit.get_action('package_search')(
        data_dict={'sort': 'views_recent desc', 'rows': limit})

    return result_dict['results']


def get_library_for_doctype(document_type):
    result = toolkit.get_action('package_search')(data_dict={'fq_list': ['+type:library_record',
                                                                         '+document_type:%s' % document_type],
                                                             'rows':1000})
    return result['results']


def tag_for_topic(topic):
    '''Return the name of the tag corresponding to a top topic'''

    log.debug('tag_for_topic')

    tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
    return tag_name if len(tag_name)<=100 else tag_name[0:99]

def recent_datasets():
    '''Return a sorted list of the datasets updated recently.'''

    dataset = toolkit.get_action('current_package_list_with_resources')(
        data_dict={'limit': 10})

    return dataset


def sanitize_html(s):
    s = ''.join(ch for ch in s if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' '))
    s = s.replace(' ','-').lower()
    return s


#Helpers for data preview_resource


def predict_if_resource_will_preview(resource_dict):
    format = resource_dict.get('format')

    if not format:
        return False

    normalised_format = format.lower().split('/')[-1]
    accepted_formats = (('csv', 'xls', 'rdf+xml', 'owl+xml', 'xlsx',
                                  'xml', 'n-triples', 'turtle', 'plain',
                                  'txt', 'atom', 'tsv', 'rss',
                                  'geojson', 'kml', 'json-stat',
                                  'doc', 'docx', 'pdf',
                                  'jpeg', 'jpg', 'png', 'gif','wms', 'json'))
    # Check format is TSV or CSV but url doesn't end in that extension
    if normalised_format in ('csv', 'tsv'):
        # Get url file extension
        url = resource_dict.get('url')
        tmp = url.split('/')
        tmp = tmp[len(tmp) - 1]
        tmp = tmp.split('?')
        tmp = tmp[0]
        ext = tmp.split('.')

        file_extension = None
        if len(ext) > 1: #Because a filename with /only/ an extension doesn't make much sense
            file_extension = ext[-1]
        if file_extension:
            return file_extension in ('csv', 'tsv')
        else:
            #Get the downloaded file extension from the server (workaround for CKAN /dump URLs)
            #Inspired by CKAN resourceproxy code but much simpler here
            try:
                r = requests.head(url)
                cd = r.headers.get('Content-Disposition', '')
                filename = cd.split('filename')[1].split('"')[1]
            except:
                return False

            ext = filename.split('.')
            file_extension = None
            if len(ext) > 0:
                file_extension = ext[-1]

            if file_extension:
                return file_extension in ('csv', 'tsv')
            else:
                return False

    else:
        return normalised_format in accepted_formats


def _get_preview_priority(dataset_type):
    default_preview_priority = (
        # if there are image resource, we want to show them first as they are fast to load
        'jpeg', 'jpg', 'png', 'gif',
        # if we have a kml resource we want to show that next
        'wms',
        # if we don't have kml, try wms and then geojson
        'kml', 'geojson',
        # no geojson, maybe json-stat?
        'json-stat',
        # welp, now it's tables I guess
        'csv', 'tsv', 'xls', 'xlsx',
        # and json
        'json',
        # no table? probably a pdf :(
        'pdf',
        # maybe a doc or ppt?
        'doc',
        'docx',
        'ppt',
        'pptx'
        # not that? no need to preview
    )
    preview_priority_laws_agreement_library = (
        # pdf should be priority for laws, library and agreement
        'pdf',
        # docs, ppt next on preview order
        'doc',
        'docx',
        'ppt',
        'pptx'
        # if there are image resource, we want to show them first as they are fast to load
        'jpeg', 'jpg', 'png', 'gif',
        # welp, now it's tables I guess
        'csv', 'tsv', 'xls', 'xlsx',
        # if we have a kml resource we want to show that next
        'wms',
        # if we don't have kml, try wms and then geojson
        'kml', 'geojson',
        # no geojson, maybe json-stat?
        'json-stat',
        # and json
        'json'
    )
    if dataset_type in ('library_record', 'laws_record', 'agreement'):
        return preview_priority_laws_agreement_library
    else:
        return default_preview_priority


def resource_to_preview_on_dataset_page(pkg):
    resources = pkg.get('resources')
    possible_resources = {}
    for resource in resources:
        if not resource.get('format', None):
            continue
        normalised_format = resource.get('format').lower().split('/')[-1]
        if (predict_if_resource_will_preview(resource)):
            if (not possible_resources.get(normalised_format)):
                possible_resources[normalised_format] = []
            possible_resources[normalised_format].append(resource)

    preview_priority = _get_preview_priority(pkg.get('type', ''))
    view_types_priority = [
        'geo_view',
        'jsonstat_view',
        'text_view'
    ]

    for possible_format in preview_priority:
        rsrc_format_group = possible_resources.get(possible_format, [])

        if rsrc_format_group:
            context ={}

            for resc in rsrc_format_group:
                try:
                    resource_views = toolkit.get_action('resource_view_list')(
                        context, {'id': resc.get('id')})
                except Exception as e:
                    log.debug('resource_view debug from action resource_view_list: %s', e)
                    continue

                for rv in resource_views:
                    if possible_format in ('csv', 'tsv', 'xls', 'xlsx'):
                        if resc.get('datastore_active'):
                            rv['resource_name'] = dt_helpers.resource_display_name(resc)
                            rv['resource_url'] = resc['url']
                            return rv
                    else:
                        rv['resource_name'] = dt_helpers.resource_display_name(resc)
                        rv['resource_url'] = resc['url']
                        return rv

    return None

def active_search_link():

    # List of path to identify as current active path
    path_list = ['/agreement', '/library_record', '/dataset', '/laws_record']
    active_path = {}

    for path in path_list:

        if path == h.current_url():

            active_path[path.replace("/", '')] = True
        else:

            active_path[path.replace("/", '')] = False

    return active_path

def gen_odm_menu(list_element, lang, first_pass=True):
    items = []

    link_template = '<a href="%s" %s>%s%s</a>'
    if len(list_element) == 0:
        return ""
    else:
        if first_pass:
            items.append('<ul class="nav navbar-nav">')
            first_pass=False
        else:
            items.append('<ul class="dropdown-menu">')

        for element in list_element:
            items.append('<li>')

            child_span = ""
            atts = ""
            if len(element['child_menus']) != 0:
                child_span = '<span class="caret"></span>'
                # disabled here means "able to click on the link'. sigh.
                # if it's missing, the root of a dropdown can't be clicked on.
                atts = """class="dropdown-toggle disabled" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false" """

            items.append(link_template %(element['url'],
                                         atts,
                                         element.get('title_translated',{}).get(lang, element['title']),
                                         child_span))

            items.append(gen_odm_menu(element['child_menus'], lang, first_pass))
            items.append('</li>')

        items.append('</ul>')

        return "".join(items)

def sitecode():
    return config.get('ckanext.odm.site_code')

def ckan_url_for_site(sitecode=None):
    if not sitecode:
        sitecode = config.get('ckanext.odm.site_code')
    return config.get("ckanext.odm.%s_url" % sitecode, "")

def wp_url_for_site(sitecode=None):
    if not sitecode:
        sitecode = config.get('ckanext.odm.site_code')
    return config.get("ckanext.odm.%s_wp_url" % sitecode, "")

def megamenu_css_url_for_site(sitecode=None):
    """
      "https://thailand.opendevelopmentmekong.net/wp-content/uploads/sites/5/maxmegamenu/style.css?ver=d2ec35"
      " https://odt.odm-eu.staging.derilinx.com/wp-content/uploads/maxmegamenu/style.css?ver=630c06"
    """
    site_id_map = { 'odc': '2',
                    'odl': '3',
                    'odmy': '4',
                    'odt': '5',
                    'odv': '6'}

    if not sitecode:
        sitecode = config.get('ckanext.odm.site_code')
    site_id = site_id_map.get(sitecode,None)
    if not site_id:
        return "%s/wp-content/uploads/maxmegamenu/style.css" % wp_url_for_site(sitecode)
    return "%s/wp-content/uploads/sites/%s/maxmegamenu/style.css" % (wp_url_for_site(sitecode), site_id)


def country_name_for_site(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')
    names = {'odm': 'Mekong',
             'odmy': 'Myanmar',
             'odt': 'Thailand',
             'odl': 'Laos',
             'odc': 'Cambodia',
             'odv': 'Vietnam'}
    return names.get(site,'')

def twitter_for_site(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')

    username = {'odm': 'opendevmekong',
            'odmy': 'opendevmm',
            'odt': 'opendevthai',
            'odl': 'opendevlaos',
            'odc': 'opendevcam',
            'odv': ''}.get(site,'')

    if username:
        return """<a href="https://twitter.com/%s" target="_blank" rel="external" title="Twitter"><i class="fa fa-twitter-square"></i></a>""" % username
    return ""

def contact_for_site(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')

    link = {'odm': 'contact',
            'odmy': 'contacts',
            'odt': 'contacts',
            'odl': 'contacts',
            'odc': 'contact',
            'odv': 'contact-us'}.get(site,'')

    if link:
        return """<a href="%s/%s/" title="Subscribe"><i class="fa fa-envelope"></i></a>""" % (wp_url_for_site(site), link)
    return ""

def facebook_for_site(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')

    username = {'odm': 'opendevmekong',
                'odmy': 'opendevmm',
                'odt': 'OpenDevThailand',
                'odl': 'OpenDevLaos',
                'odc': 'OpenDevCam',
                'odv': 'opendevvn'}.get(site,'')

    if username:
        return """<a href="https://www.facebook.com/%s/" target="_blank" rel="external" title="Facebook"><i class="fa fa-facebook-official"></i></a>""" % username
    return ""


def odm_nav_menu(site=None):
    if not site:
        site = config.get('ckanext.odm.site_code')
    return menus.extract_wp_menu(wp_url_for_site(site))

def odm_menu_path():
    site = config.get('ckanext.odm.site_code')
    lang = request.environ['CKAN_LANG']
    if site == 'odm':
        # we only have english on ODM
        lang = 'en'
    return "home/snippets/{}_{}_menu.html".format(site, lang)


def get_bounding_box_from_package(package):
    """
    Get the package from the bounding box
    :param package: xml tree type
    :return: tuple
    """

    bbox_west = package.get('EX_GeographicBoundingBox_west', '')
    bbox_north = package.get('EX_GeographicBoundingBox_north', '')
    bbox_south = package.get('EX_GeographicBoundingBox_south', '')
    bbox_east = package.get('EX_GeographicBoundingBox_east', '')

    bbox = (
        bbox_west, bbox_south, bbox_east, bbox_north
    )

    return bbox


def get_styles_for_given_layer(layer):
    """
    extract styles for a given layer. Style may be multiple
    :param layer: xml tree type
    :return: tuple
    """
    styles = [x.find(v_wms.ns('Name')).text for x in layer.findall(v_wms.ns('Style'))]

    return tuple(styles)


def download_wms_layers_link_given_formats(package, url, layer_name, formats,
                                           width=None, height=None, is_html_links=True):
    """
     Get download links for given wms layer and formats

    e.g: /geoserver/wms?service=WMS&
        request=GetMap&layers=ODCambodia%3AReserved_land_for_social_land_concession_points_en
        &srs=EPSG:32648
        &bbox=357678.513323801,%201182912.10854474,%20703184.839163763,%201575378.42709723
        &width=600&height=800&format=kmlz

    Supported Formats:
        - png
        - jpeg
        - kmlz
        - geotiff

    :param package: dict
    :param url: str
    :param layer_name: str <workspace:layer_name>
    :param formats: tuple (containing required formats)
    :param width: int/str numbers
    :param height: int/str numbers
    :param is_html_links: boolean (if true returns html list elements else returns tuple of urls
    :return:
    """
    request_type = "GetMap"
    service = "WMS"
    link_templ = """
        <li class="dropdown-item"><a target='_blank' href='%s'>%s 
        <i class="fa fa-download" aria-hidden="true"></i></a></li>
    """
    format_mapping = {
        "png": "image/png",
        "jpeg": "image/jpeg",
        "kmz": "kmz",
        "geotiff": "image/geotiff",
        "kml (compressed)": "kmz"
    }
    try:
        _width = int(width)
        _height = int(height)
    except Exception as e:
        log.error(e)
        log.info("Setting height and width to default 600, 600")
        _width = 600
        _height = 600

    dl_url_templ = "{url_scheme}://{net_loc}" \
                   "{url_path}?service={service}&request={request}&layers={layers}&" \
                   "srs={srs}&bbox={bbox}&width={width}&height={height}&format={format_type}"

    bbox = get_bounding_box_from_package(package)
    srs = package.get('MD_DataIdentification_spatialReferenceSystem', '').upper()
    if srs and srs.strip().lower() == "epsg:32648":
        srs = "CRS:84"
    try:
        _parsed_url = urlparse(url)
        url_scheme, url_netloc, url_path = _parsed_url.scheme, _parsed_url.netloc, _parsed_url.path
    except Exceptionn as e:
        log.error(e)
        return

    results = []

    for _format in formats:
        val = format_mapping.get(_format.lower().strip(), '')
        if val:
            if is_html_links:
                dl_url = dl_url_templ.format(
                    url_scheme=url_scheme,
                    net_loc=url_netloc,
                    url_path=url_path,
                    service=service,
                    request=request_type,
                    layers=layer_name,
                    srs=srs,
                    bbox=", ".join(list(bbox)),
                    width=_width,
                    height=_height,
                    format_type=val
                )
                if is_html_links:
                    results.append(link_templ % (dl_url, _(_format)))
                else:
                    results.append(dl_url)

    if results:
        return tuple(results)
    else:
        return


def odm_wms_raster_vector(resource, package):
    """
    Check if the wms resource is raster or vector. If vector parent resource_id should be db_table
    Returns true if vector
    :param resource: list
    :param package: dict
    :return: Boolean
    """

    _parent_resource_id = resource.get('parent_resource_id', '')
    if _parent_resource_id:
        try:
            parent_resource = [x for x in package['resources'] if x.get('id') == _parent_resource_id or x.get('name')
                               == _parent_resource_id][0]
            if parent_resource.get('format', '').strip().lower() == "db_table" or resource.get(
                    'vectorstorer_resource', '') == "vectorstorer_db":
                return True
            return False
        except IndexError as e:
            log.error("No parent resource for the given wms resource: {}".format(resource.get('id')))
            return False
    else:
        return False


def odm_wms_download(resource, package, large=True):
    """
    Check if the resource is wms raster or vector file. If the resource contains parent
    :param package:
    :param resource:
    :param large:
    :return:
    """
    is_vector = odm_wms_raster_vector(resource, package)

    try:
        ows_server = resource['wms_server'].replace('/wms', '/')
        layer = resource['wms_layer']
    except:
        return ''
    namespace = ''

    try:
        namespace, layer_name = layer.split(':',1)
        namespace = "%s/" % namespace
    except: pass

    ows_templ = "%s%sows?service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputFormat=%s%s"
    link_templ = """<li class="dropdown-item"><a target='_blank' href='%s'>%s <i class="fa fa-download" aria-hidden="true"></i></a></li>"""
    # templ % (ows_server, namespace, layer, output_format)

    layer = quote_plus(layer)

    def _url(fmt):
        options = format_options.get(fmt, '')
        return ows_templ % (ows_server, namespace, layer, quote_plus(fmt), options)

    if is_vector:
        output_formats = [(_('GeoJSON'), 'application/json'),
                          (_('KML'), 'application/vnd.google-earth.kml+xml'),
                          (_('Shapefile'), 'geopackage')]

        # Note -- we're inlining the format options here, requires geoserver 2.17.0
        # fixes an issue with SHP files coming back in ISO8859, killing the Khmer layer info
        format_options = {'SHAPE-ZIP': '&format_options=CHARSET:UTF-8'}
        dl_list = "\n".join([link_templ % (_url(fmt), name) for name, fmt in output_formats])

        return """<span class='dropdown'>
           <a class='btn btn-primary btn-download %s' resource_id="%s" id="a_wms_dl_%s" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">%s
             <span class="caret"></span>
             </a>
           <div class='dropdown-menu' aria-labelledby="a_wms_dl_%s">
                 %s
           </div>
         </span>""" % (large and "btn-block btn-lg" or "",
                           resource['id'],
                           resource['id'],
                           _('Download'),
                           resource['id'],
                           dl_list)

    return ""

def odm_wms_download_res(resource, package, large=True):
    """
    Check if the resource is wms raster or vector file. If the resource contains parent
    :param package:
    :param resource:
    :param large:
    :return:
    """
    is_vector = odm_wms_raster_vector(resource, package)
    format_options = {'SHAPE-ZIP': '&format_options=CHARSET:UTF-8'}
 
    try:
        ows_server = resource['wms_server'].replace('/wms', '/')
        layer = resource['wms_layer']
    except:
        return ''
    namespace = ''

    try:
        namespace, layer_name = layer.split(':',1)
        namespace = "%s/" % namespace
    except: pass

    ows_templ = "%s%sows?service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputFormat=%s%s"
    layer = quote_plus(layer)

    def _url(fmt):
        options = format_options.get(fmt, '')
        return ows_templ % (ows_server, namespace, layer, quote_plus(fmt), options)

    if is_vector:
        output_formats = [(_('GeoJSON'), 'application/json'),
                          (_('KML'), 'application/vnd.google-earth.kml+xml'),
                          (_('Shapefile'), 'geopackage')]

        downloads = dict()
        for name, fmt in output_formats:
            downloads[name] = _url(fmt)
        return downloads

    return ""


# From core ckan.lib.helpers.linked_user
def linked_user(user, maxlength=0, avatar=20):
    if not isinstance(user, model.User):
        user_name = text_type(user)
        user = model.User.get(user_name)
        if not user:
            return _("A User")
    if user:
        name = user.id
        displayname = user.name

        if maxlength and len(user.display_name) > maxlength:
            displayname = displayname[:maxlength] + '...'

        if c.userobj:
            if c.userobj.sysadmin:
                # Sysadmins can see names, link to the user page
                return tags.literal(u'{icon} {link}'.format(
                    icon=h.gravatar(
                        email_hash=user.email_hash,
                        size=avatar
                    ),
                    link=tags.link_to(
                        displayname,
                        h.url_for('user.read', id=name)
                    )
                ))
            else:
                return user.name
        return _("A User")


# Monkeypatching the builtin.
h.linked_user = linked_user

def get_title_for_languages_facet(language_code):
    return h.odm_dataset_get_resource_name_for_field_value('odm_language', language_code)

def get_icon_for_dataset_type(dataset_type):
    return DATASET_ICON_MAP.get(dataset_type, '')

def get_icon_dataset_type_for_facet(items):

    required_order = []
    for element in DATASET_ICON_MAP:
        try:
            ele = filter(lambda item: item['name'] == element, items)[0]
            ele['icon'] = DATASET_ICON_MAP[ele.get('name')]
            required_order.append(ele)
        except IndexError:
            pass

    return required_order


def get_active_url_for_search_result_facet():

    try:
        current_url = h.current_url().split("?")[0].strip('/')
        active_url = current_url.split("?")[0].strip('/')
        return active_url
    except Exception as e:
        log.debug('Error in fetching the active ur for Search Result For facet: %s', str(e))

    return ""

def get_tag_list(pkg):
    lang = request.environ['CKAN_LANG']
    return ', '.join(sorted(taxonomy_path_to_name(path, lang)
                            for path in taxonomy_paths_from_tags(pkg.get('tags',[])) if path != ('',)
    ))

def get_lang_flags(pkg):
    langs = pkg.get('MD_DataIdentification_language',pkg.get('odm_language', []))
    base_url = wp_url_for_site('odm')
    return ' '.join('<img class="lang_flag" alt="%s" src="%s/wp-content/themes/wp-odm_theme/img/%s.png">' %(lang, base_url, lang)
                    for lang in langs)

taxonomy = {}

def _load_taxonomy():
    global taxonomy
    if not taxonomy:
        with open(os.path.join(os.path.dirname(__file__), 'odm-taxonomy','2.2', 'hierarchy.json')) as f:
            taxonomy = json.load(f)

def taxonomy_paths_from_tags(tags):
    _load_taxonomy()
    log.debug([tag for tag in tags])
    return set(tuple(taxonomy['tag_to_path'].get(tag.get('name',''), '').split(',')) for tag in tags)

def taxonomy_path_to_name(tag_path, lang):
    """ Tag path as a tuple """
    _load_taxonomy()
    path_string = ','.join(str(s) for s in tag_path)
    return taxonomy['translations'].get(path_string, {})[lang]


def _add_additional_items_to_menu(menu_items):
    remove_items = ['Search']
   
    for _rm_item in remove_items:
        for _item in menu_items:
            if _item.get('title', 'NA').strip().lower() == _rm_item.strip().lower():
                menu_items.remove(_item)

    lang = request.environ['CKAN_LANG']
    items_to_add = [
                    {u'title': u'Organizations',
                     u"url":u"/organization",
                     u"index_to_add": 3,
                     u'child_menus': []}
                   ]

    for _item in items_to_add:
        _index = _item.get('index_to_add')
        _item[u"title_translated"] = {lang:_get_localized_tag((_item.get('title'), lang))}
        if len(menu_items) > _index:
            log.debug("Adding addition navidation item: {}".format(_item.get('post_title')))
            menu_items.insert(_index, _item)
        else:
            log.debug("Navigation item cannot be inserted")
    return menu_items

def get_ga_tracking_id():
    """
    Gets the current site Google Analytics Tracking id
    """
    site = config.get('ckanext.odm.site_code')
    tracking_id = {'odm': "'UA-52846113-1'",
            'odmy': "'UA-79798225-1'",
            'odt': "'UA-79740098-1'",
            'odl': "'UA-79794223-1'",
            'odc': "'UA-64869623-1'",
            'odv': "'UA-79799309-1'"}

    return tracking_id.get(site, '')

def prepare_site_nav_mobile():
    site_title = country_name_for_site()
    _literal = """
               <svg class="svg-od-logo {}-logo odm-nv-logos"><use
                   xlink:href="#icon-od-logo"></use>
               </svg>
               """.format(site_title.lower())
    return h.literal(_literal)


def parse_datetime_string_to_object(value):
    """
    Parse string to datetime object
    """
    try:
        res = parse(value)
        return res
    except Exception as e:
        log.error(e)
    return value
