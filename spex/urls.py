
from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)


router.register("miners", viewset=l_views.Miner)
router.register("list-miners", viewset=l_views.ListMiner)
router.register("orders", viewset=l_views.Order)


urlpatterns = router.urls
