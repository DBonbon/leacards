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
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from django.conf import settings


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

class CardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False, null=True, blank=True, label="image")
    card_tile = CharBlock(label="Card Title")
    card_subtile = CharBlock(label="Card Subtitle")
    POS = blocks.ChoiceBlock(
        label='Part of Speech',
        choices=SPEECH_TYPES,
    )
    language = blocks.CharBlock(max_length=10,
                                choices=settings.LANGUAGES,
                                default=settings.LANGUAGE_CODE)

    """class Meta:
        template = ''
        icon = 'list-ol'"""



""""
card group min max 4 elements

each group is 4 cards

card - image, name, translation


"""