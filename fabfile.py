# -*- coding: utf-8 -*-
"""
Fabric file.
"""
# Std Library
import ConfigParser
import os

# Fabric
from fabric.colors import green
from fabric.api import (
    cd,
    env,
    hide,
    local, 
    prefix,
    require,
    run,
    settings,
    sudo,
    task,
)


# Contants
# -----------------------------------------------------------------------------
CONF_ROOT = os.path.join(os.path.dirname(__file__), 'vagrant', 'conf')

# Environment defaults
# -----------------------------------------------------------------------------
env.shell = '/bin/bash -c'
env.db_name = 'collectr'
env.db_user = 'collectr'


# Environments
# -----------------------------------------------------------------------------
@task
def vagrant():
    """
    Vagrant environment settings and default actions to perform.
    """
    print(green(u'Setting up vagrant environment...'))
    env.user = 'vagrant'
    env.hosts = ['33.33.33.10']
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]


# PostgreSQL
# -----------------------------------------------------------------------------
def postgresql_user_exists():
    """
    Checks if a PostgreSQL user exists.
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        res = sudo('''psql -t -A -c "SELECT COUNT(*) FROM pg_user WHERE usename = '%s';"''' % env.db_user,
            user='postgres',
            shell=False)
    return (res == "1")


def postgresql_db_exists():
    """
    Checks if a PostgreSQL database exists
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        return sudo('''psql -d %s -c ""''' % env.db_name, 
            user='postgres', 
            shell=False).succeeded


def excute_postgresql_query(query, db=None, flags=None, use_sudo=False):
    """
    Executes a remote psql query.
    """
    flags = flags or u''
    if db:
        flags = u"%s -d %s" % (flags, db)
    command = u'psql %s -c "%s"' % (flags, query)
    if use_sudo:
        sudo(command, user='postgres')
    else:    
        run(command)


@task
def create_postgresql_user(username, password=None, flags=None):
    """
    Creates a PostgreSQL database user.
    """
    print(green(u'Creating PostgreSQL user...'))
    flags = flags or u'-D -A -R'
    sudo(u'createuser %s %s' % (flags, username), user=u'postgres')
    if password:
        change_postgresql_user_password(username, password)


def change_postgresql_user_password(username, password):
    """
    Changes a PostgreSQL database user's password.
    """
    print(green(u'Changing PostgreSQL user password...'))
    sql = "ALTER USER %s WITH PASSWORD '%s'" % (username, password)
    excute_postgresql_query(sql, use_sudo=True)


@task
def create_postgresql_db(name, owner=None, encoding=u'UTF-8'):
    """
    Creates a PostgreSQL database.
    """
    print(green(u'Creating PostgreSQL database...'))
    flags = u''
    if encoding:
        flags = u'-E %s' % encoding
    if owner:
        flags = u'%s -O %s' % (flags, owner)
    sudo('createdb %s %s' % (flags, name), user='postgres')


# Python
# -----------------------------------------------------------------------------
@task
def install_pip_and_virtualenv():
    """
    Setups pip and virtualenv.
    """
    print(green(u'Installing pip, virtualenv and virtualenvwrapper...'))
    sudo('easy_install -U pip')
    sudo('pip install -U virtualenv virtualenvwrapper')


# Project
# -----------------------------------------------------------------------------
@task
def install_project_requirements():
    """
    Installs project requirements.
    """
    print(green(u'Installing project requirements...'))
    with prefix('WORKON_HOME=$HOME/.virtualenvs'):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
            run('mkvirtualenv collectr')
            with cd('/home/vagrant/project'):
                with prefix('workon collectr'):
                    run('pip install -r requirements/base.txt')


# Server
# -----------------------------------------------------------------------------
@task
def setup_locales():
    """
    Setups the server locales.
    """
    print(green(u'Setting up system locales...'))
    sudo('/usr/sbin/update-locale LANG=en_US.UTF-8')


@task
def install_packages():
    """
    Installs packages.
    """
    print(green(u'Installing system packages...'))
    config_file = os.path.join(CONF_ROOT, u'packages.conf')
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    sections = ('base', 'database', 'application')
    for section in sections:
        if config.has_section(section):
            sudo(u'apt-get update')
            sudo(u'apt-get install -y %s' % config.get(section, 'packages'))
            sudo(u'apt-get upgrade -y')


@task
def setup():
    """
    Setups the server.
    """
    setup_locales()
    install_packages()
    if not postgresql_user_exists():
        create_postgresql_user(username=env.db_user)
    if not postgresql_db_exists():
        create_postgresql_db(name=env.db_name, owner=env.db_user)
    install_pip_and_virtualenv()
    install_project_requirements()
