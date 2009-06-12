
from south.db import db
from django.db import models
from polls.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'Poll.slug'
        db.add_column('polls_poll', 'slug', models.SlugField(null=True))
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'Poll.slug'
        db.delete_column('polls_poll', 'slug')
        
    
    
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
