import discord
from dotenv import load_dotenv
from os import environ
from mongoengine import *

load_dotenv()
token = environ["TOKEN"]

class Item(EmbeddedDocument):
    name = StringField(unique=True)
    price = IntField()

class ShopItem(Document):
    item = EmbeddedDocumentField(Item)
    quantity = IntField()

class Player(Document):
    userId = IntField()
    displayName = StringField()
    wallet = IntField()
    items = ListField(EmbeddedDocumentField(Item))