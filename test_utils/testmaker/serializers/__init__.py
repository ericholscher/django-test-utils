
"""
Interfaces for serializing Django requests.

To add your own serializers, use the TEST_SERIALIZATION_MODULES setting::

    TEST_SERIALIZATION_MODULES = {
        'pickle': 'test_utils.testmaker.serializers.pickle_serializer',
        'json': 'test_utils.testmaker.json_serializer',
    }

"""

from django.conf import settings
from django.utils import importlib

# Built-in serialize
TEST_SERIALIZERS = {
    'pickle': 'test_utils.testmaker.serializers.pickle_serializer',
    'json': 'test_utils.testmaker.serializers.json_serializer',
}

REQUEST_UNIQUE_STRING = '---REQUEST_BREAK---'
RESPONSE_UNIQUE_STRING = '---RESPONSE_BREAK---'

_test_serializers = {}

def register_serializer(format, serializer_module, serializers=None):
    """"Register a new serializer.

    ``serializer_module`` should be the fully qualified module name
    for the serializer.

    If ``serializers`` is provided, the registration will be added
    to the provided dictionary.

    If ``serializers`` is not provided, the registration will be made
    directly into the global register of serializers. Adding serializers
    directly is not a thread-safe operation.
    """
    module = importlib.import_module(serializer_module)
    if serializers is None:
        _test_serializers[format] = module
    else:
        serializers[format] = module

def unregister_serializer(format):
    "Unregister a given serializer. This is not a thread-safe operation."
    del _test_serializers[format]

def get_serializer(format):
    if not _test_serializers:
        _load_test_serializers()
    return _test_serializers[format].Serializer

def get_serializer_formats():
    if not _test_serializers:
        _load_test_serializers()
    return _test_serializers.keys()

def get_deserializer(format):
    if not _test_serializers:
        _load_test_serializers()
    return _test_serializers[format].Deserializer

def _load_test_serializers():
    """
    Register built-in and settings-defined serializers. This is done lazily so
    that user code has a chance to (e.g.) set up custom settings without
    needing to be careful of import order.
    """
    global _test_serializers
    serializers = {}
    for format in TEST_SERIALIZERS:
        register_serializer(format, TEST_SERIALIZERS[format], serializers)
    if hasattr(settings, "TEST_SERIALIZATION_MODULES"):
        for format in settings.TEST_SERIALIZATION_MODULES:
            register_serializer(format, settings.TEST_SERIALIZATION_MODULES[format], serializers)
    _test_serializers = serializers
