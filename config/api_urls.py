from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from jobs.api import JobViewSet
from workers.api import WorkerViewSet

router = DefaultRouter()
router.register('workers', WorkerViewSet, basename='api-worker')
router.register('jobs', JobViewSet, basename='api-job')

urlpatterns = [
    path('token/', obtain_auth_token, name='api-token'),
    path('', include(router.urls)),
]