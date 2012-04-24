# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Origin'
        db.create_table('source_origin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('source', ['Origin'])

        # Adding model 'LinkSum'
        db.create_table('source_linksum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tags', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('summary', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('link', self.gf('django.db.models.fields.TextField')()),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Origin'])),
        ))
        db.send_create_signal('source', ['LinkSum'])


    def backwards(self, orm):
        
        # Deleting model 'Origin'
        db.delete_table('source_origin')

        # Deleting model 'LinkSum'
        db.delete_table('source_linksum')


    models = {
        'source.linksum': {
            'Meta': {'object_name': 'LinkSum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Origin']"}),
            'summary': ('django.db.models.fields.TextField', [], {}),
            'tags': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'source.origin': {
            'Meta': {'object_name': 'Origin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'source.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['source']
