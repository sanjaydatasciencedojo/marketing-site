import logging
from decimal import Decimal

from bakery.views import BuildableDetailView
from bakery.views import BuildableListView
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils import timezone
from slumber.exceptions import HttpNotFoundError

from marketing_site.apps.core.views import CustomRequestMixin
from marketing_site.apps.edx.utils import discovery_api_client, parse_datetime

logger = logging.getLogger(__name__)


class CourseViewMixin:
    COURSE_RUN_DATETIME_FIELDS = ('enrollment_start', 'enrollment_end', 'start', 'end')

    def get_queryset(self):
        offset = 0
        limit = 100

        while offset is not None and offset >= 0:
            response = discovery_api_client().courses().get(exclude_utm=1, offset=offset, limit=limit)
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

    def process_course_run_result(self, course_run):
        for field in self.COURSE_RUN_DATETIME_FIELDS:
            course_run[field] = parse_datetime(course_run.get(field))

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
            response = discovery_api_client().courses(course_id).get()
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
