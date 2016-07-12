import aiohttp
import asyncio
from aiohttp import web

from rauc_hawkbit.ddi.client import DDIClient

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
    #app.router.add_route('GET', '/', hello)
    #app.router.add_get('/', hello)
    return app

async def test_hello(test_client):
    client = await test_client(create_app)

    ddi = DDIClient(client.session, '{}:{}'.format(client.host, client.port), False, None, 'DEFAULT', 'test-target')
    resp = await ddi.get_resource('{tenant}/controller/v1/{controllerId}')

    assert 'config' in resp
    assert '_links' in resp
