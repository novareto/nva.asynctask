# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import celery
import redis

celery_app = celery.Celery()
celery_app.config_from_object('celeryconfig')

ZOPE_CONF = celery_app.conf.get('ZOPE_CONF')
SITE_ZCML = celery_app.conf.get('SITE_ZCML')
REDIS_CLIENT = redis.Redis.from_url(celery_app.conf.get('BROKER_URL'))

