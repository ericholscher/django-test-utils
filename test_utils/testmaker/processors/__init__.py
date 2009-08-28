
"""
Interfaces for processing Django tests.

To add your own processors, use the TEST_PROCESSOR_MODULES setting::

    TEST_PROCESSOR_MODULES = {
        'django': 'test_utils.testmaker.processors.django',
        'twill': 'test_utils.testmaker.processors.twill',
    }

"""

from django.conf import settings
from django.utils import importlib

# Built-in processors

TEST_PROCESSORS = {
    'django': 'test_utils.testmaker.processors.django_processor',
    'twill': 'test_utils.testmaker.processors.twill_processor',
}

_test_processors = {}

def register_processor(format, processor_module, processors=None):
    """"Register a new processor.

    ``processor_module`` should be the fully qualified module name
    for the processor.

    If ``processors`` is provided, the registration will be added
    to the provided dictionary.

    If ``processors`` is not provided, the registration will be made
    directly into the global register of processors. Adding processors
    directly is not a thread-safe operation.
    """
    module = importlib.import_module(processor_module)
    if processors is None:
        _test_processors[format] = module
    else:
        processors[format] = module

def unregister_processor(format):
    "Unregister a given processor. This is not a thread-safe operation."
    del _test_processors[format]

def get_processor(format):
    if not _test_processors:
        _load_test_processors()
    return _test_processors[format].Processor

def get_processor_formats():
    if not _test_processors:
        _load_test_processors()
    return _test_processors.keys()

def _load_test_processors():
    """
    Register built-in and settings-defined processors. This is done lazily so
    that user code has a chance to (e.g.) set up custom settings without
    needing to be careful of import order.
    """
    global _test_processors
    processors = {}
    for format in TEST_PROCESSORS:
        register_processor(format, TEST_PROCESSORS[format], processors)
    if hasattr(settings, "TEST_PROCESSOR_MODULES"):
        for format in settings.TEST_PROCESSOR_MODULES:
            register_processor(format, settings.TEST_PROCESSOR_MODULES[format], processors)
    _test_processors = processors
