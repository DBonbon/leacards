from django.db import models
import datetime
from allauth.account.forms import LoginForm
from django.shortcuts import render
from django.db import models
from django.http import Http404
from wagtail import blocks
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel

from wagtail.core.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet
from wagtail.search import index

from wagtail.core.models import Orderable, Page
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import Tag as TaggitTag
from taggit.models import TaggedItemBase
from django.conf import settings
from .blocks import CardBlock, SPEECH_TYPES
#from grapple.types import GraphQLString
from grapple.models import (
        GraphQLRichText,
        GraphQLString,
        GraphQLStreamfield,
    )


"""
1. HomePage - 
    a. Display most popular/promoted games, teachers
    b. Site presentation
    c. Aboput, contact, etc' (subpages or separate)

2. Teachers - Teachers index page can be public or not
Teacher page

"""
class GamePage(RoutablePageMixin, Page):
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
    intro = RichTextField(blank=True, help_text="Describe the cars group's linguistic theme")
    #Part of speech could be streanmed with snippetsg? to explore
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


    #Allow IndexPage to Calling carousel's 1st image
    def main_image(self):
        for block in self.content:
            for column in block.value.values():
                for carousel in column:
                    if carousel.block_type == 'carousel':
                        for img in carousel.value:
                            if img.block_type == 'image':
                                return img.value['image']




class GameIndexPage(RoutablePageMixin, Page):
    intro = RichTextField(blank=True)

    # Specifies that only ArticlePage objects can live under this index page
    #subpage_types = ['ArticlePage', 'ArticleIndexPage']

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full'),
    ]


    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['posts'] = GamePage.objects.live().public()
        context['blog_page'] = self
        context['categories']=GameCategory.objects.all()
        return context

    def get_posts(self):
        return GamePage.objects.descendant_of(self).live().order_by("-post_date")


    @route(r'^tag/(?P<tag>[-\w]+)/$')
    def post_by_tag(self, request, tag, *args, **kwargs):
        self.filter_type = 'tag'
        self.filter_term = tag
        context = self.get_context(request)
        context["posts"]=self.get_posts().filter(tags__slug=tag)
        return render(request, 'cms/game_index_page.html', context)

    @route(r'^category/(?P<category>[-\w]+)/$')
    def post_by_category(self, request, category, *args, **kwargs):
        self.filter_type = 'category'
        self.filter_term = category
        context = self.get_context(request)
        context["posts"]=self.get_posts().filter(categories__blog_category__slug=category)
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


#Categories
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

#Tags
class PostPageTag(TaggedItemBase):
    content_object = ParentalKey("GamePage", related_name="post_tags")

@register_snippet
class Tag(TaggitTag):
    class Meta:
        proxy = True

