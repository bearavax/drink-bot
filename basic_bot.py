import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta

description = '''A drinking game bot with various commands and effects.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

points = {}
hangovers = {}
blackouts = {}

def slur_text(text):
    return ''.join(random.choice((str.upper, str.lower))(c) for c in text)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def drink(ctx, choice: str):
    """Drink a choice and gain points."""
    user = ctx.author
    if user in hangovers and hangovers[user] > datetime.now():
        await ctx.send(f"{user.mention}, you're still hungover!")
        return
    if user in blackouts and blackouts[user] > datetime.now():
        await ctx.send(f"{user.mention}, you're still blacked out!")
        return

    points[user] = points.get(user, 0) + 1
    await ctx.send(f"{user.mention} drank {choice} and now has {points[user]} points!")

    if random.random() < 0.12:
        hangovers[user] = datetime.now() + timedelta(hours=6)
        await ctx.send(f"{user.mention} is wasted and will have a hangover for 6 hours!")
    elif random.random() < 0.06:
        blackouts[user] = datetime.now() + timedelta(hours=6)
        await ctx.send(f"{user.mention} blacked out and is muted for 6 hours!")
        await ctx.guild.mute(user, reason="Blacked out from drinking")

@bot.command()
async def buy_round(ctx):
    """Buy a round for everyone."""
    for member in ctx.guild.members:
        if not member.bot:
            points[member] = points.get(member, 0) + 1
    await ctx.send("A round for everyone! Everyone gains 1 point.")

@bot.command()
async def give(ctx, member: discord.Member, drink: str):
    """Give a drink to another member."""
    points[member] = points.get(member, 0) + 1
    await ctx.send(f"{ctx.author.mention} gave {member.mention} a {drink}. {member.mention} now has {points[member]} points!")

@bot.command()
async def cheers(ctx):
    """Drink together, first to finish gets wagered points."""
    await ctx.send("Cheers! First to finish gets the wagered points!")
    # Implement minigame logic here

@bot.command()
async def beer_me(ctx):
    """Get a beer or lose all your leaderboard points."""
    user = ctx.author
    if random.random() < 0.5:
        points[user] = points.get(user, 0) + 1
        await ctx.send(f"{user.mention} got a beer and now has {points[user]} points!")
    else:
        points[user] = 0
        await ctx.send(f"{user.mention} lost all their points!")

@tasks.loop(minutes=1)
async def check_hangovers():
    now = datetime.now()
    for user, end_time in list(hangovers.items()):
        if end_time <= now:
            del hangovers[user]
            await user.send("Your hangover is over!")

@tasks.loop(minutes=1)
async def check_blackouts():
    now = datetime.now()
    for user, end_time in list(blackouts.items()):
        if end_time <= now:
            del blackouts[user]
            await user.send("Your blackout is over!")
            await ctx.guild.unmute(user, reason="Blackout over")

check_hangovers.start()
check_blackouts.start()

bot.run('YOUR_TOKEN_HERE')