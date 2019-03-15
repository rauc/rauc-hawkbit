# -*- coding: utf-8 -*-

import aiohttp
import aiohttp.web
import json
import hashlib
import logging

from datetime import datetime
from enum import Enum

from .deployment_base import DeploymentBase
from .softwaremodules import SoftwareModules
from .cancel_action import CancelAction

# status of the action execution
ConfigStatusExecution = Enum('ConfigStatusExecution',
                             'closed proceeding canceled scheduled rejected \
                             resumed')

# defined status of the result
ConfigStatusResult = Enum('ConfigStatusResultFinished',
                          'success failure none')


class APIError(Exception):
    pass


class DDIClient(object):
    """
    Base Direct Device Integration API client providing GET, POST and PUT
    helpers as well as access to next level API resources.
    """

    error_responses = {
        400: 'Bad Request - e.g. invalid parameters',
        401: 'The request requires user authentication.',
        403: 'Insufficient permissions or data volume restriction applies.',
        404: 'Resource not available or device unknown.',
        405: 'Method Not Allowed',
        406: 'Accept header is specified and is not application/json.',
        429: 'Too many requests.'
    }

    def __init__(self, session, host, ssl, auth_token, tenant_id, controller_id, timeout=10):
        self.session = session
        self.host = host
        self.ssl = ssl
        self.logger = logging.getLogger('rauc_hawkbit')
        self.headers = {'Authorization': 'TargetToken {}'.format(auth_token)}
        self.tenant = tenant_id
        self.controller_id = controller_id
        self.timeout = timeout
        # URL parts which get replaced lateron
        self.placeholders = ['tenant', 'target', 'softwaremodule', 'action',
                             'filename']
        self.replacements = {
            '/MD5SUM': '.MD5SUM'
        }

    @property
    def cancelAction(self):
        return CancelAction(self)

    @property
    def softwaremodules(self):
        return SoftwareModules(self)

    @property
    def deploymentBase(self):
        return DeploymentBase(self)

    async def __call__(self):
        """
        Base poll resource

        See https://docs.bosch-iot-rollouts.com/documentation/rest-api/rootcontroller-api-guide.html#_controller_base_poll_resource

        Returns: JSON data
        """
        return await self.get_resource('/{tenant}/controller/v1/{controllerId}')

    async def configData(self, status_execution, status_result, action_id='',
                         status_details=(), **kwdata):
        """
        Provide meta informtion during device registration at the update
        server.

        See http://sp.apps.bosch-iot-cloud.com/documentation/rest-api/rootcontroller-api-guide.html#_put_tenant_controller_v1_targetid_configdata # noqa

        Args:
           status_execution(ConfigStatusExecution): status of the action execution
           status_result(status_result): result of the action execution

        Keyword Args:
           action_id(str): Id of the action, not mandator for configData
           status_details((tuple, list)): List of details to provide
           other: passed as custom configuration data (key/value)
        """
        assert isinstance(action_id, str), 'id must be string'
        assert isinstance(status_result, ConfigStatusResult), \
            'status_result_finished must be ConfigStatusResult enum'
        assert isinstance(status_execution, ConfigStatusExecution), \
            'status_execution must be ConfigStatusExecution enum'
        assert isinstance(status_details, (tuple, list)), \
            'status_details must be tuple or list'
        assert len(kwdata) > 0

        time = datetime.now().strftime('%Y%m%dT%H%M%S')

        put_data = {
            'id': action_id,
            'time': time,
            'status': {
                'result': {
                    'finished': status_result.name
                },
                'execution': status_execution.name,
                'details': status_details
            },
            'data': kwdata
        }

        await self.put_resource('/{tenant}/controller/v1/{controllerId}/configData', put_data)


    def build_api_url(self, api_path):
        """
        Build the actual API URL.

        Args:
            api_path(str): REST API path

        Returns:
            Expanded API URL with protocol (http/https) and host prepended
        """
        protocol = 'https' if self.ssl else 'http'
        return '{protocol}://{host}/{api_path}'.format(
            protocol=protocol, host=self.host, api_path=api_path)

    async def get_resource(self, api_path, query_params={}, **kwargs):
        """
        Helper method for HTTP GET API requests.

        Args:
            api_path(str): REST API path
        Keyword Args:
            query_params: Query parameters to add to the API URL
            kwargs: Other keyword args used for replacing items in the API path

        Returns:
            Response JSON data
        """
        get_headers = {
            'Accept': 'application/json',
            **self.headers
        }
        url = self.build_api_url(
                api_path.format(
                    tenant=self.tenant,
                    controllerId=self.controller_id,
                    **kwargs))

        self.logger.debug('GET {}'.format(url))
        async with self.session.get(url, headers=get_headers,
                                    params=query_params) as resp:
            await self.check_http_status(resp)
            json = await resp.json()
            self.logger.debug(json)
            return json

    async def get_binary_resource(self, api_path, dl_location,
                                  mime='application/octet-stream',
                                  chunk_size=512, timeout=3600, **kwargs):
        """
        Helper method for binary HTTP GET API requests.

        Triggers download of the retreived content to ``dl_location``.

        Args:
            api_path(str): REST API path
            dl_location(str): storage path for downloaded artifact
        Keyword Args:
            mime: mimetype of content to retrieve
                  (default: 'application/octet-stream')
            chunk_size: size of chunk to retrieve
            kwargs: Other keyword args used for replacing items in the API path

        Returns:
            MD5 hash of downloaded content
        """
        url = self.build_api_url(
                api_path.format(
                    tenant=self.tenant,
                    controllerId=self.controller_id,
                    **kwargs))
        return await self.get_binary(url, dl_location, mime, chunk_size,
                                     timeout=timeout)

    async def get_binary(self, url, dl_location,
                         mime='application/octet-stream', chunk_size=512,
                         timeout=3600):
        """
        Actual download method with checksum checking.

        Args:
            url(str): URL of item to download
            dl_location(str): storage path for downloaded artifact
        Keyword Args:
            mime: mimetype of content to retrieve
                  (default: 'application/octet-stream')
            chunk_size: size of chunk to retrieve
            timeout: download timeout
                     (default: 3600)

        Returns:
            MD5 hash of downloaded content
        """
        get_bin_headers = {
            'Accept': mime,
            **self.headers
        }
        hash_md5 = hashlib.md5()

        self.logger.debug('GET binary {}'.format(url))
        length = 0
        done = False
        with open(dl_location, 'wb') as fd:
            while not done:
                async with self.session.get(url, headers=get_bin_headers) as resp:
                    await self.check_http_status(resp)
                    while not resp.content.at_eof():
                        try:
                            chunk, _ = await resp.content.readchunk()
                            if not chunk:
                                done = True
                                break
                            else:
                                length += len(chunk)
                            fd.write(chunk)
                            hash_md5.update(chunk)
                        except aiohttp.client_exceptions.ClientPayloadError as e:
                            self.logger.debug("Connection closed by remote -- retrying to connect and resume from {} bytes".format(length))
                            get_bin_headers['Range'] = 'bytes={}-'.format(length)
                            break
                        except Exception as e:
                            raise e

                    if resp.content.at_eof():
                        done = True

        return hash_md5.hexdigest()

    async def post_resource(self, api_path, data, **kwargs):
        """
        Helper method for HTTP POST API requests.

        Args:
            api_path(str): REST API path
            data: JSON data for POST request
        Keyword Args:
            kwargs: keyword args used for replacing items in the API path
        """
        post_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            **self.headers
        }
        url = self.build_api_url(
                api_path.format(
                    tenant=self.tenant,
                    controllerId=self.controller_id,
                    **kwargs))
        self.logger.debug('POST {}'.format(url))
        async with self.session.post(url, headers=post_headers,
                                        data=json.dumps(data)) as resp:
            await self.check_http_status(resp)

    async def put_resource(self, api_path, data, **kwargs):
        """
        Helper method for HTTP PUT API requests.

        Args:
            api_path(str): REST API path
            data: JSON data for POST request
        Keyword Args:
            kwargs: keyword args used for replacing items in the API path
        """
        put_headers = {
            'Content-Type': 'application/json',
            **self.headers
        }
        url = self.build_api_url(
                api_path.format(
                    tenant=self.tenant,
                    controllerId=self.controller_id,
                    **kwargs))
        self.logger.debug('PUT {}'.format(url))
        self.logger.debug(json.dumps(data))
        async with self.session.put(url, headers=put_headers,
                                    data=json.dumps(data)) as resp:
            await self.check_http_status(resp)

    async def check_http_status(self, resp):
        """Log API error message."""
        if resp.status not in [200, 206]:
            error_description = await resp.text()
            if error_description:
                self.logger.debug('API error: {}'.format(error_description))

            if resp.status in self.error_responses:
                reason = self.error_responses[resp.status]
            else:
                reason = resp.reason

            raise APIError('{status}: {reason}'.format(
                status=resp.status, reason=reason))
