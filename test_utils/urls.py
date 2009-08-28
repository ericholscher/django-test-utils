from django.conf.urls.defaults import *

import test_utils.views as test_views

urlpatterns = patterns('',
                       url(r'^set_logging/(?P<filename>.*?)/',
                           test_views.set_logging,
                           name='test_utils_set_logging'),
                       url(r'^set_logging/',
                           test_views.set_logging,
                           name='test_utils_set_logging'),
                       url(r'^show_log/',
                           test_views.show_log,
                           name='test_utils_show_log'),
                       )
