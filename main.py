import discord
from dotenv import load_dotenv
from os import environ
from mongoengine import *

from os import environ
load_dotenv()
token = environ["TOKEN"]
print(token)

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

from discord.ui import Button, Select, View
@bot.slash_command()
async def shop(ctx):
    options = []
    for item in ShopItem.objects:
        option = discord.SelectOption(label=item.item.name, description=item.item.price)
        options.append(option)
    menu = Select(placeholder="Select an item for purchase", options=options)
    async def on_select(interaction: discord.Interaction):
        # we only have 1 value
        itemName = menu.values[0]
        itemPrice = Item.objects.get(name=itemName).price
        embed = discord.Embed(title="Confirmation",
        description=f"Are you sure you want to purchase {itemName} for {itemPrice}")
        cancelButton = Button(style=discord.ButtonStyle.secondary, label="Cancel")
        confirmButton = Button(style=discord.ButtonStyle.success, label="Purchase")

        async def on_confirm(interaction: discord.Interaction):
            player = Player.objects.get(userId=interaction.user.id)
            player.wallet -= itemPrice
            player.items.append(Item.objects.get(name=itemName))
            player.save()
            await interaction.response.send_message(f"You purchased {itemName} for {itemPrice}")
        confirmButton.callback = on_confirm
        view2 = View()
        view2.add_item(cancelButton)
        view2.add_item(confirmButton)
        await interaction.response.send_message(embed=embed, view=view2)
    menu.callback = on_select
    view = View()
    view.add_item(menu)
    await ctx.respond(view=view)

bot.run(token)