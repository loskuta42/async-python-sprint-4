import typing

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

ENFORCE_DOMAIN_WILDCARD = "Domain wildcard patterns must be like '*.example.com'."


class BlackListHostMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        blocked_hosts: typing.Optional[typing.Sequence[str]] = None
    ) -> None:
        if blocked_hosts is None:
            blocked_hosts = ['*']

        for pattern in blocked_hosts:
            assert '*' not in pattern[1:], ENFORCE_DOMAIN_WILDCARD
            if pattern.startswith('*') and pattern != '*':
                assert pattern.startswith('*.'), ENFORCE_DOMAIN_WILDCARD
        self.app = app
        self.blocked_hosts = list(blocked_hosts)
        self.block_any = '*' in blocked_hosts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] not in (
            'http',
            'websocket',
        ):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        host = headers.get('host', '').split(':')[0]
        is_valid_host = True
        for pattern in self.blocked_hosts:
            if host == pattern or (
                pattern.startswith('*') and host.endswith(pattern[1:])
            ):
                is_valid_host = False
                break

        if is_valid_host:
            await self.app(scope, receive, send)
        else:
            response: JSONResponse = JSONResponse(status_code=400, content={'error': 'Host in black list'})
            await response(scope, receive, send)
