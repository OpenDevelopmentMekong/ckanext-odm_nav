import ckan.authz as authz
from ckan.common import _, config
from ckan.plugins import toolkit
from ckan.logic import check_access, NotAuthorized

from sqlalchemy import text

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def user_list(context, data_dict):
    return authz.is_authorized('sysadmin', context, data_dict)

# from _followee_list
def user_show(context, data_dict):
    model = context['model']

    # Visitors cannot see what users are following.
    authorized_user = context.get('auth_user_obj', None) or model.User.get(context.get('user'))
    if not authorized_user:
        log.debug('Requesting user is not authorized')
        return {'success': False, 'msg': _('Not authorized')}

    # Any user is authorized to see themselves.
    requested_user = data_dict.get('user_obj', None) or model.User.get(data_dict.get('id'))
    if authorized_user == requested_user:
        return {'success': True}

    # Sysadmins are authorized to see anyone.
    #return authz.is_authorized('sysadmin', context, data_dict)
    # Org admins can see anyone in their org.
    return user_is_org_admin_of_member(context, data_dict)

def user_is_org_editor(context, data_dict):
    model = context['model']

    authorized_user = model.User.get(context.get('user'))
    if not authorized_user:
        return {'success': False, 'msg': _('Not authorized')}

    requested_org = data_dict.get('id')
    # update_dataset is an editor level permission
    if authz.has_user_permission_for_group_or_org(requested_org, authorized_user.name, 'update_dataset'):
        return {'success': True}

    return {'success': False, 'msg': _('Not authorized')}


def user_is_org_admin_of_member(context, data_dict):
    """ Is the user the admin of an organization that has the target user as a member """
    model = context['model']

    authorized_user = model.User.get(context.get('user'))
    if not authorized_user:
        return {'success': False, 'msg': _('Not authorized')}

    if 'user_obj' in data_dict:
        requested_user = data_dict.get('user_obj')
    else:
        requested_user = model.User.get(data_dict.get('id'))

    #memberalias = aliased(model.Member)
    # so, member is group_id (table_name = user, table_id = user_id), ...
    # so self join here and find a group_id of the user that's an admin
    # that the requested member is a target of
    sql = """
        select count(*) from member as m1 inner join member as m2
           using (group_id)
        where m1.table_name = 'user'
        and m2.table_name = 'user'
        and m1.state = 'active'
        and m2.state = 'active'
        and m1.capacity = 'admin'
        and m1.table_id = :auth_id
        and m2.table_id = :req_id
        """

    params = {'auth_id':authorized_user.id,
              'req_id':requested_user.id}

    log.debug(sql)
    log.debug(params)

    q = model.Session.execute(sql, params)

    res = q.fetchone()


    if res[0] > 0:
        return {'success': True}

    return {'success': False, 'msg': _('Not authorized')}



def action_wrapper(action, permission):
    """ Like a decorator, we return an action function that wraps the
    existing action with a permission check.

    Use this when the existing action is correct, but hardcodes
    a permission level that we don't want. (e.g., package_show instead of package_update)

    in get_actions:
    'package_activity_list': auth.action_wrapper('package_activity_list', 'package_update')
    """
    existing = toolkit.get_action(action)

    def wrapper(context, data_dict):
        check_access(permission, context, data_dict)
        return existing(context, data_dict)

    return wrapper

def action_wrapper_html(action, permission):
    """Like a decorator, we return an action function that wraps the
    existing action with a permission check.

    Use this when the existing action is correct, but hardcodes a
    permission level that we don't want. (e.g., package_show instead
    of package_update). Use this version when a html fragment is
    emitted without trapping for Not Authorized errors.

    in get_actions:
    'package_activity_list': auth.action_wrapper('package_activity_list', 'package_update')

    """
    existing = toolkit.get_action(action)

    def wrapper(context, data_dict):
        try:
            check_access(permission, context, data_dict)
        except NotAuthorized:
            return _("Not authorized to see this page")

        return existing(context, data_dict)

    return wrapper
