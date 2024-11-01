
import abc
import asyncio
from dataclasses import dataclass

from httpx import AsyncClient, Client
from jwskate import Jwt
from datetime import datetime


@dataclass
class AuthenticationResult:
    success: bool
    error: str = ""
    payload: dict | None = None


def find_jwk(jwks, jwt):
    jwk_key = None
    jwks_keys = jwks["keys"]
    for key in jwks_keys:
        if key["kid"] == jwt.headers["kid"]:
            jwk_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "alg": key["alg"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    return jwk_key


class IHttpServiceGet(abc.ABC):
    @abc.abstractmethod
    async def get_async(self, url: str) -> dict:
        pass

class XHttpServiceGet(IHttpServiceGet):
    def __init__(self,
                 http_client: Client,
                 http_async_client: AsyncClient):
        self.http_async_client = http_async_client
        self.http_client = http_client

    async def get_async(self, url: str) -> dict:
        reponse = await self.http_async_client.get(url)
        return reponse.json()


class Authentication:
    def __init__(self,
                 issuer: str | None,
                 scopes: list[str],
                 api_audience: str | None,
                 service: IHttpServiceGet):
        self.service = service
        self.issuer = issuer
        self.api_audience = api_audience
        self.algorithms = ["RS256"]
        self.scopes = scopes
        self.cache_timestamp = 0
        self.cache_jwks = None
        self.cache_token_endpoint = None

    async def _get_jwks_async(self, service: IHttpServiceGet, issuer: str) -> dict:
        timestamp = datetime.timestamp(datetime.now())
        one_day = 86400
        if self.cache_timestamp + one_day < timestamp:
            wellknowurl = await service.get_async(issuer + "/.well-known/openid-configuration")
            self.cache_jwks = await service.get_async(wellknowurl["jwks_uri"])
            self.cache_token_endpoint = wellknowurl["token_endpoint"]
            self.cache_timestamp = timestamp

        return self.cache_jwks

    async def get_token_endpoint_async(self) -> str:
        await self._get_jwks_async(self.service, self.issuer)
        return self.cache_token_endpoint

    async def validate_async(self, token: str) -> AuthenticationResult:
        try:
            jwt = Jwt(token)
            if jwt.headers["alg"].upper() not in self.algorithms:
                return AuthenticationResult(success=False, error="wrong algorithm used")
            jwks = await self._get_jwks_async(self.service, self.issuer)
            jwk_key = find_jwk(jwks, jwt)
            if jwk_key is None:
                return AuthenticationResult(success=False, error="JWK key not found")

            payload = jwt.claims
            scopes = payload["scope"].split(" ")
            for scope in self.scopes:
                if scope not in scopes:
                    return AuthenticationResult(success=False, error="scope not found")

            if not self.api_audience:
                if jwt.validate(jwk_key, issuer=self.issuer):
                    return AuthenticationResult(success=False, error="signature verification failed")

            if jwt.validate(jwk_key, issuer=self.issuer, audience=self.api_audience):
                return AuthenticationResult(success=False, error="signature verification failed")

            return AuthenticationResult(success=True, payload=payload)

        except Exception as e:
            exception_message = str(e)
            return AuthenticationResult(success=False, error=exception_message)
