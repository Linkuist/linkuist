# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Origin'
        db.delete_table('source_origin')

        # Adding field 'Url.title'
        db.add_column('source_url', 'title',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Url.summary'
        db.add_column('source_url', 'summary',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'Url.inserted_at'
        db.add_column('source_url', 'inserted_at',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now),
                      keep_default=False)

        # Deleting field 'LinkSum.origin'
        db.delete_column('source_linksum', 'origin_id')

        # Deleting field 'LinkSum.tags'
        db.delete_column('source_linksum', 'tags')

        # Deleting field 'LinkSum.summary'
        db.delete_column('source_linksum', 'summary')

        # Deleting field 'LinkSum.source'
        db.delete_column('source_linksum', 'source_id')

        # Deleting field 'LinkSum.link'
        db.delete_column('source_linksum', 'link')

        # Deleting field 'LinkSum.title'
        db.delete_column('source_linksum', 'title')

        # Adding M2M table for field sources on 'LinkSum'
        db.create_table('source_linksum_sources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('linksum', models.ForeignKey(orm['source.linksum'], null=False)),
            ('source', models.ForeignKey(orm['source.source'], null=False))
        ))
        db.create_unique('source_linksum_sources', ['linksum_id', 'source_id'])

        # Adding M2M table for field tags on 'LinkSum'
        db.create_table('source_linksum_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('linksum', models.ForeignKey(orm['source.linksum'], null=False)),
            ('tag', models.ForeignKey(orm['source.tag'], null=False))
        ))
        db.create_unique('source_linksum_tags', ['linksum_id', 'tag_id'])


    def backwards(self, orm):
        # Adding model 'Origin'
        db.create_table('source_origin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('source', ['Origin'])

        # Deleting field 'Url.title'
        db.delete_column('source_url', 'title')

        # Deleting field 'Url.summary'
        db.delete_column('source_url', 'summary')

        # Deleting field 'Url.inserted_at'
        db.delete_column('source_url', 'inserted_at')

        # Adding field 'LinkSum.origin'
        db.add_column('source_linksum', 'origin',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Origin'], null=True),
                      keep_default=False)

        # Adding field 'LinkSum.tags'
        db.add_column('source_linksum', 'tags',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'LinkSum.summary'
        db.add_column('source_linksum', 'summary',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'LinkSum.source'
        db.add_column('source_linksum', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Source'], null=True),
                      keep_default=False)

        # Adding field 'LinkSum.link'
        db.add_column('source_linksum', 'link',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'LinkSum.title'
        db.add_column('source_linksum', 'title',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Removing M2M table for field sources on 'LinkSum'
        db.delete_table('source_linksum_sources')

        # Removing M2M table for field tags on 'LinkSum'
        db.delete_table('source_linksum_tags')


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
        'source.author': {
            'Meta': {'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Source']"})
        },
        'source.collection': {
            'Meta': {'object_name': 'Collection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'source.filter': {
            'Meta': {'object_name': 'Filter'},
            'field': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'regexp': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'to_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Collection']", 'null': 'True', 'blank': 'True'}),
            'to_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'xpath': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'source.linksum': {
            'Meta': {'unique_together': "(('url', 'user'),)", 'object_name': 'LinkSum'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'authors'", 'symmetrical': 'False', 'to': "orm['source.Author']"}),
            'collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Collection']", 'null': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inserted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'read': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'recommanded': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['source.Source']", 'null': 'True', 'symmetrical': 'False'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['source.Tag']", 'symmetrical': 'False'}),
            'url': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.Url']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'source.rss': {
            'Meta': {'object_name': 'Rss'},
            'etag': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
        },
        'source.source': {
            'Meta': {'object_name': 'Source'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'source.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        'source.url': {
            'Meta': {'object_name': 'Url'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'inserted_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'link': ('django.db.models.fields.TextField', [], {'unique': 'True'}),
            'raw_tags': ('django.db.models.fields.TextField', [], {}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['source.Tag']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'views': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['source.UrlViews']"})
        },
        'source.urlviews': {
            'Meta': {'object_name': 'UrlViews'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['source']