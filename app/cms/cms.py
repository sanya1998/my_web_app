from app.cms.auth import authentication_backend
from app.cms.views.bookings import BookingsView
from app.cms.views.hotels import HotelsView
from app.cms.views.rooms import RoomsView
from app.cms.views.users import UsersView
from app.resources.postgres import async_session
from fastapi import FastAPI
from sqladmin import Admin


def add_cms(app: FastAPI):
    cms = Admin(app=app, session_maker=async_session, authentication_backend=authentication_backend)
    cms.add_view(UsersView)
    cms.add_view(HotelsView)
    cms.add_view(RoomsView)
    cms.add_view(BookingsView)
