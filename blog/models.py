from django.db import models
from wagtail.core.models import Orderable, Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import CharBlock,RichTextBlock
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from cms.blocks import TextAndButtonsBlock
from grapple.helpers import register_streamfield_block
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
            ("text_and_buttons", TextAndButtonsBlock()),
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


