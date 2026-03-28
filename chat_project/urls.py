from django.contrib import admin
from django.urls import path

from chat_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_page, name='chat_page'),
    path('api/chat/', views.chat_api, name='chat_api'),
]
