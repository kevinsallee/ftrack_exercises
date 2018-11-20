# :coding: utf-8
# :copyright: Copyright (c) 2018 ftrack

import os
import functools
import logging

import ftrack_api
import ftrack_api.accessor.disk

import structure

logger = logging.getLogger(
    'com.ftrack.recipes.customise_structure.location.custom_location_plugin'
)

# Name of the location plugin.
LOCATION_NAMES = ['location.a', 'location.b']

# Disk mount point.
DISK_PREFIXES = ['/Users/kevin/ftrack/locationA', '/Users/kevin/ftrack/locationB']


def configure_location(session, event):
    '''Listen.'''
    for location_name, disk_prefix in zip(LOCATION_NAMES, DISK_PREFIXES):
        location = session.ensure('Location', {'name': location_name})

        location.accessor = ftrack_api.accessor.disk.DiskAccessor(
            prefix=disk_prefix
        )
        location.structure = structure.Structure()
        location.priority = 1

        logger.info(
            u'Registered location {0} at {1}.'.format(location_name, disk_prefix)
        )


def register(api_object, **kw):
    '''Register location with *session*.'''

    if not isinstance(api_object, ftrack_api.Session):
        return

    for disk_prefix in DISK_PREFIXES:
        if not disk_prefix:
            logger.error('No disk prefix configured for location.')
            return

        if not os.path.exists(disk_prefix) or not os.path.isdir(disk_prefix):
            logger.error('Disk prefix location does not exist.')
            return

    api_object.event_hub.subscribe(
        'topic=ftrack.api.session.configure-location',
        functools.partial(configure_location, api_object)
    )
