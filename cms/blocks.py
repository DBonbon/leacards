from django import forms
from wagtail.core.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    DateTimeBlock,
    FieldBlock,
    IntegerBlock,
    ListBlock,
    PageChooserBlock,
    RawHTMLBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    StructValue,
    TextBlock,
    URLBlock,
)
from grapple.helpers import register_streamfield_block
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from django.conf import settings
#grapple codes:
from typing import Any, Dict, Optional
import graphene
from graphene_django import DjangoObjectType
from grapple.models import (
    GraphQLBoolean,
    GraphQLCollection,
    GraphQLEmbed,
    GraphQLField,
    GraphQLFloat,
    GraphQLForeignKey,
    GraphQLImage,
    GraphQLInt,
    GraphQLRichText,
    GraphQLStreamfield,
    GraphQLString,
)


SPEECH_TYPES = (
        ('verb', 'Verb'),
        ('noun', 'Noun'),
        ('adjective', 'Adjective'),
        ('adverb', 'Adverb'),
        ('pronoun', 'Pronoun'),
        ('preposition', 'Preposition'),
        ('conjunction', 'Conjunction'),
        ('interjection', 'Interjection'),
        ('determiner', 'Determiner'),
    )

@register_streamfield_block
class CardBlock(blocks.StructBlock):
    """Basic game block that contains exactly 4 cards"""
    image = ImageChooserBlock(required=False, null=True, blank=True, label="image")
    card_title = CharBlock(label="Card Title")
    card_subtitle = CharBlock(label="Card Subtitle", required=False, help_text="another text string can be used as hint, En translation, etc'")

    graphql_fields = [
        GraphQLString("card_title"),
        GraphQLString("card_subtitle"),
        GraphQLImage("image"),
    ]

    """class Meta:
        template = 'cms/card_block.html'
        icon = 'list-ol'"""

@register_streamfield_block
class GameBlock(blocks.StreamBlock):
    """Game unit which contains a un/limited niumber of 4 card units."""
    series = CardBlock(required=False, null=True, blank=True, label="image")
    title = CharBlock(label="Game Title")
    intro = CharBlock(label="Card Subtitle", required=False, help_text="describe the goal and/or add BG information, optional")

    graphql_fields = [
        GraphQLString("title"),
        GraphQLImage("intro"),
        GraphQLStreamfield("series"),
    ]

class SomeStructBlock(blocks.StructBlock):
    text = blocks.CharBlock()

    graphql_fields = [
        GraphQLField(
            field_name="some_name",
            field_type=graphene.String,
            source="some_method",
        )
    ]

    def some_method(self, values: Dict[str, Any] = None) -> Optional[str]:
        return values.get("text") if values else None


@register_streamfield_block
class ButtonBlock(blocks.StructBlock):
    button_text = blocks.CharBlock(required=True, max_length=50, label="Text")
    button_link = blocks.CharBlock(required=True, max_length=255, label="Link")

    graphql_fields = [GraphQLString("button_text"), GraphQLString("button_link")]


@register_streamfield_block
class TextAndButtonsBlock(blocks.StructBlock):
    text = blocks.TextBlock()
    buttons = blocks.ListBlock(ButtonBlock())
    mainbutton = ButtonBlock()

    graphql_fields = [
        GraphQLString("text"),
        GraphQLImage("image"),
        GraphQLStreamfield("buttons"),
        GraphQLStreamfield(
            "mainbutton", is_list=False
        ),  # this is a direct StructBlock, not a list of sub-blocks
    ]

""""
card group min max 4 elements

each group is 4 cards

card - image, name, translation


"""