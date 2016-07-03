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


.. _pip: http://www.pip-installer.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/
