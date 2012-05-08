# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UrlViews'
        db.create_table('source_urlviews', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('source', ['UrlViews'])

        # Adding model 'Url'
        db.create_table('source_url', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.TextField')()),
            ('views', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.UrlViews'])),
            ('raw_tags', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('source', ['Url'])

        # Adding M2M table for field tags on 'Url'
        db.create_table('source_url_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('url', models.ForeignKey(orm['source.url'], null=False)),
            ('tag', models.ForeignKey(orm['source.tag'], null=False))
        ))
        db.create_unique('source_url_tags', ['url_id', 'tag_id'])

        # Adding model 'Tag'
        db.create_table('source_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('source', ['Tag'])

        # Adding field 'LinkSum.url'
        db.add_column('source_linksum', 'url', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Url'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'UrlViews'
        db.delete_table('source_urlviews')

        # Deleting model 'Url'
        db.delete_table('source_url')

        # Removing M2M table for field tags on 'Url'
        db.delete_table('source_url_tags')

        # Deleting model 'Tag'
        db.delete_table('source_tag')

        # Deleting field 'LinkSum.url'
        db.delete_column('source_linksum', 'url_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'source.collection': {
            'Meta': {'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'source.filter': {
            'Meta': {'object_name': 'Filter'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'regexp': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'to_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Collection']", 'null': 'True', 'blank': 'True'}),
            'to_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'source.linksum': {
            'Meta': {'object_name': 'LinkSum'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Collection']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Origin']", 'null': 'True'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recommanded': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Source']", 'null': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Url']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        },
        'source.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'source.url': {
            'Meta': {'object_name': 'Url'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.TextField', [], {}),
            'raw_tags': ('django.db.models.fields.TextField', [], {}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['source.Tag']", 'symmetrical': 'False'}),
            'views': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.UrlViews']"})
        },
        'source.urlviews': {
            'Meta': {'object_name': 'UrlViews'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['source']
