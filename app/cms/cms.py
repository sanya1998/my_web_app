from app.cms.auth import authentication_backend
from app.cms.views.bookings import BookingsView
from app.cms.views.hotels import HotelsView
from app.cms.views.rooms import RoomsView
from app.cms.views.users import UsersView
from app.resources.postgres import engine
from fastapi import FastAPI
from sqladmin import Admin


def add_cms(app: FastAPI):
    cms = Admin(app=app, engine=engine, authentication_backend=authentication_backend)  # TODO: мб session_maker ?
    cms.add_view(UsersView)
    cms.add_view(HotelsView)
    cms.add_view(RoomsView)
    cms.add_view(BookingsView)
