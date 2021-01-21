from ckanext.odm_nav.controller import donor_report_index, set_resource_format_wms
from ckanext.odm_nav.thumbnail import read
import ckan.lib.helpers as h
from ckan.common import _, c
from ckan.views.resource import CreateView
from flask import Blueprint
import logging

log = logging.getLogger(__name__)

odm_nav_views = Blueprint("odm_nav", "odm_nav")


def redirect_base_url_to_dataset():
    return h.redirect_to('dataset.search')


def thumbnail_read(id, resource_id, filename=None):
    return read(id, resource_id, filename=filename)


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
    "/dataset/<id>/resource/<resource_id>/thumbnail/<file_name>", methods=["GET"], view_func=thumbnail_read,
)
odm_nav_views.add_url_rule(
    "/dataset/<id>/resource/<resource_id>/thumbnail", methods=["GET"], view_func=thumbnail_read,
)

odm_nav_views.add_url_rule(
    "/user/<id>/donor_report", methods=["GET"], view_func=donor_report_index,
)

odm_nav_views.add_url_rule(
    "/dataset/new_geoserver_resource/<id>", methods=["GET", "POST"], view_func=CreateView.as_view(str(u'new')),
)
