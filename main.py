import discord
from dotenv import load_dotenv
from mongoengine import *

import os
load_dotenv()
token = os.environ["TOKEN"]
print(token)

connect('economy')

class Item(Document):
    name = StringField(unique=True)
    price = IntField()

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

@bot.slash_command(guild_ids=[os.environ["GUILD_ID"]])
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
@bot.slash_command(guild_ids=[os.environ["GUILD_ID"]])
async def shop(ctx: discord.ApplicationContext):
    options = []
    for item in Item.objects:
        option = discord.SelectOption(label=item.name, description=item.price)
        options.append(option)
    menu = Select(placeholder="Select an item for purchase", options=options)
    async def on_select(interaction: discord.Interaction):
        await ctx.interaction.delete_original_message()
        # we only have 1 value
        itemName = menu.values[0]
        itemPrice = Item.objects.get(name=itemName).price
        embed = discord.Embed(title="Confirmation",
        description=f"Are you sure you want to purchase {itemName} for {itemPrice}")
        cancelButton = Button(style=discord.ButtonStyle.secondary, label="Cancel")
        confirmButton = Button(style=discord.ButtonStyle.success, label="Purchase")

        async def on_cancel(interactione: discord.Interaction):
            await interaction.response.defer(ephemeral=False)
            await interaction.delete_original_message()

        async def on_confirm(interactionne: discord.Interaction):
            try:
                player = Player.objects.get(userId=interactionne.user.id)
            except DoesNotExist:
                player = Player(userId=interactionne.user.id, displayName=interactionne.user.display_name, wallet=0, items=[])
                player.save()
            if Item.objects.get(name=itemName) in player.items:
                # the double underscore is like items.name
                await interactionne.response.send_message(f"You already own {itemName}")
                await interaction.delete_original_message()
            else:
                if player.wallet < itemPrice:
                    await interactionne.response.send_message(f"You don't have enough money to buy {itemName}")
                    await interaction.delete_original_message()
                    return
                player.wallet -= itemPrice
                player.items.append(Item.objects.get(name=itemName))
                player.save()
                await interactionne.response.send_message(f"You purchased {itemName} for {itemPrice}")
                await interaction.delete_original_message()
        confirmButton.callback = on_confirm
        cancelButton.callback = on_cancel
        view2 = View()
        view2.add_item(cancelButton)
        view2.add_item(confirmButton)
        await interaction.response.send_message(embed=embed, view=view2)
    menu.callback = on_select
    view = View()
    view.add_item(menu)
    await ctx.respond(view=view)

@bot.slash_command(guild_ids=[os.environ["GUILD_ID"]])
async def sparechange(ctx: discord.ApplicationContext, amount: int = None):
    try:
        player = Player.objects.get(userId=ctx.author.id)
    except DoesNotExist:
        player = Player(userId=ctx.author.id, displayName=ctx.author.name, wallet=0, items=[])
        player.save()
    # if they didn't pass in an amount, the condition will fail and it'll give 10k
    player.wallet += amount or 10000
    player.save()
    embed = discord.Embed(title="Money deposited", description=f"{amount or 10000} has been deposited into your wallet")
    await ctx.respond(embed=embed)

bot.run(token)
