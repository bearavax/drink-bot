import os
import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta
from keep_alive import keep_alive

description = '''A drinking game bot with various commands and effects.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', description=description, intents=intents)

points = {}
hangovers = {}
blackouts = {}

# Global check to ensure commands are only used in the #bar channel
def is_bar_channel(ctx):
    return ctx.channel.name == 'bar'

# Add the global check to the bot
bot.add_check(is_bar_channel)

def slur_text(text):
    return ''.join(random.choice((str.upper, str.lower))(c) for c in text)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    check_hangovers.start()
    check_blackouts.start()

from datetime import datetime, timedelta

# Dictionary to track the last drink time for each user
last_drink_time = {}

@bot.command()
async def drink(ctx, choice: str):
    """Drink a choice and gain points."""
    print(f"Command !drink invoked by {ctx.author} with choice {choice}")
    user = ctx.author
    now = datetime.now()

    if user in hangovers and hangovers[user] > now:
        await ctx.send(f"{user.mention}, you're still hungover!")
        return
    if user in blackouts and blackouts[user] > now:
        await ctx.send(f"{user.mention}, you're still blacked out!")
        return
    if user in last_drink_time and last_drink_time[user] > now - timedelta(minutes=2):
        await ctx.send("gulp gulp")
        return

    # Update the last drink time
    last_drink_time[user] = now

    points[user] = points.get(user, 0) + 1
    await ctx.send(f"{user.mention} drank {choice} and now has {points[user]} points!")

    # Calculate the chance of getting wasted
    chance_of_wasted = min(points[user] / 12, 1.0)
    if random.random() < chance_of_wasted:
        hangovers[user] = now + timedelta(hours=1)
        await ctx.send(f"{user.mention}, you're wasted and have a hangover!")

@bot.command()
async def buy_round(ctx):
    """Buy a round for everyone."""
    print(f"Command !buy round invoked by {ctx.author}")
    user = ctx.author
    total_members = len([member for member in ctx.guild.members if not member.bot])
    user_points = points.get(user, 0)

    if user_points < total_members:
        await ctx.send(f"{user.mention}, you don't have enough points to buy a round for everyone!")
        return

    points[user] = user_points - total_members
    members = [member for member in ctx.guild.members if not member.bot]
    random.shuffle(members)

    recipients = []
    for member in members:
        if points[user] > 0:
            points[member] = points.get(member, 0) + 1
            points[user] -= 1
            recipients.append(member.mention)
        else:
            break

    await ctx.send(f"{user.mention} bought a round! Points were given to: {', '.join(recipients)}. {user.mention} now has {points[user]} points.")

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
    
@bot.command()
async def jagerbomb(ctx):
    """Temporarily remove hangover for 15 minutes."""
    user = ctx.author
    if user in hangovers and hangovers[user] > datetime.now():
        original_hangover_end = hangovers[user]
        hangovers[user] = datetime.now() + timedelta(minutes=15)
        await ctx.send(f"{user.mention} took a jagerbomb! Hangover temporarily removed for 15 minutes.")
        await asyncio.sleep(15 * 60)  # 15 minutes
        hangovers[user] = original_hangover_end
        await ctx.send(f"{user.mention}, your hangover is back!")
    else:
        await ctx.send(f"{user.mention}, woah slow down there!")

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

bot.run(os.getenv("DISCORD_TOKEN"))