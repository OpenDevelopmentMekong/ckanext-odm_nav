from ckan.controllers.user import UserController
from ckan.controllers.package import PackageController
from ckanext.odm_nav import utils


class DonorReport(UserController):
    """
    Donor Report Controller for ckan 2.8
    """
    def index(self, id=None):
        return utils.donor_report_index(id)


class GeoserverNewWMSResource(PackageController):

    def new_mws_resource(self, id, data=None, errors=None, error_summary=None):
        data = utils.set_resource_format_wms(c, data)
        return self.new_resource(id, data, errors, error_summary)

