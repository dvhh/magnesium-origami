#!/usr/bin/env python3
import os

from urllib.parse import join

import httpx
import uvicorn
import pyvips


configuration = {
    
}


async def reply_error(send, status_code, body=None, content_type=None):
    payload = {
        'type': 'http.response.start',
        'status': 204,
    }
    if content_type is not None:
        payload['headers'] = {}
    await send(payload)

    payload = {
        'type': 'http.response.body'
    }
    if body is not None:
        payload['body'] = body
    await send(payload)


async def get_request_handler(scope, receive, send):
    origin = configuration['origin']
    request = parse_operations(path)
    uri = join(origin, scope['path'])

    async with httpx.AsyncClient() as client:
        async with client.stream('GET', uri) as response:
            if response.status_code != 200:
                await reply_error(send, response.status_code)
                return
            await response.aread()

    await reply_error(send, 501)


async def head_request_handler(scope, receive, send):
    await reply_error(send, 501)


async def fallback_handler(scope, receive, send):
    await reply_error(send, 405)


async def app(scope, receive, send):
    assert scope['type'] == 'http'

    handlers = {
        'GET': get_request_handler(),
        'HEAD': handle_head()
    }
    handler = handlers.get(
        scope['method'],
        fallback_handler
    )
    await handler(scope, receive, send)


if __name__ == "__main__":
    # origin = os.getenv('origin')
    uvicorn.run("min:app", host="0.0.0.0", port=5000, log_level="info")
