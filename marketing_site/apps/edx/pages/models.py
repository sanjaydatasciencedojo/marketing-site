from modelcluster.fields import ParentalKey
from wagtail.wagtailadmin.edit_handlers import (FieldPanel, InlinePanel,
                                                MultiFieldPanel)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField


class HomePage(Page):
    bakery_views = ('marketing_site.apps.edx.pages.bakery_views.HomePageStatic',)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full')
    ]


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', related_name='form_fields')


class FormPage(AbstractEmailForm):
    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro', classname='full'),
        InlinePanel('form_fields', label='Form fields'),
        FieldPanel('thank_you_text', classname='full'),
        MultiFieldPanel([
            FieldPanel('to_address', classname='full'),
            FieldPanel('from_address', classname='full'),
            FieldPanel('subject', classname='full'),
        ], 'Email')
    ]
