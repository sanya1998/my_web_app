from app.cms.auth import AdminAuth
from app.cms.views.bookings import BookingsView
from app.cms.views.hotels import HotelsView
from app.cms.views.rooms import RoomsView
from app.cms.views.users import UsersView
from app.config.common import settings
from app.resources.postgres import PostgresManager
from fastapi import FastAPI
from sqladmin import Admin


async def add_cms(app: FastAPI, postgres_manager: PostgresManager):
    """
    Инициализация SQLAdmin с переданным менеджером БД
    """
    session_factory = postgres_manager.session_factory
    authentication_backend = AdminAuth(session_factory=session_factory, secret_key=settings.JWT_SECRET_KEY)
    cms = Admin(app=app, session_maker=session_factory, authentication_backend=authentication_backend)
    cms.add_view(UsersView)
    cms.add_view(HotelsView)
    cms.add_view(RoomsView)
    cms.add_view(BookingsView)
