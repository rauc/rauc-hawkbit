# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum


# status of the action execution
CancelStatusExecution = Enum('CancelStatusExecution',
                             'closed proceeding canceled scheduled rejected \
                             resumed')

# defined status of the result
CancelStatusResult = Enum('CancelStatusResultFinished',
                          'success failure none')


class Action(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/cancelAction/{actionId} in
    HawkBit's DDI API.
    """
    def __init__(self, ddi, action_id):
        self.ddi = ddi
        self.action_id = action_id

    async def __call__(self):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_get_tenant_controller_v1_targetid_cancelaction_actionid # noqa
        """
        return await self.ddi.get_resource(
            '/{tenant}/controller/v1/{controllerId}/cancelAction/{actionId}', actionId=self.action_id)

    async def feedback(self, status_execution, status_result,
                       status_details=()):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_post_tenant_controller_v1_targetid_cancelaction_actionid_feedback # noqa
        """
        assert isinstance(status_execution, CancelStatusExecution), \
            'status_execution must be CancelStatusExecution'
        assert isinstance(status_result, CancelStatusResult), \
            'status_result must be CancelStatusResult enum'
        assert isinstance(status_details, (tuple, list)), \
            'status_details must be tuple or list'

        time = datetime.now().strftime('%Y%m%dT%H%M%S')

        post_data = {
            'id': self.action_id,
            'time': time,
            'status': {
                'result': {
                    'finished': status_result.name
                },
                'execution': status_execution.name,
                'details': status_details
            }
        }

        return await self.ddi.post_resource(
            '/{tenant}/controller/v1/{controllerId}/cancelAction/{actionId}/feedback', post_data, actionId=self.action_id)


class CancelAction(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/cancelAction in HawkBit's DDI
    API.
    """
    def __init__(self, ddi):
        self.ddi = ddi

    def __getitem__(self, key):
        action_id = key
        return Action(self.ddi, action_id)
