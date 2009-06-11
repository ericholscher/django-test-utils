__doc__ = """
### test setup() and teardown() logic

>>> from test_utils.utils.twill_runner import *
>>> from django.conf import settings
>>> setup()
<..._EasyTwillBrowser object at ...>
>>> setup()                                # no duplicate registrations
False
>>> len(INSTALLED)
1
>>> teardown()
True
>>> len(INSTALLED)
0

>>> setup(host='myhost', port=40)
<..._EasyTwillBrowser object at ...>
>>> setup(host='myhost', port=10)
<..._EasyTwillBrowser object at ...>
>>> teardown(port=10)                      # exact match OR no arguments to pop last required
False
>>> teardown()                             # this will remove the last
True
>>> len(INSTALLED)                         # one handler is still registered
1
>>> teardown(host='myhost', port=40)       # remove it by exact match
True
>>> len(INSTALLED)
0

>>> settings.DEBUG_PROPAGATE_EXCEPTIONS = False
>>> setup(propagate=True)
<..._EasyTwillBrowser object at ...>
>>> settings.DEBUG_PROPAGATE_EXCEPTIONS
True
>>> teardown()
True
>>> settings.DEBUG_PROPAGATE_EXCEPTIONS
False
>>> len(INSTALLED)
0


### test relative url handling ###
# Note that for simplicities sake we only
# check whether our custom code appended a
# host name; the twill browser base class
# never gets to see the urls, and we don't
# know what it makes of it.

# put browser into testing mode
>>> browser = get_browser()
>>> browser._testing_ = True

>>> setup(host='a', port=1)
<..._EasyTwillBrowser object at ...>

>>> browser.go('/')
'http://a:1/'
>>> browser.go('/index')
'http://a:1/index'

>>> browser.go('http://google.de')
'http://google.de'
>>> browser.go('/services')
'/services'
>>> browser.go('')
''
>>> browser.go('?foo=bar')
'?foo=bar'

>>> browser.go('/index', default=True)
'http://a:1/index'

# TODO: since we don't work with real urls, we don't get anything back. Improve.
>>> url()

>>> teardown()
True
>>> len(INSTALLED)
0

# leave testing mode again
>>> browser._testing_ = False

# TODO: test the login/logout methods
"""
