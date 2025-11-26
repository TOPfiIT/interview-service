from cryptography.hazmat.primitives import serialization
from jose import jwt, JWTError
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import ORJSONResponse
from typing import Any
from loguru import logger
import time


class JWTManager:
    """
    JWT Authentication manager
    """

    def __init__(self, jwt_public_key: str):
        """
        Initialize the JWT Authentication manager
        :param jwt_private_key: JWT private key
        """

        self.jwt_private_key = self.load_pubkey(jwt_public_key)
        self.algorithm = "ES256"

    def load_pubkey(self, pubkey: str) -> Any:
        """
        Load public key
        :param pubkey: string of public key
        :return: deserialized public key
        """

        public_key = serialization.load_pem_public_key(
            pubkey.encode(),
        )

        return public_key

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        Verify token
        :param token: Token
        :return: Token payload
        """

        try:
            payload = jwt.decode(
                token,
                self.jwt_private_key,
                algorithms=[self.algorithm],
            )
            return payload
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
            )

    async def __call__(self, request: Request, call_next) -> Response:
        """
        Call the middleware
        :param request: Request object
        :param call_next: Next middleware or endpoint function
        :return: Response object
        """

        logger.info("JWT Middleware")
        logger.debug(f"Request: {request.url}")
        logger.debug(f"Method: {request.method}")

        if (
            "/api/v1/room" in request.url.path
            and request.method == "POST"
            or "docs" in request.url.path
            or "openapi.json" in request.url.path
        ):
            logger.debug("Room creation request")
            return await call_next(request)

        token = request.cookies.get("room_token")

        if not token:
            return ORJSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "No token provided"},
            )

        try:
            payload = self.verify_token(token)
            request.state.room = payload

            if "exp" in payload and payload["exp"] < int(time.time()):
                return ORJSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token expired"},
                )

            return await call_next(request)
        except HTTPException as e:
            return ORJSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )
