# -*- coding: utf-8 -*-

import celery

celery_app = celery.Celery()
celery_app.config_from_object('celeryconfig')

ZOPE_CONF = celery_app.conf.get('ZOPE_CONF')
SITE_ZCML = celery_app.conf.get('SITE_ZCML')
