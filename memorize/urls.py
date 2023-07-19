
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("define/<str:word>", views.get_word_info, name="get_word_info"),
    path("users/<str:username>", views.favor_list, name="favor_list"),
    path("users/<str:username>/<str:word>", views.word_in_favor_list, name="word_in_favor_list"),
    path("users", views.user_list, name="user_list"),
    path("upload", views.upload_view, name="upload"),
    path("handle_upload", views.handle_upload, name="handle_upload"),
]
