
from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)


router.register("miners", viewset=l_views.Miner)
router.register("list-miners", viewset=l_views.ListMiner)
router.register("messages", viewset=l_views.Message, basename="message")
router.register("orders", viewset=l_views.Order)
router.register("comments", viewset=l_views.Comment)


urlpatterns = router.urls
