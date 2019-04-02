try:
    from PIL import Image
    HAS_PIL = True
except:
    HAS_PIL = False

import io
import requests


from ckan.lib.base import BaseController
from ckan.plugins import toolkit
from ckan.lib import helpers
from ckan.common import request, response, c

from .helpers import memoize

import logging
log = logging.getLogger(__name__)

@memoize
def _thumbnail(url):
    r = requests.get(url, stream=True)
    r.raw.decode_content = True
    im = Image.open(r.raw)
    log.debug('Initial size: %s, format: %s' %(im.size, im.format))
    im.thumbnail((120,58))

    out_buf = io.BytesIO()
    im.save(out_buf, im.format)
    
    return (Image.MIME[im.format], out_buf.getvalue())

class Controller(BaseController):
    
    def read(self, id, resource_id, filename=None):
        context = {'user': c.user,
                   'auth_user_obj': c.userobj}
        
        resource = toolkit.get_action('resource_show')(context,
                                                       {'id': resource_id})
        if not HAS_PIL:
            helpers.redirect_to(resource['url'])
            return

        content_type, img_bytes = _thumbnail(resource['url'])
        
        response.headers['Content-type'] = content_type
        response.headers['cache-control'] = "max-age=86400"
        
        return img_bytes
