.. _settings:


==================
Available Settings
==================

This page contains the available settings for test utils. Broken down by the app that they affect.


Testmaker
=========

TESTMAKER_SERIALIZER
--------------------

This is the serializer that Testmaker should use. By default it is `pickle`.

TESTMAKER_PROCESSOR
-------------------

This is the processor that Testmaker should use. By default it is `django`.

TEST_PROCESSOR_MODULES
----------------------

This allows Testmaker to have access to your own custom processor modules. They are defined with the full path to the module import as the value.

To add your own processors, use the TEST_PROCESSOR_MODULES setting::

    TEST_PROCESSOR_MODULES = {
        'awesome': 'my_sweet_app.processors.awesome',
    }

TEST_SERIALIZATION_MODULES
--------------------------

The same as the above `TEST_PROCESSOR_MODULES`, allowing you to augment Testmakers default serializers.

To add your own serializers, use the TEST_SERIALIZATION_MODULES setting::

    TEST_SERIALIZATION_MODULES = {
        'awesome': 'my_sweet_app.serializers.awesome',
    }
