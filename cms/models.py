from wagtail import blocks
from .blocks import CardBlock, SPEECH_TYPES
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.core.models import Orderable, Page, TranslatableMixin, Site
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel
from wagtail.admin.panels import PageChooserPanel

from wagtail.core.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from taggit.models import Tag as TaggitTag
from taggit.models import TaggedItemBase
from django.conf import settings
from django_extensions.db.fields import AutoSlugField
from django.db import models
import datetime
from allauth.account.forms import LoginForm
from django.shortcuts import render
from django.db import models
from django.http import Http404
# from grapple.types import GraphQLString
from grapple.models import (
    GraphQLRichText,
    GraphQLString,
    GraphQLStreamfield,
)
# contact forms
from wagtail.contrib.forms.models import (
    AbstractEmailForm,
    AbstractFormField
)
from wagtailcaptcha.models import WagtailCaptchaEmailForm
# testing group users
from django.contrib.auth.admin import UserAdmin
from userauth.models import CustomUser
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

"""
self.admins_group = Group.objects.get(name="Administrators")
        self.editors_group = Group.objects.get(name="Editors")
event_moderators_group = Group.objects.get(name='Event moderators')
users = User.objects.filter(groups__name='Staff')

def get_users(self):
        return Group.objects.get(name="Administrators")

def get_users2(self):
        return User.objects.filter(groups__name='Staff')
        """
##end testing users

"""
1. HomePage -
    a. Display most popular/promoted games, teachers
    b. Site presentation
    c. Aboput, contact, etc' (subpages or separate)

2. Teachers - Teachers index page can be public or not
Teacher page

"""


class HomePage(Page):
    max_count = 1

    # this is to pass the user details to the about section
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['home_page'] = self
        context['users'] = CustomUser.objects.filter(groups__name="Editors")
        context['menuitems'] = self.get_descendants(inclusive=True).live().in_menu()
        return context

    def get_sitemap_urls(self, request):
        sitemap = super().get_sitemap_urls(request)

        for locale_home in self.get_siblings(inclusive=False).live():
            for entry in locale_home.get_sitemap_urls(request):
                sitemap.append(entry)
            for child_page in locale_home.get_descendants().live():
                for entry in child_page.get_sitemap_urls(request):
                    sitemap.append(entry)
        return sitemap


"""
class CreatorIndexPage(Page):
    parent_page_types = ['cms.HomePage']
    parent_page_types = ['cms.GamePage']
    pass
"""


class GamePage(RoutablePageMixin, Page):
    template = 'cms/game_page.html'
    parent_page_types = ['cms.GamesIndexPage']
    subpage_types = ['cms.CardsPage']
    intro = RichTextField(blank=True, help_text="Describe the game theme")
    POS = models.CharField(
        max_length=20, choices=SPEECH_TYPES,
    )
    tags = ClusterTaggableManager(through="cms.PostPageTag", blank=True)
    min_recommended_age = models.IntegerField(max_length=2, null=True, blank=True)
    max_recommended_age = models.IntegerField(max_length=2, null=True, blank=True)
    language = models.CharField(max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)
    post_date = models.DateTimeField(
        verbose_name="Game date", default=datetime.datetime.today)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('POS'),
        MultiFieldPanel([
            FieldPanel('min_recommended_age'),
            FieldPanel('max_recommended_age'),
        ], heading=("Age Recommendation")),
        FieldPanel('language', help_text='original language of the game'),
        InlinePanel("categories", label="Linguistic difficulty/level"),
        FieldPanel("tags"),
    ]

    graphql_fields = [
        GraphQLString("intro"),
        GraphQLString("POS"),
        GraphQLString("tags"),
        GraphQLString("post_datepyt"),
        GraphQLRichText("categories"),
        GraphQLStreamfield("intro"),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("post_date"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('POS'),
    ]

    # Game-author is passed through the USERAuth so no need to FK field


class CardsPage(Page):
    parent_page_types = ['cms.GamePage']
    subpage_types = []
    template = 'cms/cards_page.html'
    intro = RichTextField(blank=True, help_text="Describe the cars group's linguistic theme")
    # Part of speech could be streanmed with snippetsg? to explore
    cards = StreamField([
        ('card', CardBlock(form_classname="card")),
    ], max_num=4, min_num=4, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('cards'),
    ]

    graphql_fields = [
        GraphQLString("cards"),
        GraphQLString("Intro"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('title'),
        index.SearchField('cards'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['game_page'] = self.get_parent().specific
        return context

    def get_absolute_url(self):
        return self.get_url()

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, 'cms/article_page.html')
        response.context_data['login_form'] = LoginForm()
        return response

    # Allow IndexPage to Calling carousel's 1st image
    def main_image(self):
        for block in self.content:
            for column in block.value.values():
                for carousel in column:
                    if carousel.block_type == 'carousel':
                        for img in carousel.value:
                            if img.block_type == 'image':
                                return img.value['image']


class GamesIndexPage(RoutablePageMixin, Page):
    parent_page_types = ['cms.HomePage']
    subpage_types = ['cms.GamePage']

    intro = RichTextField(blank=True)

    # Specifies that only ArticlePage objects can live under this index page
    # subpage_types = ['ArticlePage', 'ArticleIndexPage']

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['posts'] = GamePage.objects.live().public()
        context['blog_page'] = self
        context['categories'] = GameCategory.objects.all()
        return context

    def get_posts(self):
        return GamePage.objects.descendant_of(self).live().order_by("-post_date")

    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.filter_type = 'tag'
        self.filter_term = tag
        context = self.get_context(request)
        context["posts"] = self.get_posts().filter(tags__slug=tag)
        return render(request, 'cms/game_index_page.html', context)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.filter_type = 'category'
        self.filter_term = category
        context = self.get_context(request)
        context["posts"] = self.get_posts().filter(categories__blog_category__slug=category)
        return render(request, 'cms/game_index_page.html', context)

    @route(r"^(\d{4})/(\d{2})/(\d{2})/(.+)/$")
    def post_by_date_slug(self, request, year, month, day, slug, *args, **kwargs):
        post_page = self.get_posts().filter(slug=slug).first()
        if not post_page:
            raise Http404
        # here we render another page, so we call the serve method of the page instance
        return post_page.serve(request)

    @route(r'^$')
    def post_list(self, request, *args, **kwargs):
        self.posts = self.get_posts()
        return self.render(request)


# Categories
class PostPageGameCategory(models.Model):
    page = ParentalKey(
        "cms.GamePage", on_delete=models.CASCADE, related_name="categories"
    )
    game_category = models.ForeignKey(
        "cms.GameCategory", on_delete=models.CASCADE, related_name="post_pages"
    )

    panels = [
        FieldPanel("game_category"),
    ]

    class Meta:
        unique_together = ("page", "game_category")


@register_snippet
class GameCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=80)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


# Tags
class PostPageTag(TaggedItemBase):
    content_object = ParentalKey("GamePage", related_name="post_tags")


@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True


# MENUS
class MenuItem(Orderable):
    link_title = models.CharField(
        blank=True,
        null=True,
        max_length=50
    )
    link_url = models.CharField(
        max_length=500,
        blank=True
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)

    page = ParentalKey("Menu", related_name="menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        FieldPanel("open_in_new_tab"),
    ]

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title
        return 'Missing Title'

    @property
    def get_context(self, request):
        context = super(HomePage, self).get_context(request)
        # context['menuitems'] = homepage.get_children().live().in_menu()
        context['menuitems'] = request.site.root_page.get_descendants(inclusive=True).live().in_menu()


@register_snippet
class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)
    # slug = models.SlugField()

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Menu"),
        InlinePanel("menu_items", label="Menu Item")
    ]

    def __str__(self):
        return self.title


