# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Collection'
        db.create_table('source_collection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('source', ['Collection'])

        # Adding model 'Filter'
        db.create_table('source_filter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('regexp', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('field', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('to_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('to_collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Collection'], null=True, blank=True)),
            ('xpath', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('source', ['Filter'])

        # Adding model 'Source'
        db.create_table('source_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('slug', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
        ))
        db.send_create_signal('source', ['Source'])

        # Adding model 'UrlViews'
        db.create_table('source_urlviews', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('source', ['UrlViews'])

        # Adding model 'Tag'
        db.create_table('source_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
        ))
        db.send_create_signal('source', ['Tag'])

        # Adding model 'Url'
        db.create_table('source_url', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.TextField')(unique=True)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('views', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.UrlViews'])),
            ('raw_tags', self.gf('django.db.models.fields.TextField')()),
            ('summary', self.gf('django.db.models.fields.TextField')(null=True)),
            ('html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('inserted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('source', ['Url'])

        # Adding M2M table for field tags on 'Url'
        db.create_table('source_url_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('url', models.ForeignKey(orm['source.url'], null=False)),
            ('tag', models.ForeignKey(orm['source.tag'], null=False))
        ))
        db.create_unique('source_url_tags', ['url_id', 'tag_id'])

        # Adding model 'Author'
        db.create_table('source_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Source'])),
        ))
        db.send_create_signal('source', ['Author'])

        # Adding model 'LinkSum'
        db.create_table('source_linksum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Url'], null=True, blank=True)),
            ('read', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('recommanded', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Collection'], null=True)),
            ('inserted_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('source', ['LinkSum'])

        # Adding unique constraint on 'LinkSum', fields ['url', 'user']
        db.create_unique('source_linksum', ['url_id', 'user_id'])

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

        # Adding M2M table for field authors on 'LinkSum'
        db.create_table('source_linksum_authors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('linksum', models.ForeignKey(orm['source.linksum'], null=False)),
            ('author', models.ForeignKey(orm['source.author'], null=False))
        ))
        db.create_unique('source_linksum_authors', ['linksum_id', 'author_id'])

        # Adding model 'HotTopic'
        db.create_table('source_hottopic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('source', ['HotTopic'])

        # Adding M2M table for field sums on 'HotTopic'
        db.create_table('source_hottopic_sums', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hottopic', models.ForeignKey(orm['source.hottopic'], null=False)),
            ('linksum', models.ForeignKey(orm['source.linksum'], null=False))
        ))
        db.create_unique('source_hottopic_sums', ['hottopic_id', 'linksum_id'])

        # Adding model 'Rss'
        db.create_table('source_rss', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.URLField')(unique=True, max_length=1024)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('etag', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('source', ['Rss'])

        # Adding M2M table for field users on 'Rss'
        db.create_table('source_rss_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('rss', models.ForeignKey(orm['source.rss'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('source_rss_users', ['rss_id', 'user_id'])

        # Adding model 'Reddit'
        db.create_table('source_reddit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subreddit', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal('source', ['Reddit'])

        # Adding M2M table for field users on 'Reddit'
        db.create_table('source_reddit_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('reddit', models.ForeignKey(orm['source.reddit'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('source_reddit_users', ['reddit_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'LinkSum', fields ['url', 'user']
        db.delete_unique('source_linksum', ['url_id', 'user_id'])

        # Deleting model 'Collection'
        db.delete_table('source_collection')

        # Deleting model 'Filter'
        db.delete_table('source_filter')

        # Deleting model 'Source'
        db.delete_table('source_source')

        # Deleting model 'UrlViews'
        db.delete_table('source_urlviews')

        # Deleting model 'Tag'
        db.delete_table('source_tag')

        # Deleting model 'Url'
        db.delete_table('source_url')

        # Removing M2M table for field tags on 'Url'
        db.delete_table('source_url_tags')

        # Deleting model 'Author'
        db.delete_table('source_author')

        # Deleting model 'LinkSum'
        db.delete_table('source_linksum')

        # Removing M2M table for field sources on 'LinkSum'
        db.delete_table('source_linksum_sources')

        # Removing M2M table for field tags on 'LinkSum'
        db.delete_table('source_linksum_tags')

        # Removing M2M table for field authors on 'LinkSum'
        db.delete_table('source_linksum_authors')

        # Deleting model 'HotTopic'
        db.delete_table('source_hottopic')

        # Removing M2M table for field sums on 'HotTopic'
        db.delete_table('source_hottopic_sums')

        # Deleting model 'Rss'
        db.delete_table('source_rss')

        # Removing M2M table for field users on 'Rss'
        db.delete_table('source_rss_users')

        # Deleting model 'Reddit'
        db.delete_table('source_reddit')

        # Removing M2M table for field users on 'Reddit'
        db.delete_table('source_reddit_users')


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
        'source.hottopic': {
            'Meta': {'object_name': 'HotTopic'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sums': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['source.LinkSum']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
        'source.reddit': {
            'Meta': {'object_name': 'Reddit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subreddit': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'})
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
            'html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
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