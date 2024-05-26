from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logoutUser, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('upload/', views.upload, name='upload'),
    path('profile/', views.profile, name='profile'),
    path('profile/overview', views.overview, name='overview'),
    path('profile/alert', views.alert, name='alert'),
    path('profile/reproduction', views.reproduction, name='reproduction'),
    path('model/', views.model, name='model'),
    path('download/', views.download, name='download'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('changepassword/', views.changepassword, name='changepassword'),
]
