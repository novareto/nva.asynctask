nva.asynctask
=============

Installation
------------

Zunächst müssen wir unseren Buildout mit folgendem File erweitern

  extends = 
    ...
    celery.cfg

Diese Extension installiert und konfiguriert alle Komponenten um celery
ausführen zu können.

Anschließend müssen wir unser Package nva.asynctask in das install_requires unseres Packages aufnehmen.
Um die Konfiguration von celery nutzen zu können muss das Konfigurationsfile
celeryconfig.py im Systempath auffindbar sein. Hierzu können wir in der
Buildout-Sektion [app] folgendes ergänzen:

[app]
extra-paths = ${celery:config-path}

Wir können Celery wiefolgt starten:

.. code-block:: bash

  ./bin/celery worker -l debug -c 2


Handler um die Zope-Umgebung in Celery zu initialiesieren
---------------------------------------------------------
(tasks.py)

.. code-block:: python 

    # -*- coding: utf-8 -*-
    # Copyright (c) 2007-2013 NovaReto GmbH
    # cklinger@novareto.de


    import logging
    import celeryconfig
    import zope.app.wsgi

    from celery.signals import worker_process_init

    logger = logging.getLogger()
    level = logging.INFO


    @worker_process_init.connect
    def setupZCA(signal, sender):
        zope.app.wsgi.config(celeryconfig.ZOPE_CONF)
        logger.log(level, 'Starting Zope/Grok ENVIRONMENT')


Die Funktion setupZCA wird über einen Event von celery ausgeführt und somit die 
wird der Stack von Grok geladen.


Tasks
-----

Einfache Tasks ohne ZCA-Stack.

.. code-block:: python 

    from celery import task

    @task
    def nothing():
        print "NOTHING"


Tasks die erst nach einer erflogreichen Transaktion aufgerufen werden

.. code-block:: python 

    from nva.asynctask.task import zope_task, transactional_task

    @transactional_task
    def send_mail():
        send_mymail(....)


Tasks die innerhalb eines ZopeStacks und innerhalb einer eigenen Transaktion laufen.

.. code-block:: python 

    from nva.asynctask.task import zope_task 
    @zope_task
    def smail(*args, **kwargs):
        from .emailer import send_mail
        send_mail('cklinger@nvatest.de', ('cklinger@nvatest.de', ),  kwargs.get('message') + 'A', "LBBLALLA")


Taks die innerhalb des ZopeStacks laufen und die ZODB-verändern


.. code-block:: python 

    # Call
    update_title.delay(context=self.context, message='HALLO')

    # Caller
    from nva.asynctask.task import zope_task 

    @zope_task
    def update_title(context, message):
        context.title = context.title + message
        context.counter += 1
        return context.title
