import base

TEST_TEMPLATE = \
"""    def test_{{path}}_{{time}}(self):
        r = self.client.{{method}}({{request_str}})"""

STATUS_TEMPLATE  = \
"""        self.assertEqual(r.status_code, {{status_code}})"""

CONTEXT_TEMPLATE = \
"""        self.assertEqual(unicode(r.context["{{key}}"]), u"{{value}}")"""

class Processor(base.Processer):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name='django'):
        super(Processor, self).__init__(name)

    def _get_template(self, templatename):
        return {
            'test': TEST_TEMPLATE,
            'status': STATUS_TEMPLATE,
            'context': CONTEXT_TEMPLATE,
            }[templatename]
