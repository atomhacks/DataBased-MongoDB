import discord
from dotenv import load_dotenv
from os import environ
from mongoengine import *

from os import environ
load_dotenv()
token = environ["TOKEN"]
print(token) # will print mytokenhere

connect('economy')

class Item(Document):
    name = StringField(unique=True)
    price = IntField()

class ShopItem(Document):
    item = ReferenceField(Item)
    quantity = IntField()

class Player(Document):
    userId = IntField()
    displayName = StringField()
    wallet = IntField()
    items = ListField(ReferenceField(Item))

# chanel_bag = Item(name="Chanel Blue", price=1000000)
# shop_item = ShopItem(item=chanel_bag, quantity=10)
# player = Player(userId=196692594443550720, displayName="frykher", wallet=20, items=[chanel_bag])
# chanel_bag.save()
# player.save()
# shop_item.save()

# frykher = Player.objects.get(userId=196692594443550720)
# new_item = Item(name="calculator", price=1)
# frykher.items.append(new_item)
# new_item.save()
# frykher.save()

bot = discord.Bot()

@bot.slash_command()
async def hello(ctx, name: str = None):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

@bot.slash_command(guild_ids=[804100748275220530])
async def inventory(ctx):
    try:
        player = Player.objects.get(userId=ctx.author.id)
    except DoesNotExist:
        player = Player(userId=ctx.author.id, displayName=ctx.author.name, wallet=0, items=[])
        player.save()
    items = player.items
    embed = discord.Embed(title="Inventory", description=f"{player.displayName}'s inventory")
    if not items:
        embed.set_image(url="https://i.imgflip.com/68g2gz.jpg")
    else:
        for item in items:
            embed.add_field(name=item.name, value=f'Worth: {item.price}', inline=True)
    await ctx.respond(embed=embed)

@bot.slash_command()
async def shop(ctx):
    pass

bot.run(token)