import discord
import youtube_dl
import asyncio

from discord.ext import commands
from discord.ext.commands import Bot

TOKEN = 'NDc0NzIyNDg0NjgwMjYxNjMz.DkWCxQ.jLur90XrG5E22ejFY4YHZ7wC7Mo'

client = commands.Bot(command_prefix='.')
client.remove_command('help')

players = {}
queues = {}

def check_queues(id):
    if queues[id] != []:
        player = queues[id].pop(0)
        players[id] = player
        player.start()

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='Type .help for some helpful info'))
    print ("I'm ready to go")
    print ("I am running on " + client.user.name)
    print ("With the ID: " + client.user.id)

@client.command()
async def ping():
    await client.say('Pong')

@client.command(pass_context=True)
async def info(ctx, user: discord.Member):
    embed = discord.Embed(title="{}'s info".format(user.name), description="Here's what I could find.", color=0x00ff00)
    embed.add_field(name="Name", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Status", value=user.status, inline=True)
    embed.add_field(name="Highest role", value=user.top_role)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.set_thumbnail(url=user.avatar_url)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def serverinfo(ctx):
    embed = discord.Embed(name="{}'s info".format(ctx.message.server.name), description="Here's what I could find.", color=0x00ff00)
    embed.set_author(name="Server Info")
    embed.add_field(name="Name", value=ctx.message.server.name, inline=True)
    embed.add_field(name="ID", value=ctx.message.server.id, inline=True)
    embed.add_field(name="Roles", value=len(ctx.message.server.roles), inline=True)
    embed.add_field(name="Members", value=len(ctx.message.server.members))
    embed.set_thumbnail(url=ctx.message.server.icon_url)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='.ping', value='Returns pong. This is a test command to insure the bot is working', inline=True)
    embed.add_field(name='.clear', value='This will clear out any message in a bulk fashion this is a staff only command', inline=True)
    embed.add_field(name='.mods', value='List of all the staff members')
    embed.add_field(name='.join', value='The bot will join whatever voice channel you are in', inline=True)
    embed.add_field(name='.leave', value='The bot will leave whatever voice  channel you are in', inline=True)
    embed.add_field(name='.play', value='To use this command find a youtube link of whatever song you want then type the command followed by the link', inline=True)
    embed.add_field(name='.stop', value='This will stop the music player', inline=True)
    embed.add_field(name='.pause', value='This will pause the current song', inline=True)
    embed.add_field(name='.resume', value='This will resume the current song', inline=True)
    embed.set_thumbnail(url=ctx.message.server.icon_url)

    await client.send_message(author, embed=embed)

@client.command(pass_context=True)
@commands.has_role("Owner")
@commands.has_role("Moderators")
async def clear(ctx, amount=100):
    channel = ctx.message.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount)):
        messages.append(message)
    await client.delete_messages(messages)
    await client.say("Messages wiped.")

@client.command(pass_context=True)
async def mods(ctx):
    embed = discord.Embed(name='Staff Team', description='This is the staff team from highest to lowest', color=0x00ff00)
    embed.add_field(name='Owner', value='DizzyThermal', inline=False)
    embed.add_field(name='Moderator', value='SlothySco', inline=False)
    embed.add_field(name='Moderator', value='ShatteredHCD', inline=False)
    embed.add_field(name='Moderator', value='Mango', inline=False)
    embed.add_field(name='Moderator', value='NerÆus96', inline=False)
    embed.add_field(name='Moderator', value='SpeedyJake01', inline=False)
    embed.set_thumbnail(url=ctx.message.server.icon_url)
    await client.say(embed=embed)

@client.command(pass_context=True)
@commands.has_role("Moderators")
async def kick(ctx, user: discord.Member):
    await client.say(":boot:16 star:{} Mips has kicked you out of bounds".format(user.name))
    await client.kick(user)

@client.command(pass_context=True)
@commands.has_role("Owner")
async def ban(ctx, user: discord.Member):
    await client.say(":hammer: {} Failed a 0 star run awww to bad CYA TROLL :hammer:".format(user.name))
    await client.ban(user)

@client.command(pass_context=True)
@commands.has_role("Owner")
async def unban(ctx):
    ban_list = await client.get_bans(ctx.message.server)

    # Show banned users
    await client.say("Ban list:\n{}".format("\n".join([user.name for user in ban_list])))

    # Unban last banned user
    if not ban_list:
        await client.say("Ban list is empty.")
        return
    try:
        await client.unban(ctx.message.server, ban_list[-1])
        await client.say("Unbanned user: `{}`".format(ban_list[-1].name))
    except discord.Forbidden:
        await client.say("I do not have permission to unban.")
        return
    except discord.HTTPException:
        await client.say("Unban failed.")
        return

#music commands
@client.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.voice_channel
    await client.join_voice_channel(channel)

@client.command(pass_context=True)
async def leave(ctx):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    await voice_client.disconnect()

@client.command(pass_context=True)
async def play(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))
    players[server.id] = player
    player.start()

@client.command(pass_context=True)
async def pause(ctx):
    id = ctx.message.server.id
    players[id].pause()

@client.command(pass_context=True)
async def stop(ctx):
    id = ctx.message.server.id
    players[id].stop()

@client.command(pass_context=True)
async def resume(ctx):
    id = ctx.message.server.id
    players[id].resume()

@client.command(pass_context=True)
async def queue(ctx, url):
    server = ctx.message.server
    voice_client = client.voice_client_in(server)
    player = await voice_client.create_ytdl_player(url, after=lambda: check_queue(server.id))

    if server.id in queues:
        queues[server.id].append(player)
    else:
        queues[server.id] = [player]
    await client.say('Song added to the queue')

@client.command(pass_context=True)
@commands.has_role("Owner")
async def logout():
    await client.logout()

client.run(TOKEN)
