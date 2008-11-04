
class TemplateTestCase(TestCase):
    """An extended ``TestCase`` that includes a simple helper for rendering templates (and tags/filters). """

    def render(self, template_string, context={}):
        """Return the rendered string or the exception raised while rendering."""
        try:
            t = template.Template(template_string)
            c = template.Context(context)
            return t.render(c)
        except Exception, e:
            return e

    def assertClassesEqual(self, Class1, Class2):
        """Assert that instances of two exceptions are of the same class."""
        self.assertEqual(Class1.__class__, Class2.__class__)

    def assertTemplateSyntaxError(self, Class):
        """Assert that an exception is a template.TemplateSyntaxError."""
        self.assertTrue(isinstance(Class, template.TemplateSyntaxError))

    def checkTagLoads(self):
        """Meant to be inherited: used to check if the template tag loads"""
        self.assertEqual(self.render(u'{% load ' + self.tag_name + ' %}'), u'')
