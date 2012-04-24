# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'LinkSum.source'
        db.add_column('source_linksum', 'source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Source'], null=True), keep_default=False)

        # Changing field 'LinkSum.origin'
        db.alter_column('source_linksum', 'origin_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Origin'], null=True))


    def backwards(self, orm):
        
        # Deleting field 'LinkSum.source'
        db.delete_column('source_linksum', 'source_id')

        # Changing field 'LinkSum.origin'
        db.alter_column('source_linksum', 'origin_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['source.Origin']))


    models = {
        'source.linksum': {
            'Meta': {'object_name': 'LinkSum'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Origin']", 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Source']", 'null': 'True'}),
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
