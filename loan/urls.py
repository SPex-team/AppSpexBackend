

from rest_framework import routers

from . import views as l_views


router = routers.DefaultRouter(trailing_slash=False)


router.register("miners", viewset=l_views.Miner)
router.register("loans", viewset=l_views.Loan)


urlpatterns = router.urls
