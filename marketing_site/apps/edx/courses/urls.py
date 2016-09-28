from django.conf.urls import url

from marketing_site.apps.edx.courses.constants import COURSE_ID_REGEX
from marketing_site.apps.edx.courses.views import CourseListView, CourseDetailView

urlpatterns = [
    url(r'^$', CourseListView.as_view(), name='list'),
    url(r'^(?P<pk>{})/$'.format(COURSE_ID_REGEX), CourseDetailView.as_view(), name='detail'),
]
