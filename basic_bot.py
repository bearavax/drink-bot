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
    check_hangovers.start()
    check_blackouts.start()

@bot.command()
async def drink(ctx, choice: str):
    """Drink a choice and gain points."""
    print(f"Command !drink invoked by {ctx.author} with choice {choice}")
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
    print(f"Command !buy round invoked by {ctx.author}")
    for member in ctx.guild.members:
        if not member.bot:
            points[member] = points.get(member, 0) + 1
    await ctx.send("A round for everyone! Everyone gains 1 point.")

@bot.command()
async def give(ctx, member: discord.Member, drink: str):
    """Give a drink to another member."""
    print(f"Command !give invoked by {ctx.author} to give {drink} to {member}")
    points[member] = points.get(member, 0) + 1
    await ctx.send(f"{ctx.author.mention} gave {member.mention} a {drink}. {member.mention} now has {points[member]} points!")

@bot.command()
async def cheers(ctx):
    """Drink together, first to finish gets wagered points."""
    print(f"Command !cheers invoked by {ctx.author}")
    await ctx.send("Cheers! First to finish gets the wagered points!")
    # Implement minigame logic here

@bot.command()
async def beer_me(ctx):
    """Get a beer or lose all your leaderboard points."""
    print(f"Command !beer me invoked by {ctx.author}")
    user = ctx.author
    if random.random() < 0.5:
        points[user] = points.get(user, 0) + 1
        await ctx.send(f"{user.mention} got a beer and now has {points[user]} points!")
    else:
        points[user] = 0
        await ctx.send(f"{user.mention} lost all their points!")

@bot.command()
async def leaderboard(ctx):
    """Show the top 10 drink scores and the player's rank."""
    sorted_points = sorted(points.items(), key=lambda item: item[1], reverse=True)
    top_10 = sorted_points[:10]
    leaderboard_message = "🏆 **Leaderboard** 🏆\n"
    for rank, (user, score) in enumerate(top_10, start=1):
        leaderboard_message += f"{rank}. {user.display_name}: {score} points\n"

    user_rank = next((rank for rank, (user, _) in enumerate(sorted_points, start=1) if user == ctx.author), None)
    total_players = len(sorted_points)
    if user_rank:
        leaderboard_message += f"\nYou are ranked {user_rank} out of {total_players} players."

    await ctx.send(leaderboard_message)

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

bot.run('')