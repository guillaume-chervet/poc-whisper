from http import HTTPStatus

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from authentication import Authentication, IHttpServiceGet


def authentication_middleware(issuer: str,
                              scopes: list[str],
                              api_audience: str,
                              exclude_urls: list[str],
                              service: IHttpServiceGet):
    authentication = Authentication(issuer, scopes, api_audience, service)

    class AuthenticateMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
            try:
                if request.url.path in exclude_urls or request.method == "OPTIONS":
                    response = await call_next(request)
                    return response

                authorization = request.headers.get('Authorization')
                if not authorization:
                    return Response(status_code=HTTPStatus.UNAUTHORIZED)
                validation_result = await authentication.validate_async(authorization.replace("Bearer ", ""))
                if not validation_result.success:
                    return Response(status_code=HTTPStatus.UNAUTHORIZED)
                response = await call_next(request)
                return response
            except Exception as e:
                return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                content="Internal Server Error: {0}".format(
                                    str(e)))

    return AuthenticateMiddleware