# Contact
class FormField(AbstractFormField):
    page = ParentalKey(
        'ContactPage',
        on_delete=models.CASCADE,
        related_name='form_fields',
    )


class ContactPage(WagtailCaptchaEmailForm):
    template = "cms/contact_page.html"
    # This is the default path.
    # If ignored, Wagtail adds _landing.html to your template name
    landing_page_template = "cms/contact_page_landing.html"
    parent_page_types = ['cms.HomePage']
    subpage_types = []

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),

        InlinePanel('form_fields', label='Form Fields'),
        FieldPanel('thank_you_text'),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel("subject"),
        ], heading="Email Settings"),
    ]

    """def get_context(self, request, *args, **kwargs):
        ""Adding HomePage to your page context.""
        context = super().get_context(request, *args, **kwargs)
        context["home_page"] = HomePage.objects.first()
        context["form_fields"] = self.form_fields.objects.all()
        context["form"] = self.form
        context["data_fields"] = [
            (field.clean_name, field.label)
            for field in self.get_form_fields()
        ]
        return context"""

    def get_form_fields(self):
        return self.form_fields.all()


# company logo
@register_snippet
class CompanyLogo(models.Model):
    name = models.CharField(max_length=250)
    logo = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )

    panels = [
        FieldPanel('name', classname='full'),
        FieldPanel('logo'),
    ]

    def __str__(self):
        return self.name


# Snipets to translated trempaltes with localitzed
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet
from wagtail_localize.fields import TranslatableField
from wagtail.models import Locale
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable


@register_snippet
class TemplateText(TranslatableMixin, ClusterableModel):
    template_set = models.CharField(
        max_length=50,
        verbose_name="Set Name",
        help_text=_("The set needs to be loaded in template tags then text references as {{set.tag}}")
    )

    translatable_fields = [
        TranslatableField('templatetext_items'),
    ]

    panels = [
        FieldPanel("template_set"),
        MultiFieldPanel(
            [
                InlinePanel("templatetext_items"),
            ],
            heading=_("Text Items"),
        ),
    ]

    def __str__(self):
        return self.template_set

    class Meta:
        verbose_name = _('Template Text')
        unique_together = ('translation_key', 'locale'), ('locale', 'template_set')

    def clean(self):
        def_lang = Locale.get_default()

        if self.locale == Locale.get_default():
            if TemplateText.objects.filter(template_set=self.template_set).filter(locale=self.locale_id).exclude(
                    pk=self.pk).count() > 0:
                raise ValidationError(_("This template set name is already in use. Please only use a unique name."))
        elif self.get_translations().count() == 0:
            raise ValidationError(_(f"Template sets can only be created in the default language ({def_lang}). \
                                      Please create the set in {def_lang} and use the translate option."))

    def delete(self):
        if self.locale == Locale.get_default():
            for trans in self.get_translations():
                trans.delete()
        super().delete()


class TemplateTextSetItem(TranslatableMixin, Orderable):
    set = ParentalKey(
        "TemplateText",
        related_name="templatetext_items",
        help_text=_("Template Set to which this item belongs."),
        verbose_name="Set Name",
    )
    template_tag = models.SlugField(
        max_length=50,
        help_text=_("Enter a tag without spaces, consisting of letters, numbers, underscores or hyphens."),
        verbose_name="Template Tag",
    )
    text = models.TextField(
        null=True,
        blank=True,
        help_text=_("The text to be inserted in the template.")
    )

    translatable_fields = [
        TranslatableField('text'),
    ]

    panels = [
        FieldPanel('template_tag'),
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.template_tag

    class Meta:
        unique_together = ('set', 'template_tag'), ('translation_key', 'locale')

