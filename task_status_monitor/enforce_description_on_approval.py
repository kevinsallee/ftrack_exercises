import logging
from collections import namedtuple

import ftrack_api
from ftrack_api.entity.base import Entity
from typing import List, Any, Dict

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
    return " / ".join([l['name'] for l in entity['link'][1:]])


def get_approved_entities_with_no_description(entities):
    # type: (List[Dict[str, Any]]) -> List[EntityInfo]
    """
    Get a list of entities from an event, and return a list of EntityInfo of entities which were approved but have no
    description (tasks and assetversions only)
    """
    task_ids = [entity['entityId'] for entity in entities if entity['entityType'] == 'task' and 'statusid' in
                entity['keys']]
    version_ids = [entity['entityId'] for entity in entities if entity['entityType'] == 'assetversion' and
                   "statusid" in entity["keys"]]
    result = get_approved_tasks_with_no_description(task_ids)
    result.extend(get_approved_versions_with_no_description(version_ids))
    return result


def get_approved_tasks_with_no_description(task_ids):
    # type: (List[str]) -> List[EntityInfo]
    if not task_ids:
        return []
    task_ids_str = "(" + ",".join(task_ids) + ")"
    tasks = session.query("select link from Task where id in {} and description is '' and status.name is Approved"
                          .format(task_ids_str)).all()
    return [EntityInfo(id=task['id'], name=get_full_name(task), type="Task") for task in tasks]


def get_approved_versions_with_no_description(version_ids):
    # type: (List[str]) -> List[EntityInfo]
    if not version_ids:
        return []
    version_ids_str = "(" + ",".join(version_ids) + ")"
    versions = session.query("select link from AssetVersion where id in {} and comment is '' and status.name is "
                             "Approved".format(version_ids_str)).all()
    return [EntityInfo(id=version['id'], type='AssetVersion', name=get_full_name(version))
            for version in versions]


def enforce_entity_description_on_approval(event):
    # type: (Dict[str, Any]) -> None
    """
    When an event has tasks or asset versions which were approved, but have no description,
    create a web UI form forcing the user to enter the missing descriptions
    """
    data = event['data']
    user_id = event['source']['user']['id']
    entities = data.get('entities', [])
    invalid_entities = get_approved_entities_with_no_description(entities)
    if not invalid_entities:
        return
    items = [{'type': 'hidden', 'value': event, 'name': 'source_event'}]
    for entity_info in invalid_entities:
        items.extend([
            {
                'type': 'label',
                'value': entity_info.name
            },
            {
                'type': 'text',
                'name': 'description__{}__{}'.format(entity_info.type, entity_info.id),
                'label': 'Description'
            }
        ])
    action_event = ftrack_api.event.base.Event(
        topic='ftrack.action.trigger-user-interface',
        data={
            'type': 'form',
            'items': items,
            'title': 'These approved elements need a description!',
            'actionIdentifier': ACTION_IDENTIFIER,
        },
        target=(
            'applicationId=ftrack.client.web and user.id={0}'.format(user_id)
        ),
    )
    session.event_hub.publish(action_event)


def handle_missing_descriptions(event):
    # type: (Dict[str, Any]) -> None
    """
    When missing descriptions are received,
    1/ if they're not empty again, add them to the entities for which they were edited
    2/ if at least one is empty, re-suscribe the source event to get a web UI again for the missing ones.
    """
    user_id = event['source']['user']['id']
    values = event['data']['values']
    source_event = values.pop("source_event")
    for key, description in values.items():
        if description:
            _, entity_type, entity_id = key.split("__")
            entity = session.get(entity_type, entity_id)
            if entity_type == "Task":
                entity['description'] = description
            else:
                entity['comment'] = description
    if [v for v in values.values() if v]:
        session.commit()
    if [v for v in values.values() if not v]:
        session.event_hub.publish(source_event)
    else:
        action_event = ftrack_api.event.base.Event(
            topic='ftrack.action.trigger-user-interface',
            data={
                'type': 'message',
                'success': True,
                'message': 'Descriptions updated! Please Refresh',
            },
            target=(
                'applicationId=ftrack.client.web and user.id={0}'.format(user_id)
            ),
        )
        session.event_hub.publish(action_event)


if __name__ == '__main__':
    session = ftrack_api.Session(server_url='https://playground.ftrackapp.com',
                                 api_key='MYKEY',
                                 api_user='kevin.sallee@gmail.com')

    session.event_hub.subscribe('topic=ftrack.update', enforce_entity_description_on_approval)
    session.event_hub.subscribe('topic=ftrack.action.launch and data.actionIdentifier={}'.format(ACTION_IDENTIFIER),
                                handle_missing_descriptions)
    session.event_hub.wait()
