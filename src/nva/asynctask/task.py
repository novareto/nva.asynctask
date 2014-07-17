# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import celery
import transaction

from celery.contrib import rdb
from z3c.objpath import resolve
from zope.app.publication.zopepublication import ZopePublication
from zope.app.wsgi import config
from zope.component.hooks import setSite, getSite

from . import REDIS_CLIENT, ZOPE_CONF


class AfterCommitTask(celery.Task):
    abstract = True

    def apply_async(self, *args, **kw):
        def hook(success):
            if success:
                super(AfterCommitTask, self).apply_async(*args, **kw)
        transaction.get().addAfterCommitHook(hook)


def simpleton(path, timeout=None):
    """Enforce only one celery task at a time, on the given path.
    """

    def simpleton_wrapper(run_func):
        def simpleton_runner(*args, **kwargs):
            with REDIS_CLIENT.lock(path, timeout=timeout):
                ret_value = run_func(*args, **kwargs)
            return ret_value
        return simpleton_runner

    return simpleton_wrapper


def zope_task(**kwargs):
    
    def wrap(func):
        def queued_task(*args, **kw):

            @simpleton(path=kw.get('path'))
            def db_modificator(obj):
                with transaction.manager:
                    result = func(obj, *args, **kw)
                return result

            try:
                db = config(ZOPE_CONF, None, ())
                connection = db.open()
                root = connection.root()
                root_folder = root.get(ZopePublication.root_name, None)
                setSite(root_folder['app'])
                obj = resolve(getSite(), kw.get('path'))
                result = db_modificator(obj)
            finally:
                setSite(None)
                db.close()

            return result
                
        queued_task.__name__ = func.__name__
        return celery.task(base=AfterCommitTask, **kwargs)(queued_task)
    return wrap
