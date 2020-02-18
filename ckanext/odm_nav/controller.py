import csv
import StringIO
from ckan.lib.base import BaseController, render, abort
from ckan.common import _, c, request, response
import ckan.plugins as p
import ckan.model as model
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.controllers.user import UserController
import logging

log = logging.getLogger(__name__)
check_access = logic.check_access
ValidationError = logic.ValidationError


class DonorReport(UserController):
    """

    """

    def _download(self, data, action_name):
        """
        Donwload the files given data and field names
        :param data: orm instance
        :param fieldnames: list of table columns
        :return: csv response
        """
        file_object = StringIO.StringIO()
        fieldnames = None
        for _r in data:
            fieldnames = list(dict(_r).keys())
            break
        if fieldnames:
            try:
                writer = csv.DictWriter(file_object, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()

                # For each row in a data
                for row in data:
                    writer.writerow(dict(row))
            except Exception as e:
                log.error(e)
                pass
            finally:
                result = file_object.getvalue()
                file_object.close()

            file_name = "{}".format(action_name)
            p.toolkit.response.headers['Content-type'] = 'text/csv'
            p.toolkit.response.headers['Content-disposition'] = 'attachment;filename=%s.csv' % str(file_name)
            return result
        else:
            raise ValidationError("No data found for the given report type")

    def _process_raw_data(self):
        """
        :return: csv response
        """
        query = """
            SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
            PUBLIC.group.title AS org_title, p.pkg_taxonomy AS pkg_taxonomy, p.parent_taxonomy AS parent_taxonomy 
            FROM PUBLIC.group, (SELECT 
            pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
            FROM (SELECT 
            package.id AS pkg_id, package.title AS title, package.type AS type, 
            package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
            TRANSLATE(unnest(string_to_array(package_extra.value, ', ')), '[]"', '') AS pkg_taxonomy 
            FROM package, package_extra WHERE package.state = 'active' 
            AND package.id = package_extra.package_id 
            AND package_extra.key = 'taxonomy') AS tb 
            LEFT JOIN odm_taxonomy ON tb.pkg_taxonomy = odm_taxonomy.taxonomy) AS p 
            WHERE PUBLIC.group.id = p.org;
        """
        conn = model.Session.connection()
        res = conn.execute(query).fetchall()

        return self._download(res, "odm_raw_data")

    def _process_gp_pkg(self):
        """

        :return:
        """
        query = """
             SELECT q.type AS pkg_type, q.parent_taxonomy AS parent_taxonomy, COUNT(pkg_id) AS pkg_count 
             FROM (SELECT 
             pkg_id, title, type, pkg_state, private, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
             FROM (SELECT 
             package.id AS pkg_id, package.title AS title, package.type AS type, package.state AS pkg_state, 
             package.private AS private, 
             TRANSLATE(unnest(string_to_array(package_extra.value, ', ')), '[]"', '') AS pkg_taxonomy 
             FROM package, package_extra WHERE package.state = 'active' 
             AND package.id = package_extra.package_id AND package_extra.key = 'taxonomy') AS tb 
             LEFT JOIN odm_taxonomy ON tb.pkg_taxonomy = odm_taxonomy.taxonomy) AS q 
             GROUP BY q.type, q.parent_taxonomy ORDER BY q.parent_taxonomy, pkg_count DESC;
        """
        conn = model.Session.connection()
        res = conn.execute(query).fetchall()

        return self._download(res, "odm_group_by_dataset")

    def _process_gp_org(self):
        """

        :return:
        """
        query = """
            SELECT PUBLIC.group.title AS org_title, p.type AS pkg_type, parent_taxonomy, pkg_count 
            FROM PUBLIC.group, (SELECT 
            org, type, parent_taxonomy, COUNT(pkg_id) AS pkg_count 
            FROM (SELECT 
            pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
            FROM (SELECT 
            package.id AS pkg_id, package.title AS title, package.type AS type, package.state AS pkg_state, 
            package.private AS private, package.owner_org AS org, 
            TRANSlATE(unnest(string_to_array(package_extra.value, ', ')), '[]"', '') AS pkg_taxonomy 
            FROM package, package_extra WHERE package.state = 'active' AND package.id = package_extra.package_id 
            AND package_extra.key = 'taxonomy') AS tb 
            LEFT JOIN odm_taxonomy ON tb.pkg_taxonomy = odm_taxonomy.taxonomy) AS q 
            GROUP BY q.org, q.type, q.parent_taxonomy 
            ORDER BY q.parent_taxonomy, pkg_count DESC) AS p 
            WHERE p.org = PUBLIC.group.id;
        """

        conn = model.Session.connection()
        res = conn.execute(query)
        return self._download(res, "odm_group_by_org")

    def index(self, id=None):

        context = {
            'model': model, 'session': model.Session,
            'user': c.user, 'auth_user_obj': c.userobj,
            'for_view': True
        }
        data_dict = {
            'id': id,
            'user_obj': c.userobj,
            'include_datasets': True,
            'include_num_followers': True
        }

        self._setup_template_variables(context, data_dict)

        vars = {
            "user_dict": c.user_dict,
            "errors": {},
            "error_summary": {}
        }

        # Allow to generate report only for sysadmin
        try:
            check_access('user_update', context, data_dict)
        except NotAuthorized:
            abort(403, _('Unauthorized to view or run this.'))

        if request.method == 'GET':
            return render('user/donor_report.html', extra_vars=vars)

        if request.method == "POST":
            _parms = request.params
            if "run" in _parms:
                report_type = _parms.get('report_type')

                if not report_type:
                    raise ValidationError('Not a valid report type. Please select the proper report type')
                try:
                    if report_type == 'Raw Data':
                        return self._process_raw_data()
                    elif report_type == "Group By Dataset":
                        return self._process_gp_pkg()
                    elif report_type == "Group By Organization":
                        return self._process_gp_org()
                    else:
                        # This should not occur
                        vars['errors'] = ["Unkown Report Type"]
                        vars['error_summary'] = "Unkown Report Type: {}".format(report_type)
                        raise ValidationError("Unkown Report Type")

                except ValidationError as e:
                    h.flash_error(_(e.message))
                    return render('user/donor_report.html', extra_vars=vars)
            else:
                donor_report_page = h.url_for(
                    controller='ckanext.odm_nav.controller:DonorReport',
                    action='index',
                    id=id
                )
                h.flash_error(_("Something went wrong contact sysadmin"))
                h.redirect_to(donor_report_page)
