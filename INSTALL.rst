Installation
============

Local
-----

Make sure `pip`_ and `virtualenvwrapper`_ are installed::

    sudo easy_install -U pip
    sudo pip install virtualenvwrapper
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bash_profile
    source ~/.bash_profile
    
Then create a dedicated virtualenv for Collectr::

    mkvirtualenv collectr

Now, install project requirements::

    pip install -r requirements/base.txt

Rename ``settings_local.sample.py`` file::

    mv collectr/settings_local.sample.py collectr/settings_local.py

Add your own local settings (database credentials, Twitter consumer key/secret, 
etc) in this file.

Create the initial database tables::

    python manage.py syncdb

Execute migrations::

    python manage.py migrate

Run the server::

    python manage.py runserver

Enjoy.

Vagrant (Ubuntu 12.04 virtual server)
-------------------------------------

Install `VirtualBox`_ and `Vagrant`_.

Install `Fabric`_::

    sudo easy_install -U pip
    sudo pip install fabric

Start and setup the virtual server::

    vagrant up
    fab vagrant setup

Log into the server via SSH::

    vagrant ssh

Activate the virtualenv::

    workon collectr

Go to the project directory::

    cd project/collectr

Rename ``settings_local.sample.py`` file::

    mv collectr/settings_local.sample.py collectr/settings_local.py

Add your own local settings (database credentials, Twitter consumer key/secret, 
etc) in this file. 

Defaults:

* PostgreSQL user: ``collectr``
* PosgtreSQL user password: ``collectr``
* PosgtreSQL database: ``collectr``

Create the initial database tables::

    python manage.py syncdb

Execute migrations::

    python manage.py migrate

Run the server::

    python manage.py runserver [::]:8000

In your browser, go to: http://localhost:8001. 

Enjoy.


.. _pip: http://www.pip-installer.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
.. _VirtualBox: https://www.virtualbox.org
.. _Vagrant: http://vagrantup.com
.. _Fabric: http://fabfile.org
