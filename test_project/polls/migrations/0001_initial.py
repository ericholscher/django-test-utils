
from south.db import db
from django.db import models
from polls.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Poll'
        db.create_table('polls_poll', (
            ('id', models.AutoField(primary_key=True)),
            ('question', models.CharField(max_length=200)),
            ('pub_date', models.DateTimeField('date published')),
        ))
        db.send_create_signal('polls', ['Poll'])
        
        # Adding model 'Choice'
        db.create_table('polls_choice', (
            ('id', models.AutoField(primary_key=True)),
            ('poll', models.ForeignKey(orm.Poll)),
            ('choice', models.CharField(max_length=200)),
            ('votes', models.IntegerField()),
        ))
        db.send_create_signal('polls', ['Choice'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Poll'
        db.delete_table('polls_poll')
        
        # Deleting model 'Choice'
        db.delete_table('polls_choice')
        
    
    
    models = {
        'polls.poll': {
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'pub_date': ('models.DateTimeField', ["'date published'"], {}),
            'question': ('models.CharField', [], {'max_length': '200'})
        },
        'polls.choice': {
            'choice': ('models.CharField', [], {'max_length': '200'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'poll': ('models.ForeignKey', ["orm['polls.Poll']"], {}),
            'votes': ('models.IntegerField', [], {})
        }
    }
    
    complete_apps = ['polls']
