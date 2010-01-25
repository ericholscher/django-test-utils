import base

TEST_TEMPLATE = """go {{ path }}"""

STATUS_TEMPLATE = """code {{ status_code }}"""

#CONTEXT_TEMPLATE = '''find {{value}}'''
CONTEXT_TEMPLATE = ''

class Processor(base.Processer):
    """Processes the serialized data. Generally to create some sort of test cases"""

    def __init__(self, name='twill'):
        super(Processor, self).__init__(name)

    def _get_template(self, templatename):
        return {
            'test': TEST_TEMPLATE,
            'status': STATUS_TEMPLATE,
            'context': CONTEXT_TEMPLATE,
            }[templatename]
