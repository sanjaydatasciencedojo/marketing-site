import datetime
import logging
from decimal import Decimal

from bakery.views import BuildableDetailView
from bakery.views import BuildableListView
from dateutil import parser
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property
from edx_rest_api_client.client import EdxRestApiClient
from slumber.exceptions import HttpNotFoundError

from marketing_site.apps.core.views import CustomRequestMixin

logger = logging.getLogger(__name__)


class CatalogApiViewMixin:
    COURSE_RUN_DATETIME_FIELDS = ('enrollment_start', 'enrollment_end', 'start', 'end')

    @property
    def access_token(self):
        """ Returns an access token for this site's service user.

        The access token is retrieved using the current site's OAuth credentials and the client credentials grant.
        The token is cached for the lifetime of the token, as specified by the OAuth provider's response. The token
        type is JWT.

        Returns:
            str: JWT access token
        """
        key = 'courselistview_access_token'
        access_token = cache.get(key)

        if not access_token:
            access_token, expiration_datetime = EdxRestApiClient.get_oauth_access_token(
                '{}/access_token'.format(settings.SOCIAL_AUTH_EDX_OIDC_URL_ROOT),
                settings.SOCIAL_AUTH_EDX_OIDC_KEY,
                settings.SOCIAL_AUTH_EDX_OIDC_SECRET,
                token_type='jwt'
            )

            expires = (expiration_datetime - datetime.datetime.utcnow()).seconds
            cache.set(key, access_token, expires)

        return access_token

    @cached_property
    def catalog_api_client(self):
        return EdxRestApiClient(settings.CATALOG_API_URL, jwt=self.access_token)

    def parse_datetime(self, s):
        if s:
            return parser.parse(s)

        return None

    def process_course_run_result(self, course_run):
        for field in self.COURSE_RUN_DATETIME_FIELDS:
            course_run[field] = self.parse_datetime(course_run.get(field))

        end = course_run.get('end')
        course_run['is_archived'] = end and end < timezone.now()
        course_run['is_self_paced'] = course_run['pacing_type'] == 'self_paced'
        course_run['pricing'] = self._get_course_run_pricing(course_run)
        return course_run

    def process_course_result(self, course):
        # Fix the owner field name
        course['authoring_organizations'] = course.pop('owners')

        # Remove course runs with no start date as they will break sorting in the template
        course['course_runs'] = [
            self.process_course_run_result(course_run) for course_run in course['course_runs'] if
            course_run['start']]
        return course

    def _get_course_run_pricing(self, course_run):
        pricing = {}

        for seat in course_run['seats']:
            # TODO Handle credit seats
            price = Decimal(seat['price']).normalize()
            pricing[seat['type']] = {
                'price': 0 if price == Decimal(0) else price,
                'currency': '$'  # seat['currency'],
            }

        return pricing


class CourseViewMixin(CatalogApiViewMixin):
    def get_queryset(self):
        offset = 0
        limit = 100

        while offset is not None and offset >= 0:
            response = self.catalog_api_client.courses().get(exclude_utm=1, offset=offset, limit=limit)
            results = [self.process_course_result(course) for course in response['results']]
            return results

            # NOTE (CCB): Un-comment if we need to list all courses
            # logger.info('Retrieved %d courses...', len(results))
            #
            # if response['next']:
            #     offset += limit
            # else:
            #     offset = None
            #
            # for body in results:
            #     yield body


class CourseListView(CustomRequestMixin, CourseViewMixin, BuildableListView):
    build_path = 'courses/index.html'
    context_object_name = 'courses'
    template_name = 'courses/course_list.html'

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        courses = [course for course in context['courses'] if course.get('course_runs')]
        context[self.context_object_name] = courses
        return context


class CourseDetailView(CustomRequestMixin, CourseViewMixin, BuildableDetailView):
    context_object_name = 'course'
    template_name = 'courses/course_detail.html'

    def get_object(self, queryset=None):
        # This shortcut for django-bakery allows us to avoid making API calls
        # for every rendered course.
        if 'obj' in self.kwargs:
            return self.kwargs['obj']

        course_id = self.kwargs[self.pk_url_kwarg]

        try:
            response = self.catalog_api_client.courses(course_id).get()
            return self.process_course_result(response)
        except HttpNotFoundError:
            raise Http404

    # NOTE: These are only used by django-bakery
    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]  # pylint: disable=expression-not-assigned

    def get_url(self, obj):
        return reverse('courses:detail', kwargs={'pk': obj['key']})

    def set_kwargs(self, obj):
        super(CourseDetailView, self).set_kwargs(obj)
        self.kwargs.update({
            'pk': obj['key'],
            'obj': obj,
        })
