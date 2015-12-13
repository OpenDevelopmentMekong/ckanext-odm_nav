import os
from nose.tools import assert_equal, assert_in

class TestValidation:

  def test_01_odm_taxonomy_available(self):

    assert os.path.isdir(os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy/taxonomy_en.json')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy/taxonomy_km.json')))
    assert os.path.isfile(os.path.abspath(os.path.join(__file__, '../../','odm-taxonomy/taxonomy_th.json')))
