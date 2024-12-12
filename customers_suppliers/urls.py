from django.urls import include, path
from . import views
from rest_framework.routers import DefaultRouter


router=DefaultRouter()
router.register(r'custom_user', views.CustomUserViewSet)
router.register('customer', views.CustomerViewSet)
router.register('supplier', views.SupplierViewSet)


urlpatterns = [
    path('api/v1/', include(router.urls)),
]