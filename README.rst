Django simple account
================================

.. image:: https://github.com/kostya-ten/django_simple_account/workflows/Workflows/badge.svg
     :target: https://github.com/kostya-ten/django_simple_account/actions/
     :alt: GihHub Action

.. image:: https://img.shields.io/github/last-commit/kostya-ten/django_simple_account
     :target: https://github.com/kostya-ten/django_simple_account/commits/master
     :alt: GitHub last commit

.. image:: https://api.codacy.com/project/badge/Grade/45d420b488fd452cae355db78f7e1e96
    :target: https://www.codacy.com/manual/kostya/django_simple_account?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=kostya-ten/django_simple_account&amp;utm_campaign=Badge_Grade

.. image:: https://requires.io/github/kostya-ten/django_simple_account/requirements.svg?branch=master
     :target: https://requires.io/github/kostya-ten/django_simple_account/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://badge.fury.io/py/django-simple-account.svg
     :target: https://badge.fury.io/py/django-simple-account
     :alt: pypi

.. image:: https://img.shields.io/github/license/kostya-ten/django_simple_account?style=plastic
     :target: https://github.com/kostya-ten/django_simple_account/blob/master/LICENSE
     :alt: license




Requirements
""""""""""""""""""
* Python 3.6+
* A supported version of Django (currently 3.x)

Getting It
""""""""""""""""""
You can get Django tree materialized by using pip::

    $ pip install django-simple-account

If you want to install it from source, grab the git repository from GitHub and run setup.py::

    $ git clone git://github.com/kostya-ten/django_simple_account.git
    $ cd django_simple_account
    $ python setup.py install

Installation
"""""""""""""
To enable ``django_simple_account`` in your project you need to add it to `INSTALLED_APPS` in your projects ``settings.py``

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'django_simple_account',
        # ...
    )


Enable ``context_processors``

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    # ....
                    'django_simple_account.context_processors.settings',
                ],
            },
        },
    ]

Add ``urls.py`` in project

.. code-block:: python

    urlpatterns = [
        # ...
        path('accounts/', include('django_simple_account.urls')),
    ]
