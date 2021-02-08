from ckanext.odm_nav.utils import donor_report_index, set_resource_format_wms
from ckanext.odm_nav.thumbnail import read
import ckan.lib.helpers as h
from ckan.common import _, c
from ckan.views.resource import CreateView
from flask import Blueprint, make_response
import logging

log = logging.getLogger(__name__)

odm_nav_views = Blueprint("odm_nav", __name__)


def redirect_base_url_to_dataset():
    return h.redirect_to('dataset.search')


def thumbnail_read(id, resource_id, filename=None):
    img_bytes, content_type = read(id, resource_id, filename=filename)
    response = make_response(img_bytes)
    response.headers['Content-type'] = content_type
    response.headers['cache-control'] = "max-age=86400"
    return response


def index(id=None):
    return donor_report_index(id)


class GeoserverResourceCreateView(CreateView, object):
    def get(self, id, data=None, errors=None, error_summary=None):
        data = set_resource_format_wms(c, data)
        return super(CreateView, self).get(id, data=data, errors=errors, error_summary=error_summary)


odm_nav_views.add_url_rule(
    "/", methods=["GET"], view_func=redirect_base_url_to_dataset,
)

odm_nav_views.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/thumbnail",
    methods=["GET"], view_func=thumbnail_read, defaults={'filename': None}
)
odm_nav_views.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/thumbnail/<filename>",
    methods=["GET"], view_func=thumbnail_read
)

odm_nav_views.add_url_rule(
    "/user/<id>/donor_report", methods=["GET"], view_func=donor_report_index,
)

odm_nav_views.add_url_rule(
    "/dataset/new_geoserver_resource/<id>", methods=["GET", "POST"], view_func=CreateView.as_view(str(u'new')),
)
