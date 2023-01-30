from django.db import models
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import CharBlock,RichTextBlock
from grapple.models import (
    GraphQLRichText,
    GraphQLString,
    GraphQLStreamfield,
)


class BlogPage(Page):
    author = models.CharField(max_length=255)
    date = models.DateField("Post date")
    summary = RichTextField()
    body = StreamField(
        [
            ("heading", CharBlock(classname="full title")),
            ("paragraph", RichTextBlock()),
            ("image", ImageChooserBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("summary"),
        FieldPanel("body"),
    ]

    # Note these fields below:
    graphql_fields = [
        GraphQLString("heading"),
        GraphQLString("date"),
        GraphQLString("author"),
        GraphQLRichText("summary"),
        GraphQLStreamfield("body"),
    ]