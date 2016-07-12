# -*- coding: utf-8 -*-

from datetime import datetime
from enum import Enum

# status of the action execution
DeploymentStatusExecution = Enum('DeploymentStatusExecution',
                                 'closed proceeding canceled scheduled \
                                 rejected resumed')

# defined status of the result
DeploymentStatusResult = Enum('DeploymentStatusResultFinished',
                              'success failure none')

# handling for the update part of the provisioning process
DeploymentUpdate = Enum('DeploymentUpdate',
                        'skip attempt forced')


class DeploymentBaseAction(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/deploymentBase/{actionId}
    in HawkBit's DDI API.
    See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_get_tenant_controller_v1_targetid_deploymentbase_actionid # noqa
    """

    def __init__(self, ddi, action_id):
        self.ddi = ddi
        self.action_id = action_id

    async def __call__(self, resource=None):
        return await self.ddi.get_resource(
            '/{tenant}/controller/v1/{controllerId}/deploymentBase/{actionId}', {'c': resource}, actionId=self.action_id)

    async def feedback(self, status_execution, status_result,
                       status_details=(), **kwstatus_result_progress):
        """
        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_post_tenant_controller_v1_targetid_deploymentbase_actionid_feedback # noqa
        """
        assert isinstance(status_execution, DeploymentStatusExecution), \
            'status_execution must be DeploymentStatusExecution enum'
        assert isinstance(status_result, DeploymentStatusResult), \
            'status_result must be DeploymentStatusResult enum'
        assert isinstance(status_details, (tuple, list)), \
            'status_details must be tuple or list'

        time = datetime.now().strftime('%Y%m%dT%H%M%S')

        post_data = {
            'id': self.action_id,
            'time': time,
            'status': {
                'result': {
                    'progress': kwstatus_result_progress,
                    'finished': status_result.name
                },
                'execution': status_execution.name,
                'details': status_details
            }
        }

        return await self.ddi.post_resource(
            '/{tenant}/controller/v1/{controllerId}/deploymentBase/{actionId}/feedback', post_data, actionId=self.action_id)


class DeploymentBase(object):
    """
    Represents /{tenant}/controller/v1/{targetid}/deploymentBase in HawkBit's
    DDI API.
    """
    def __init__(self, ddi):
        self.ddi = ddi

    def __getitem__(self, key):
        action_id = key
        return DeploymentBaseAction(self.ddi, action_id)
