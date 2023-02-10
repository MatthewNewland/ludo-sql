from __future__ import annotations
from typing import Any

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlite import (
    ASGIConnection,
    Cookie,
    NotAuthorizedException,
    Response,
    Request,
    Router,
    get,
    post,
)
from starlite.contrib.jwt import JWTCookieAuth, Token

from .db import Base, dto_factory


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str | None] = mapped_column(default=None)
    password: Mapped[str]

    pages: Mapped[list[Page]] = relationship(back_populates="author", lazy="selectin")


from ludo.pages.models import Page


UserInDTO = dto_factory("UserInDTO", User, exclude=["id", "pages"])
UserOutDTO = dto_factory("UserOutDTO", User, exclude=["password", "pages"])


# Create Crypt Context
crypt_context = CryptContext(schemes=["bcrypt"])


async def retrieve_user(token: Token, connection: ASGIConnection) -> UserOutDTO:
    user_dict = await connection.cache.get(token.sub)
    if user_dict is not None:
        return UserOutDTO(**user_dict)


jwt_cookie_auth = JWTCookieAuth[User](
    retrieve_user_handler=retrieve_user,
    token_secret="abcd123",
    exclude=["/login", "/register"],
)


@post("/register")
async def register_user_handler(
    request: Request[Any, Any], data: UserInDTO, session: AsyncSession
) -> Response[UserOutDTO]:
    # Check to see if user is already registered.
    result = await session.scalars(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    )

    if result.one_or_none() is not None:
        raise NotAuthorizedException(detail="Username or email is already registered")

    hashed_password = crypt_context.hash(data.password)

    db_user = User(**data.dict(exclude={"password"}), password=hashed_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    user_out = UserOutDTO.from_model_instance(db_user)
    await request.cache.set(user_out.username, user_out.dict())
    return jwt_cookie_auth.login(identifier=user_out.username, response_body=user_out)


@post("/login")
async def login_handler(
    request: Request[Any, Any], data: UserInDTO, session: AsyncSession
) -> Response[UserOutDTO]:
    user = await _verify_user(data, session)

    user_out = UserOutDTO.from_model_instance(user)
    await request.cache.set(user_out.username, user_out.dict())
    return jwt_cookie_auth.login(identifier=user_out.username, response_body=user_out)


async def _verify_user(data: UserInDTO, session: AsyncSession) -> User:
    user = await session.scalar(
        select(User).where(
            (User.username == data.username) | (User.email == data.email)
        )
    )

    if user is None:
        raise NotAuthorizedException("Username or email not registered")

    if not crypt_context.verify(data.password, user.password):
        raise NotAuthorizedException("Username and password do not match")
    return user


# @put("/reset-password")
# async def reset_password_handler(
#     request: Request[Any, Any], session: AsyncSession, data: UserResetModel
# ) -> Response[UserOutDTO]:
async def current_active_user(
    request: Request[UserOutDTO, JWTCookieAuth], session: AsyncSession
) -> User:
    user = await session.scalar(
        select(User).where(
            (User.username == request.user.username)
            | (User.email == request.user.email)
        )
    )
    if user is None:
        raise NotAuthorizedException(detail="User not logged in")
    return user


@get("/user")
async def get_logged_in_user(user: User) -> UserOutDTO:
    return UserOutDTO.from_model_instance(user)


@post("/logout")
async def logout_handler(request: Request[Any, Any], user: User) -> Response[None]:
    await request.cache.delete(user.username)
    logout_cookie = Cookie(
        key=jwt_cookie_auth.key, path=jwt_cookie_auth.path, value="", expires=0
    )
    return Response(cookies=[logout_cookie])


auth_router = Router(
    path="/auth",
    route_handlers=[
        login_handler,
        register_user_handler,
        logout_handler,
        get_logged_in_user,
    ],
)
