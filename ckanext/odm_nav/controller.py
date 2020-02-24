import csv, codecs, cStringIO
import StringIO
from ckan.lib.base import BaseController, render, abort
from ckan.common import _, c, request, response
import ckan.plugins as p
import ckan.model as model
import ckan.logic as logic
import ckan.lib.helpers as h
from ckan.controllers.user import UserController
from ckanext.odm_nav import validators
import logging

log = logging.getLogger(__name__)
check_access = logic.check_access
ValidationError = logic.ValidationError


class UnicodeDictWriter:
    """
    Mod for CSV DICT writer UTF-8
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        """
        Convert dictionary values if not null to utf-8
        :param row: dict
        :return: None
        """
        item = dict()
        for k, v in row.iteritems():
            # Cannot encode if its none type
            try:
                if v:
                    v = v.encode("utf-8")
                if k:
                    k = k.encode("utf-8")
            except AttributeError as e:
                # Numbers cannot be encoded
                pass
            item[k] = v

        self.writer.writerow(item)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for item in rows:
            self.writerow(item)

    def writeheader(self):
        self.writer.writeheader()


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
                writer = UnicodeDictWriter(file_object, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()

                # For each row in a data
                for row in data:
                    writer.writerow(dict(row))
            except Exception as e:
                log.error("Error while writing row")
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

    def _process_raw_data(self, from_dt, to_dt):
        """
        :return: csv response
        """
        query = """
            SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
            PUBLIC.group.title AS org_title, TRIM(p.pkg_taxonomy) AS pkg_taxonomy, 
            TRIM(p.parent_taxonomy) AS parent_taxonomy 
            FROM PUBLIC.group, (SELECT 
            pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
            FROM (SELECT 
            package.id AS pkg_id, package.title AS title, package.type AS type, 
            package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
            TRANSLATE(unnest(string_to_array(package_extra.value, ',')), '[]"', '') AS pkg_taxonomy 
            FROM package, package_extra 
            WHERE package.state = 'active'
            AND (
                    package.metadata_created 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    OR package.metadata_modified 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    )
            AND package.id = package_extra.package_id 
            AND package_extra.key = 'taxonomy') AS tb 
            LEFT JOIN odm_taxonomy 
            ON LOWER(TRANSLATE(tb.pkg_taxonomy, ' ', '')) = LOWER(TRANSLATE(odm_taxonomy.taxonomy, ' ', ''))) AS p 
            WHERE PUBLIC.group.id = p.org;
        """.format(from_dt=str(from_dt), to_dt=str(to_dt))

        conn = model.Session.connection()
        res = conn.execute(query).fetchall()

        return self._download(res, "odm_raw_data")

    def _process_gp_pkg(self, from_dt, to_dt):
        """

        :return:
        """
        query = """
              SELECT raw_data.pkg_type AS pkg_type, TRIM(raw_data.parent_taxonomy) as parent_taxonomy, 
              COUNT(raw_data.pkg_id) AS pkg_count 
              FROM (SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
              PUBLIC.group.title AS org_title, p.pkg_taxonomy AS pkg_taxonomy, p.parent_taxonomy AS parent_taxonomy
              FROM PUBLIC.group, (SELECT 
              pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
              FROM (SELECT 
              package.id AS pkg_id, package.title AS title, package.type AS type, 
              package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
              TRANSLATE(unnest(string_to_array(package_extra.value, ',')), '[]"', '') AS pkg_taxonomy 
              FROM package, package_extra 
              WHERE package.state = 'active'
              AND (
                    package.metadata_created 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    OR package.metadata_modified 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                  )
              AND package.id = package_extra.package_id 
              AND package_extra.key = 'taxonomy') AS tb 
              LEFT JOIN odm_taxonomy 
              ON LOWER(TRANSLATE(tb.pkg_taxonomy, ' ', '')) = LOWER(TRANSLATE(odm_taxonomy.taxonomy, ' ', ''))) AS p 
              WHERE PUBLIC.group.id = p.org) as raw_data
              GROUP BY pkg_type, parent_taxonomy
              ORDER BY pkg_count DESC;
        """.format(from_dt=str(from_dt), to_dt=str(to_dt))
        log.info(query)
        conn = model.Session.connection()
        res = conn.execute(query).fetchall()

        return self._download(res, "odm_group_by_dataset")

    def _process_gp_org(self, from_dt, to_dt):
        """

        :return:
        """
        query = """
                SELECT PUBLIC.group.title as org_title, gp.pkg_type as pkg_type, gp.pkg_count as pkg_count, 
                gp.parent_taxonomy as parent_taxonomy
                FROM(SELECT raw_data.pkg_type AS pkg_type, raw_data.parent_taxonomy as parent_taxonomy,
                raw_data.org_id as org_id, COUNT(raw_data.pkg_id) AS pkg_count 
                FROM (SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
                PUBLIC.group.title AS org_title, p.pkg_taxonomy AS pkg_taxonomy, p.parent_taxonomy AS parent_taxonomy
                FROM PUBLIC.group, (SELECT 
                pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
                FROM (SELECT 
                package.id AS pkg_id, package.title AS title, package.type AS type, 
                package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
                TRANSLATE(unnest(string_to_array(package_extra.value, ',')), '[]"', '') AS pkg_taxonomy 
                FROM package, package_extra 
                WHERE package.state = 'active'
                AND (
                      package.metadata_created 
                      BETWEEN '{from_dt}' AND '{to_dt}'
                      OR package.metadata_modified 
                      BETWEEN '{from_dt}' AND '{to_dt}'
                    )
                AND package.id = package_extra.package_id 
                AND package_extra.key = 'taxonomy') AS tb 
                LEFT JOIN odm_taxonomy 
                ON LOWER(TRANSLATE(tb.pkg_taxonomy, ' ', '')) = LOWER(TRANSLATE(odm_taxonomy.taxonomy, ' ', ''))) AS p 
                WHERE PUBLIC.group.id = p.org) as raw_data
                GROUP BY org_id, pkg_type, parent_taxonomy
                ORDER BY pkg_count DESC) as gp, PUBLIC.group
                WHERE gp.org_id = PUBLIC.group.id;
                """.format(from_dt=str(from_dt), to_dt=str(to_dt))
        log.info(query)
        conn = model.Session.connection()
        res = conn.execute(query)
        return self._download(res, "odm_group_by_org")

    def _process_pkg_sdg(self, from_dt, to_dt):
        """
        Count of all SDGs
        :param from_dt: str
        :param to_dt: str
        :return: str
        """
        query = """
            SELECT raw_data.pkg_type AS pkg_type, raw_data.pkg_taxonomy as pakcage_taxonomy, count(raw_data.pkg_id) AS pkg_count 
            FROM (SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
            PUBLIC.group.title AS org_title, p.pkg_taxonomy AS pkg_taxonomy, p.parent_taxonomy AS parent_taxonomy
            FROM PUBLIC.group, (SELECT 
            pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
            FROM (SELECT 
            package.id AS pkg_id, package.title AS title, package.type AS type, 
            package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
            TRANSLATE(unnest(string_to_array(package_extra.value, ',')), '[]"', '') AS pkg_taxonomy 
            FROM package, package_extra 
            WHERE package.state = 'active'
            AND (
                    package.metadata_created 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    OR package.metadata_modified 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    )
            AND package.id = package_extra.package_id 
            AND package_extra.key = 'taxonomy') AS tb 
            LEFT JOIN odm_taxonomy 
            ON LOWER(TRANSLATE(tb.pkg_taxonomy, ' ', '')) = LOWER(TRANSLATE(odm_taxonomy.taxonomy, ' ', ''))) AS p 
            WHERE PUBLIC.group.id = p.org
            AND LOWER(TRANSLATE(p.parent_taxonomy, ' ', '')) = 'sustainabledevelopmentgoals'
            ) as raw_data
            GROUP BY pkg_type, pkg_taxonomy
            ORDER BY pkg_count DESC;
        """.format(from_dt=str(from_dt), to_dt=str(to_dt))
        log.info(query)
        conn = model.Session.connection()
        res = conn.execute(query)
        return self._download(res, "odm_group_by_pkg_sdg")

    def _process_org_sdg(self, from_dt, to_dt):
        """
        Count of all SDGs
        :param from_dt: str
        :param to_dt: str
        :return: str
        """
        query = """
            SELECT PUBLIC.group.title as org_title, gp.pkg_type as pkg_type, gp.pkg_count as pkg_count, 
            gp.pkg_taxonomy as pkg_taxonomy
            FROM(SELECT raw_data.pkg_type AS pkg_type, raw_data.pkg_taxonomy as pkg_taxonomy,
            raw_data.org_id as org_id, COUNT(raw_data.pkg_id) AS pkg_count 
            FROM (SELECT p.pkg_id AS pkg_id, p.title AS pkg_title, p.type AS pkg_type, p.org AS org_id, 
            PUBLIC.group.title AS org_title, p.pkg_taxonomy AS pkg_taxonomy, p.parent_taxonomy AS parent_taxonomy
            FROM PUBLIC.group, (SELECT 
            pkg_id, title, type, pkg_state, private, org, pkg_taxonomy, taxonomy AS odm_taxonomy, parent_taxonomy 
            FROM (SELECT 
            package.id AS pkg_id, package.title AS title, package.type AS type, 
            package.state AS pkg_state, package.private AS private, package.owner_org AS org, 
            TRANSLATE(unnest(string_to_array(package_extra.value, ',')), '[]"', '') AS pkg_taxonomy 
            FROM package, package_extra 
            WHERE package.state = 'active'
            AND (
                    package.metadata_created 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    OR package.metadata_modified 
                    BETWEEN '{from_dt}' AND '{to_dt}'
                    )
            AND package.id = package_extra.package_id 
            AND package_extra.key = 'taxonomy') AS tb 
            LEFT JOIN odm_taxonomy 
            ON LOWER(TRANSLATE(tb.pkg_taxonomy, ' ', '')) = LOWER(TRANSLATE(odm_taxonomy.taxonomy, ' ', ''))) AS p 
            WHERE PUBLIC.group.id = p.org
            AND LOWER(TRANSLATE(p.parent_taxonomy, ' ', '')) = 'sustainabledevelopmentgoals'
            ) as raw_data
            GROUP BY org_id, pkg_type, pkg_taxonomy
            ORDER BY pkg_count DESC) as gp, PUBLIC.group
            WHERE gp.org_id = PUBLIC.group.id;
        """.format(from_dt=str(from_dt), to_dt=str(to_dt))
        log.info(query)
        conn = model.Session.connection()
        res = conn.execute(query)
        return self._download(res, "odm_group_by_org_sdg")

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
            vars['data'] = data_dict
            return render('user/donor_report.html', extra_vars=vars)

        if request.method == "POST":
            _parms = request.params
            if "run" in _parms:
                report_type = data_dict['report_type'] = _parms.get('report_type', '')
                data_dict['from_dt'] = _parms.get('from_dt', '')
                data_dict['to_dt'] = _parms.get('to_dt', '')
                try:
                    # TODO: Optimize this CKAN way
                    for key in ('from_dt', 'to_dt'):
                        err = validators.validate_date(key, data_dict, vars['errors'])
                        if err:
                            raise ValidationError("Not a valid date")
                    err = validators.check_date_period(data_dict, vars['errors'])
                    if err:
                        raise ValidationError

                    if not report_type:
                        raise ValidationError('Not a valid report type. Please select the proper report type')

                    if report_type == 'Raw Data':
                        return self._process_raw_data(data_dict['from_dt'], data_dict['to_dt'])
                    elif report_type == "Group By Dataset":
                        return self._process_gp_pkg(data_dict['from_dt'], data_dict['to_dt'])
                    elif report_type == "Group By Organization":
                        return self._process_gp_org(data_dict['from_dt'], data_dict['to_dt'])
                    elif report_type == "Group By Dataset SDG":
                        return self._process_pkg_sdg(data_dict['from_dt'], data_dict['to_dt'])
                    elif report_type == "Group By Organization SDG":
                        return self._process_org_sdg(data_dict['from_dt'], data_dict['to_dt'])
                    else:
                        # This should not occur
                        vars['errors'] = ["Unkown Report Type"]
                        vars['error_summary'] = "Unkown Report Type: {}".format(report_type)
                        raise ValidationError("Unkown Report Type")

                except ValidationError as e:
                    msg = e.error_dict['message']
                    h.flash_error(_(msg))
                    vars['data'] = data_dict
                    return render('user/donor_report.html', extra_vars=vars)
            else:
                donor_report_page = h.url_for(
                    controller='ckanext.odm_nav.controller:DonorReport',
                    action='index',
                    id=id
                )
                h.flash_error(_("Something went wrong contact sysadmin"))
                h.redirect_to(donor_report_page)
