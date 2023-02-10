from starlite import Starlite, CacheConfig, CORSConfig, Provide


from .utils import PicklingCacheBackend
from .db import db_on_startup, sqlalchemy_plugin
from .auth import auth_router, jwt_cookie_auth, current_active_user
from .pages.routes import PagesController


app = Starlite(
    debug=True,
    route_handlers=[auth_router, PagesController],
    on_startup=[db_on_startup],
    on_app_init=[jwt_cookie_auth.on_app_init],
    plugins=[sqlalchemy_plugin],
    dependencies={"user": Provide(current_active_user)},
    cors_config=CORSConfig(
        allow_credentials=True, allow_origins=["http://localhost:5173"]
    ),
    cache_config=CacheConfig(
        backend=PicklingCacheBackend("persist.pickle"), expiration=60 * 60 * 24
    ),
)
