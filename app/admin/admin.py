from app.admin.views.bookings import BookingsView
from app.admin.views.hotels import HotelsView
from app.admin.views.rooms import RoomsView
from app.admin.views.users import UsersView
from app.resources.postgres import engine
from fastapi import FastAPI
from sqladmin import Admin


def add_admin(app: FastAPI):
    admin = Admin(app=app, engine=engine)  # TODO: мб session_maker ?
    admin.add_view(UsersView)
    admin.add_view(HotelsView)
    admin.add_view(RoomsView)
    admin.add_view(BookingsView)
