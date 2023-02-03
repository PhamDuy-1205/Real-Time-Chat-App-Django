from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('create-room/', views.createRoom, name = 'create-room'),
    path('login/', views.login_user, name = 'login'),
    path('register/', views.register_user, name = 'register'),
    path('logout/', views.logout_user, name = 'logout'),
    path('room/<int:room_id>', views.room, name = 'room'),
    path('update-room/<str:room_id>', views.updateroom, name = 'update-room'),
    path('delete-room/<str:room_id>', views.deleteroom, name = 'delete-room'),
    path('delete-message/<str:message_id>', views.deleteMessage, name = 'delete-message'),
    path('profile/<str:user_id>', views.userProfile, name = 'profile'),
    path('update-user', views.updateUser, name = 'update-user'),
    path('topics', views.topicsPage, name = 'topics'),
    path('activity', views.activityPage, name = 'activity'),

]
