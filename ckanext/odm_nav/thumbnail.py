try:
    from PIL import Image
    HAS_PIL = True
except:
    HAS_PIL = False

import io
import requests


from ckan.lib.base import BaseController
from ckan.plugins import toolkit
from ckan.lib import helpers, uploader
from ckan.common import request, response, c

from .helpers import memoize

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

@memoize
def _thumbnail(path):
    im = Image.open(path)
    log.debug('Initial size: %s, format: %s' %(im.size, im.format))
    im.thumbnail((120,58))

    out_buf = io.BytesIO()
    im.save(out_buf, im.format)
    
    return (Image.MIME[im.format], out_buf.getvalue())

def _blank():
    im = Image.new('RGB', (58,58), 'white')
    out_buf = io.BytesIO()
    im.save(out_buf, "PNG")

    return (Image.MIME['PNG'], out_buf.getvalue())
    
class Controller(BaseController):
    
    def read(self, id, resource_id, filename=None):
        context = {'user': c.user,
                   'auth_user_obj': c.userobj}
        
        resource = toolkit.get_action('resource_show')(context,
                                                       {'id': resource_id})
        if not HAS_PIL:
            helpers.redirect_to(resource['url'])
            return

        path = None
        if resource['url_type'] == 'upload':
            upload = uploader.get_resource_uploader(resource)
            path = upload.get_path(resource['id'])
                                    
        try:
            content_type, img_bytes = _thumbnail(path)
        except IOError as e:
            log.error("Exception thumbnailing %s %s: %s" %(
                resource_id, filename, e))
            content_type, img_bytes = _blank()
        
        response.headers['Content-type'] = content_type
        response.headers['cache-control'] = "max-age=86400"
        
        return img_bytes
