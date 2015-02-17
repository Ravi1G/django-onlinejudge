# Installation

To install django-onlinejudge and its dependencies run:

    pip install -e git+https://github.com/darbula/django-onlinejudge.git@master#egg=django-onlinejudge


## Sandbox (Debian)

    sudo wget http://heanet.dl.sourceforge.net/project/libsandbox/0.3.5/libsandbox_<version>_<platform>.deb
    sudo dpkg -i libsandbox_<version>_<platform>.deb
    sudo wget http://heanet.dl.sourceforge.net/project/libsandbox/0.3.5/pysandbox_<version>_<platform>.deb
    dpkg -i pysandbox_<version>_<platform>.deb


If `libc6` is wrong version i.e. on wheezy sandbox 0.3.5-3 demands libc6>=2.14 and wheezy has 2.13. In that case download source tar files form http://heanet.dl.sourceforge.net/project/libsandbox/0.3.5/ and compile:

    apt-get install python-dev
    tar -xzf libsandbox-<version>.tar.gz
    cd libsandbox-<version>
    ./configure --prefix=/usr
    sudo make install
    tar -xzvf pysandbox-<version>.tar.gz
    cd pysandbox-<version>
    python setup.py build
    sudo python setup.py install

Link package to use it in virtualenv:

    ln -s /usr/local/lib/python2.7/dist-packages/sandbox <virtualenv>/lib/python2.7/site-packages/

### Windows

Since pysandbox does not support windows for development purposes you can use `pydevrunner.py`, a mockup version of `pysandboxrunner.py`.


### Useful links:

[SO answer](http://stackoverflow.com/users/1445583/liuyu?tab=answers)

[Result codes](https://github.com/openjudge/sandbox/blob/V_0_3_x/libsandbox/src/sandbox.h)

[FAQ](http://stackoverflow.com/a/15143094/1247955)

[Customizing policies](https://github.com/liuyu81/TR-OJA-201209A)


# OnlineJudge project

Simplest way is to integrate this app in project is to override base.html template.

## Celery

Programs tests are performed using celery worker.

Install rabbitMQ as message broker for celery:

    sudo apt-get update
    sudo apt-get install rabbitmq-server

Django ORM is used as a result backend.

In project setup `celery.py` as decribed [here](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html).

[Examples](https://github.com/celery/celery/tree/3.1/examples/django/)

Run:

    celery worker -A <project>


# Tests

    python runstests.py
