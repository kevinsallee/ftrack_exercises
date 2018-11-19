import json
import logging

import ftrack_api
from ftrack_api import exception
from ftrack_api.entity.base import Entity
from typing import Any, Dict, List, Optional as Opt, Tuple


class CopyAssetBuild(object):
    """Custom action."""

    label = 'Copy Asset Build'
    identifier = 'copy.asset_build'
    description = 'Copy asset build from project A to project B'

    def __init__(self, session):
        # type: (ftrack_api.Session) -> None
        """Initialise action."""
        super(CopyAssetBuild, self).__init__()
        self.session = session
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def register(self):
        # type: () -> None
        """Register action."""
        self.session.event_hub.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                self.session.api_user
            ),
            self.discover
        )
        self.session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0} and '
            'source.user.username={1}'.format(
                self.identifier,
                self.session.api_user
            ),
            self.launch
        )

    def discover(self, event):
        # type: (Dict[str, Any]) -> Opt[Dict[str, Any]]
        """Return action config if triggered on a single asset build."""
        data = event['data']

        # If selection contains more than one item return early since
        # this action can only handle a single asset build.
        selection = data.get('selection', [])
        self.logger.info('Got selection: {0}'.format(selection))
        if len(selection) != 1 or selection[0]['entityType'] != 'task':
            return

        if not self.session.get("AssetBuild", selection[0]['entityId']):
            return
        return {
            'items': [{
                'label': self.label,
                'description': self.description,
                'actionIdentifier': self.identifier
            }]
        }

    def launch(self, event):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """Callback method for custom action."""
        asset_build_id = event['data']['selection'][0]['entityId']
        if 'values' in event['data']:
            values = event['data']['values']
            source_project_id = values['source_project_id']
            destination_project_id = values['destination_project_id']
            if destination_project_id:
                source_project = self.session.query(
                    'select full_name from Project where id is "{}"'.format(source_project_id)).one()
                destination_project = self.session.query(
                    'select full_name from Project where id is "{}"'.format(destination_project_id)).one()
                asset_build = self.session.query(
                    'select name from AssetBuild where id is "{}"'.format(asset_build_id)).one()
                user_id = event['source']['user']['id']
                user = self.session.get("User", user_id)
                job = self.session.create(
                    'Job',
                    {'user': user, 'status': 'running', 'data': json.dumps({
                        'description': 'Copy {}<br>from {} to {}'.format(
                            asset_build['name'], source_project['full_name'], destination_project['full_name'])})
                     })
                success, message = self.copy_asset_build(asset_build, source_project, destination_project)

                if success:
                    job['status'] = 'done'
                else:
                    job['status'] = 'failed'
                self.session.commit()
                return {
                    'success': success,
                    'message': message
                }

        asset_build_id = event['data']['selection'][0]['entityId']
        return self.get_form(asset_build_id)

    def copy_asset_build(self, asset_build, source_project, destination_project):
        # type: (Entity, Entity, Entity) -> Tuple[bool, str]
        """ Copies asset_build from source_project to destination_project.
        It just copies it empty, with a link to the source project.
        A deep copy would require some more effort."""
        tmp_session = ftrack_api.Session()
        asset_build_unique_name = self.get_unique_name(asset_build['name'], destination_project)
        new_asset_build_data = {
            'name': asset_build_unique_name,
            'parent': destination_project,
            'description': 'Copied from {}'.format(source_project['full_name'])
        }
        try:
            new_asset_build = tmp_session.create('AssetBuild', new_asset_build_data)
            tmp_session.create('TypedContextLink', {'from': new_asset_build, 'to': asset_build})
            tmp_session.commit()
        except exception.ServerError as e:
            return False, "Could not copy {} to {}:<br>{}".format(
                asset_build['name'], destination_project['full_name'], str(e))
        finally:
            tmp_session.close()

        return True, 'Copied {} from {} to {} as {}'.format(
            asset_build['name'], source_project['full_name'], destination_project['full_name'], asset_build_unique_name)

    def get_unique_name(self, asset_build_name, project):
        # type: (str, Entity) -> str
        i = 0
        while True:
            if not i:
                asset_build_new_name = asset_build_name
            else:
                asset_build_new_name = "{} ({})".format(asset_build_name, i)
            query_str = 'AssetBuild where name is "{}" and project_id is {}'.format(asset_build_new_name, project['id'])
            asset_build = self.session.query(query_str).first()
            if not asset_build:
                return asset_build_new_name
            i += 1

    def get_form(self, asset_build_id):
        # type: (str) -> Dict[str, Any]
        asset_build = self.session.query('select project.full_name, project.id from AssetBuild where id is "{}"'.format(
            asset_build_id)).one()

        return {'items': [
            {
                'type': 'label',
                'value': 'From:{}{}'.format('&nbsp;' * 8, asset_build['project']['full_name'])
            },
            {
                'type': 'hidden',
                'name': 'source_project_id',
                'value': asset_build['project']['id']
            },
            {
                'label': 'To:',
                'type': 'enumerator',
                'name': 'destination_project_id',
                'data': self.get_other_projects_dict(asset_build['project']['id'])
            }]}

    def get_other_projects_dict(self, project_id):
        # type: (str) -> List[Dict[str, Any]]
        """Return all active projects different from the one which id is provided"""
        query_str = "select full_name from Project where status is active and id is_not {}".format(project_id)
        projects = self.session.query(query_str).all()
        return [{'label': p['full_name'], 'value': p['id']} for p in projects]


def register(session, **kw):
    # type: (ftrack_api.Session, Any) -> None
    """Register plugin."""
    del kw
    # Validate that session is an instance of ftrack_api.Session. If not,
    # assume that register is being called from an incompatible API
    # and return without doing anything.
    if not isinstance(session, ftrack_api.Session):
        # Exit to avoid registering this plugin again.
        return

    action = CopyAssetBuild(session)
    action.register()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    ftrack_session = ftrack_api.Session()
    register(ftrack_session)

    # Wait for events.
    ftrack_session.event_hub.wait()
