from wagtailbakery.views import WagtailBakeryView

from marketing_site.apps.core.views import CustomRequestMixin
from marketing_site.apps.edx.pages import models


class HomePageStatic(CustomRequestMixin, WagtailBakeryView):
    model = models.HomePage
