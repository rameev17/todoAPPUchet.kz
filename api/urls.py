from django.urls import path
from api import views
from api.views import ChangePasswordView
from knox import views as knox_views
from .views import LoginAPI
from django.urls import path

urlpatterns = [
    path('', views.apiOverview, name="api-overview"),
    path('todo/', views.taskList, name="todo List"),
    path('todo/<str:pk>/', views.taskDetail, name="todo Detail"),
    path('todo-create/', views.taskCreate, name="todo Create"),
    path('todo-delete/<str:pk>/', views.taskDelete, name="todo Delete"),
    path('todo-update/<str:pk>/', views.taskUpdate, name="todo Update"),
    path('todo/<str:pk>/execute/', views.taskMakeDone, name="todo Is DONE"),
    path('todo/<str:pk>/notexecute/', views.taskMakeNotDone, name="todo Is Not DONE"),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
]