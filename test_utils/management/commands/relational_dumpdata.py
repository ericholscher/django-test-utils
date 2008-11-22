from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from optparse import make_option
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.db.models import get_app, get_apps, get_models

def _relational_dumpdata(app, collected):
    objects = []
    for mod in get_models(app):
        objects.extend(mod._default_manager.all())
    #Got models, now get their relationships.
    #Thanks to http://www.djangosnippets.org/snippets/918/
    related = []
    collected = collected.union(set([(x.__class__, x.pk) for x in objects]))
    for obj in objects:
        for f in obj._meta.fields :
            if isinstance(f, ForeignKey):
                new = getattr(obj, f.name) # instantiate object
                if new and not (new.__class__, new.pk) in collected:
                    collected.add((new.__class__, new.pk))
                    related.append(new)
        for f in obj._meta.many_to_many:
            if isinstance(f, ManyToManyField):
                for new in getattr(obj, f.name).all():
                    if new and not (new.__class__, new.pk) in collected:
                        collected.add((new.__class__, new.pk))
                        related.append(new)
    if related != []:
        objects.extend(related)
    return (objects, collected)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('-e', '--exclude', dest='exclude',action='append', default=[],
            help='App to exclude (use multiple --exclude to exclude multiple apps).'),
    )
    help = 'Output the contents of the database as a fixture of the given format.'
    args = '[appname ...]'

    def handle(self, *app_labels, **options):

        format = options.get('format','json')
        indent = options.get('indent',None)
        exclude = options.get('exclude',[])
        show_traceback = options.get('traceback', False)

        excluded_apps = [get_app(app_label) for app_label in exclude]

        if len(app_labels) == 0:
            app_list = [app for app in get_apps() if app not in excluded_apps]
        else:
            app_list = [get_app(app_label) for app_label in app_labels]

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)

        objects = []
        collected = set()
        for app in app_list: #Yey for ghetto recusion
            objects, collected = _relational_dumpdata(app, collected)
        #****End New stuff
        try:
            return serializers.serialize(format, objects, indent=indent)
        except Exception, e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)
