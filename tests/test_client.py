import pytest
import aiohttp
import asyncio
from aiohttp import web

from rauc_hawkbit.ddi.client import DDIClient
from rauc_hawkbit.ddi.client import APIError

async def hello(request):
    data = {
        "config" : {
            "polling" : {
                "sleep" : "12:00:00"
            }
        },
        "_links" : {
            "deploymentBase" : {
                "href" : "https://rollouts-cs.apps.bosch-iot-cloud.com/TENANT_ID/controller/v1/CONTROLLER_ID/deploymentBase/3?c=-2129030598"
            },
            "configData" : {
                "href" : "https://rollouts-cs.apps.bosch-iot-cloud.com/TENANT_ID/controller/v1/CONTROLLER_ID/configData"
            }
        }
    }
    return web.json_response(data)

def create_app(loop):
    app = web.Application()
    app.router.add_route('GET', '/DEFAULT/controller/v1/test-target', hello)
    return app

async def test_get_resource_valid(test_client):
    client = await test_client(create_app)

    ddi = DDIClient(client.session, '{}:{}'.format(client.host, client.port), False, None, None, '/DEFAULT', 'test-target')
    resp = await ddi.get_resource('{tenant}/controller/v1/{controllerId}')

    assert 'config' in resp
    assert '_links' in resp

async def test_get_resource_invalid_key(test_client):
    client = await test_client(create_app)

    ddi = DDIClient(client.session, '{}:{}'.format(client.host, client.port), False, None, None, '/DEFAULT', 'test-target')

    with pytest.raises(KeyError):
        resp = await ddi.get_resource('{tenant}/controller/v1/{dummy}')

async def test_get_resource_invalid_path(test_client):
    client = await test_client(create_app)

    ddi = DDIClient(client.session, '{}:{}'.format(client.host, client.port), False, None, None, '/DEFAULT', 'test-target')

    with pytest.raises(APIError):
        resp = await ddi.get_resource('{tenant}/controller/v2')
