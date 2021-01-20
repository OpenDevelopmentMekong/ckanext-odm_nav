from ckanext.odm_nav.controller import DonorReport, GeoserverNewWMSResource
from ckanext.odm_nav.thumbnail import Controller
import ckan.lib.helpers as h
from flask import Blueprint
import logging

log = logging.getLogger(__name__)

odm_nav_views = Blueprint("odm_nav", "odm_nav")


def redirect_base_url_to_dataset():
    return h.redirect_to('dataset.search')


def thumbnail_read(id, resource_id, filename=None):
    thumbnail_controller = Controller()
    return thumbnail_controller.read(id, resource_id, filename=filename)


def donor_report_index(id):
    donor_report_controller = DonorReport()
    return donor_report_controller.index(id)


def new_mws_resource(id, data=None, errors=None, error_summary=None):
    geoserver_new_resource_controller = GeoserverNewWMSResource()
    return geoserver_new_resource_controller.new_mws_resource(id, data=data, errors=errors, error_summary=error_summary)


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
    "/dataset/new_geoserver_resource/<id>", methods=["GET"], view_func=new_mws_resource,
)
