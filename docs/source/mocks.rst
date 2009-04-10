.. _mocks:


Mock Objects
============


Mock Requests
-------------

This mock allows you to make requests against a view that isn't included in any URLConf.

RequestFactory
^^^^^^^^^^^^^^

Usage::

    rf = RequestFactory()
    get_request = rf.get('/hello/')
    post_request = rf.post('/submit/', {'foo': 'bar'})

This class re-uses the django.test.client.Client interface, docs here:
http://www.djangoproject.com/documentation/testing/#the-test-client

Once you have a request object you can pass it to any view function,
just as if that view had been hooked up using a URLconf.


Original Source
"""""""""""""""

Taken from Djangosnippets.net_, originally by `Simon Willison <http://simonwillison.net/>`_.

.. _Djangosnippets.net: http://www.djangosnippets.org/snippets/963/
