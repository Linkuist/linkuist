# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'LinkSum.read'
        db.add_column('source_linksum', 'read', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'LinkSum.recommanded'
        db.add_column('source_linksum', 'recommanded', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'LinkSum.read'
        db.delete_column('source_linksum', 'read')

        # Deleting field 'LinkSum.recommanded'
        db.delete_column('source_linksum', 'recommanded')


    models = {
        'source.linksum': {
            'Meta': {'object_name': 'LinkSum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Origin']", 'null': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recommanded': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Source']", 'null': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.TextField', [], {}),
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
