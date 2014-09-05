# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import celery
import transaction

from ZODB.interfaces import IDatabase

from celery.contrib import rdb
from z3c.objpath import resolve
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility
from zope.component.hooks import setSite, getSite

from . import REDIS_CLIENT, ZOPE_CONF


class AfterCommitTask(celery.Task):
    abstract = True

    def apply_async(self, *args, **kw):
        def hook(success):
            if success:
                super(AfterCommitTask, self).apply_async(*args, **kw)
        transaction.get().addAfterCommitHook(hook)

    def run(self, context, *args, **kwargs):
        # Run the task inside a transaction.
        # The object revival needs to happen inside this transaction too.
        try:
            celery.Task.run(self, context, *args, **kwargs)
        except Exception as e:
            self.retry(exc=e)


def zope_task(**kwargs):

    def get_root():
        conn = getUtility(IDatabase).open()
        return conn.root()[ZopePublication.root_name]

    def wrap(func):
        def queued_task(*args, **kw):
            try:
                root_folder = get_root()
                setSite(root_folder['app'])
                obj = resolve(getSite(), kw.get('path'))
                with transaction.manager:
                    result = func(obj, *args, **kw)
            finally:
                setSite(None)
                db.close()

            return result
                
        queued_task.__name__ = func.__name__
        return celery.task(base=AfterCommitTask, **kwargs)(queued_task)
    return wrap
