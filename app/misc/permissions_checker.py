# pylint: disable=R1720,R1705,R0911
from base64 import b64decode
from typing import Optional, Tuple

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.authentication import AuthCredentials, AuthenticationBackend, BaseUser, UnauthenticatedUser

from app.exception import AppException, AuthException, AuthHeaderException, JWTDecodeException, JWTExpiredSignatureError
from app.misc.constants import TAG_ADMIN


class AuthenticatedUser(BaseUser):
    def __init__(self, token: dict, auth_method: str) -> None:
        self.token = token
        self.auth_method = auth_method

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.token["email"]

    @property
    def identity(self) -> str:
        return str(self.token["identity_id"])


class OptionalHTTPBearer(HTTPBearer):
    """
    Optional HTTP Bearer.

    This class is used to make the HTTP Bearer optional (disabled in configuration).
    """

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        """Call."""
        if not request.app.state.config["auth"]["sso"]["enable"]:
            return

        try:
            return await super().__call__(request)
        except (Exception, HTTPException) as exp:
            ex = AppException(
                status_code=401,
                message="Missing authorization token",
                error_type=exp.__class__.__name__,
                is_warning=True,
            )
            ex.log_exception()
            return None


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        auth_cfg = conn.app.state.config["auth"]

        if "Authorization" not in conn.headers:
            # no auth header, therefore the user is not authenticated
            return None

        auth = conn.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            scheme = scheme.lower()
            if scheme == "bearer":
                # bearer auth scheme
                if auth_cfg["sso"]["enable"]:
                    # decode the json web token
                    token = decode_jwt_token(credentials)
                    return AuthCredentials(["authenticated"]), AuthenticatedUser(token=token, auth_method=scheme)
                else:
                    # SSO may be disabled for local development and testing
                    return None

            elif scheme == "basic":
                # basic auth scheme
                if auth_cfg["basic"]["enable"]:
                    b64decoded = b64decode(credentials).decode("utf-8")
                    login, password = b64decoded.split(":")
                    if login != auth_cfg["basic"]["login"] or password != auth_cfg["basic"]["password"]:
                        # invalid login or password
                        raise AuthException(message="Invalid password")

                    return AuthCredentials(["authenticated"]), AuthenticatedUser(
                        token={"email": login, "identity_id": login}, auth_method=scheme
                    )
                else:
                    # basic auth is disabled
                    return None

            else:
                # unsupported auth scheme
                return AuthCredentials(), UnauthenticatedUser()

        except ValueError as ex:
            # invalid auth header
            raise AuthHeaderException(message="Invalid Authorization header") from ex
        except jwt.ExpiredSignatureError:
            # the token has expired
            raise JWTDecodeException(message="jwt: token ExpiredSignatureError") from jwt.ExpiredSignatureError
        except jwt.DecodeError:
            # the token is invalid
            raise JWTDecodeException(message="jwt: token DecodeError") from jwt.DecodeError


async def user_is_authenticated(
    request: Request,
    _credentials: HTTPAuthorizationCredentials = Depends(OptionalHTTPBearer(auto_error=False)),
) -> None:
    """Check if the user is authenticated."""

    # Assume the user is authenticated
    auth_sso_enabled = request.app.state.config["auth"]["sso"]["enable"]
    auth_basic_enabled = request.app.state.config["auth"]["basic"]["enable"]
    if not auth_sso_enabled and not auth_basic_enabled:
        return

    if not request.user.is_authenticated:
        raise HTTPException(status_code=401, detail="User is not authenticated")
        # raise AppException(
        #     status_code=401, message="User is not authenticated", is_warning=True
        # )

    if request.user.auth_method == "basic":
        # User logged with basic auth has all permissions
        # it's only used by trusted inner services (sophia live)
        return

    # Check if the user has admin permissions
    if TAG_ADMIN in request.scope["route"].tags:
        if not request.app.state.auth_client.user_has_admin_role(user_uuid=request.user.identity):
            raise AppException(
                status_code=403,
                message=f"User {request.user.display_name} does not have admin permissions",
            )


def check_demo_permissions(
    request: Request,
    operation_id: str,
    **kwargs,
) -> None:
    # note: the variable "operation_id" can be used to check the permissions for the specific operation
    try:
        if not request.user.is_authenticated and not request.app.state.config["auth"]["sso"]["enable"]:
            # Debug mode: no user is authenticated and SSO is disabled
            return

        allowed = request.app.state.auth_client.user_has_permissions(
            user_uuid=request.user.identity,
            operation_id=operation_id,
            request=request,
            **kwargs,
        )
    except AppException as ex:
        raise ex
    except HTTPException as ex:
        raise AppException(
            message=f"Failed to get permissions for {request.user.display_name}",
            error_type="AppException",
            status_code=500,
        ) from ex
    else:
        if not allowed:
            raise AppException(
                status_code=403,
                message=f"User {request.user.display_name} does not have enough permissions"
                f" for the operation {operation_id}",
                is_warning=True,
            )


def decode_jwt_token(token: str) -> dict:
    """Decode a JWT token."""
    try:
        # TODO should verify the signature, it may be implemented in the future
        payload = jwt.decode(
            token,
            algorithms=["HS256"],
            options={
                "verify_signature": False,
                "verify_exp": True,
            },
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise JWTExpiredSignatureError(message="jwt: token ExpiredSignatureError") from jwt.ExpiredSignatureError
    except jwt.DecodeError:
        raise JWTDecodeException(message="jwt: token DecodeError") from jwt.DecodeError


def get_requester_id(request: Request) -> str:
    return request.user.identity if request.user and request.user.is_authenticated else ""
