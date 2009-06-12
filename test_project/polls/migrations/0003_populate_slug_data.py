from south.db import db
from django.db import models
from polls.models import *
from django.template.defaultfilters import slugify

class Migration:

    def forwards(self, orm):
        for poll in orm.Poll.objects.all():
            poll.slug = slugify(poll.question)
            poll.save()

    def backwards(self, orm):
        "Write your backwards migration here"
        for poll in orm.Poll.objects.all():
            poll.slug = ""
            poll.save()


    models = {
        'polls.poll': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('models.DateTimeField', ["'date published'"], {}),
            'question': ('models.CharField', [], {'max_length': '200'}),
            'slug': ('models.SlugField', [], {'null': 'True'})
        },
        'polls.choice': {
            'choice': ('models.CharField', [], {'max_length': '200'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'poll': ('models.ForeignKey', ["orm['polls.Poll']"], {}),
            'votes': ('models.IntegerField', [], {})
        }
    }

    complete_apps = ['polls']
