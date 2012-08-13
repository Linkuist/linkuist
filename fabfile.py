# -*- coding: utf-8 -*-
"""
Fabric file.
"""
# Std Library
import ConfigParser
import os

# Fabric
from fabric.api import (
    cd,
    env,
    local, 
    prefix,
    require,
    run,
    settings,
    sudo,
    task,
)


# Contants
CONF_ROOT = os.path.join(os.path.dirname(__file__), 'vagrant', 'conf')

# Environment defaults
env.shell = '/bin/bash -c'


@task
def vagrant():
    """
    Vagrant environment settings and default actions to perform.
    """
    env.user = 'vagrant'
    env.hosts = ['33.33.33.10']
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]


@task
def install_packages():
    """
    Installs packages.
    """
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
def setup_server(*roles):
    """
    Setups the server.
    """
    sudo('/usr/sbin/update-locale LANG=en_US.UTF-8')
    install_packages()
    sudo('easy_install -U pip')
    sudo('pip install -U virtualenv virtualenvwrapper pytidylib')
    with prefix('WORKON_HOME=$HOME/.virtualenvs'):
        with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
            run('mkvirtualenv collectr')
            with cd('/home/vagrant/project'):
                with prefix('workon collectr'):
                    run('pip install -r requirements/base.txt')
