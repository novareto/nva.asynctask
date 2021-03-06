# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import kombu
import celery
import transaction
import zope.location

from ZODB.interfaces import IDatabase
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.location.interfaces import ILocationInfo
from .conf import celery_app


class ZopeTask(celery.Task):
    """ A database task knowns:
    1. to find the root of the database
    2. to execute the code in a transaction
    """
    abstract = True
    _conn = None

    def get_connection(self):
        if self._conn is None:
            self._conn = getUtility(IDatabase).open()
        return self._conn

    def delay(self, *args, **kwargs):
        if 'context' in kwargs and not 'oid' in kwargs:
            context = kwargs.pop('context')
            kwargs['oid'] = context._p_oid
        return celery.Task.delay(self, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        conn = self.get_connection()
        try:
            with transaction.manager:
                if 'oid' in kwargs and not 'context' in kwargs:
                    oid = kwargs.pop('oid')
                    kwargs['context'] = conn.get(oid)
                if 'context' in kwargs:
                    location_info = ILocationInfo(kwargs['context'])
                    setSite(location_info.getNearestSite())
                return self.run(*args, **kwargs)
        except Exception as e:
            self.retry(exc=e)


class TransactionAwareTask(celery.Task):
    """
    Only give the task to the broker on successful commit of the
    transaction.
    """
    abstract = True

    def apply_async(self, *args, **kwargs):
        task_id = kombu.utils.uuid()

        def hook(success):
            if success:
                celery.Task.apply_async(self, *args, **kwargs)

        transaction.get().addAfterCommitHook(hook)
        return self.AsyncResult(task_id)


class ZopeTransactionalTask(ZopeTask, TransactionAwareTask):
    abstract = True


def transactional_task(func):
    return celery_app.task(base=TransactionAwareTask)(func)


def zope_task(func):
    return celery_app.task(base=ZopeTransactionalTask)(func)
