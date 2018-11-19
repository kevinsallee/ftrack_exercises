import json
import logging
from collections import namedtuple

import ftrack_api

from typing import Any, Dict
from location import custom_location_plugin

ACTION_IDENTIFIER = '98f4ab90642b4880916302f4bedce6d7'
EntityInfo = namedtuple("EntityInfo", "id type name")

logging.basicConfig()
logger = logging.getLogger(__name__)


def get_full_name(entity):
    # type: (Entity) -> str
    """
    Given a Task or an AssetVersion, return a "full name" for it.
    Note: Normally the type should be Union[Task, AssetVersion] but I was not sure how the task was instantiated since
    upon inspection it just tells me it's an dynamic class from abc module...
    """
    return " / ".join([l['name'] for l in entity['link']])


def copy_from_location_a_to_location_b(event):
    # type: (Dict[str, Any]) -> None
    """
    When missing descriptions are received,
    1/ if they're not empty again, add them to the entities for which they were edited
    2/ if at least one is empty, re-suscribe the source event to get a web UI again for the missing ones.
    """
    username = event['source']['user']['username']
    location_id = event['data']['location_id']
    component_id = event['data']['component_id']
    location = session.query("select name from Location where id is {}".format(location_id)).one()
    if location['name'] == "location.a":
        component = session.query("select version_id from Component where id is {}".format(component_id)).one()
        asset_version = session.query("select link from AssetVersion where id is {}"
                                      .format(component['version_id'])).one()
        location_b = session.query('Location where name is "location.b"').one()
        user = session.query('User where username="{}"'.format(username)).one()
        job = session.create('Job', {'user': user, 'status': 'running',
            'data': json.dumps({
                'description': 'Transfer <br>{}<br> from locationA to locationB'.format(
                get_full_name(asset_version))})
        })

        location_b.add_component(component, location)
        message = 'Version {} transferred from locationA to locationB'.format(get_full_name(asset_version))
        send_message(username, message, True)
        job['status'] = 'done'
        session.commit()


def send_message(username, msg_str, success):
    # type: (str, bool) -> None
    action_event = ftrack_api.event.base.Event(
        topic='ftrack.action.trigger-user-interface',
        data={
            'type': 'message',
            'success': success,
            'message': msg_str
        },
        target=(
            'applicationId=ftrack.client.web and user.username="{0}"'.format(username)
        ),
    )
    session.event_hub.publish(action_event)


if __name__ == '__main__':
    session = ftrack_api.Session()
    custom_location_plugin.configure_location(session, None)
    session.event_hub.subscribe('topic=ftrack.location.component-added', copy_from_location_a_to_location_b)
    session.event_hub.wait()
