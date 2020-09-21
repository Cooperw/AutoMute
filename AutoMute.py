####################################################
##    Created by:  Cooper (@CWSharkbones#3537)    ##
##      https://github.com/Cooperw/AutoMute       ##
####################################################
'''
python something/DiscordBots/AutoMute.py

Feel free to use this code but please be sure to credit me in the code and store postings.
'''
########################## Imports ##########################
import discord
from discord import ChannelType
from discord.ext import tasks, commands

########################## Bot Variables ##########################
BOT_USERNAME = "AutoMute#0046"
TOKEN = "This is where you add you API token"
client = commands.Bot(command_prefix='!')
creator = "@CWSharkbones#3537"
BOT_CHANNEL = 'auto-mute'

approved_channels = []
approved_channels.append(BOT_CHANNEL)

cleanable_channels = []
cleanable_channels.append(BOT_CHANNEL)

########################## Other Variables ##########################

debug = False
SILENCE_ROLE = 'Cone of Silence'
seconds = 5

GREEN = 0x42f57e
YELLOW = 0xf2f542
RED = 0xfa341e

MUTED_URL = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/muted-speaker_1f507.png'
UNMUTED_URL = 'https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/259/speaker-low-volume_1f508.png'

########################## Commands ##########################
@client.command()
async def refresh(ctx, *, arg=""):
    if channel_approved(ctx.channel):
        return await refresh_voice_channels(ctx)

@client.command()
async def r(ctx, *, arg=""):
    if channel_approved(ctx.channel):
        return await refresh_voice_channels(ctx)

# Admin commands, I normally Pin the helper in the channel
@client.command()
async def h(ctx, *, arg=""):
    if channel_approved(ctx.channel):
        return await print_helper(ctx)

########################## Private/Helper Functions ##########################

def clean_string(name):
    name = name.replace('.','')
    name = name.replace('_','')
    name = name.replace('-','')
    name = name.replace("'",'')
    name = name.replace('"','')
    name = name.replace(':','')
    name = name.replace(',','')
    return name.strip().lower()

def captureError(method, error):
    print(method+": "+str(error))

class CustomError(Exception):
    pass
    
def channel_approved(channel):
    if(str(channel) not in approved_channels):
        print(str(channel)+" not in approved_channels")
        
    return str(channel) in approved_channels
    
def channel_cleanable(channel):
    if(str(channel) not in cleanable_channels):
        print(str(channel)+" not in cleanable_channels")
        
    return str(channel) in approved_channels

async def clean_channel(channel, clean_pinned=False, clean_bot=False):
    if channel_cleanable(channel):
        try:
            mgs = []
            async for x in channel.history():
                if(x.pinned and not clean_pinned):
                    pass
                elif (str(x.author) == BOT_USERNAME and not clean_bot):
                    pass
                else:
                    mgs.append(x)
            await channel.delete_messages(mgs)
        except Exception as e:
            print(e)
    return;

########################## Main Methods ##########################
def change_embed_color(_embed, color):
    em2 = discord.Embed(title=_embed.title, description=_embed.description, color=color)
    return em2

async def check_for_reaction(message):
    max_reaction = None
    max_reaction_count = 1
    
    for reaction in message.reactions:
        if reaction.count > max_reaction_count:
            max_reaction_count = reaction.count
            max_reaction = reaction
            
        users = await reaction.users().flatten()
        for user in users:
            if str(user) != BOT_USERNAME:
                await reaction.remove(user)
    
    if max_reaction_count > 1:
        if str(max_reaction.emoji) == '🔇':
            await mute(message, True)
            
            em2 = change_embed_color(message.embeds[0], RED)
            em2.set_thumbnail(url=MUTED_URL)
            await message.edit(embed=em2)
        elif str(max_reaction.emoji) == '🔈':
            await mute(message, False)
            
            em2 = change_embed_color(message.embeds[0], GREEN)
            em2.set_thumbnail(url=UNMUTED_URL)
            await message.edit(embed=em2)
        else:
            pass
    else:
        pass
        
    return

async def mute(message, _mute):
    title = message.embeds[0].title
    if title:
        for chan in message.guild.channels:
            if chan.name == title and chan.type==ChannelType.voice:
                channel = client.get_channel(chan.id)
        
                for member in channel.members:
                    try:
                        role = discord.utils.get(member.guild.roles, name=SILENCE_ROLE)
                    except:
                        pass

                    if _mute:
                        await member.edit(mute=True, deafen=True)
                        if role:
                            await member.add_roles(role)
                    else:
                        await member.edit(mute=False, deafen=False)
                        if role:
                            await member.remove_roles(role)
                break
    
########################## Command Methods ##########################
async def print_helper(ctx):
    embedHelp=discord.Embed()
    embedHelp = discord.Embed(title=BOT_USERNAME, description="I am here to help you manage your voice channels by using reaction controls!", color=YELLOW)
    embedHelp.add_field(name="Refresh:", value='Use this command to clean and update voice channels.\n!refresh', inline=False)
    embedHelp.add_field(name="Notes:", value='I run every '+str(seconds)+' seconds.\nI can only post in the "auto-mute" channel\nIf you create a "Cone of Silence" role it will be given to muted users', inline=False)
    embedHelp.set_footer(text='Created By: Cooper')
    
    await ctx.channel.send(embed=embedHelp)

async def refresh_voice_channels(ctx):
    await clean_channel(ctx.channel, clean_bot=True)
    
    voice_channels = (c.name for c in ctx.message.guild.channels if c.type==ChannelType.voice)
    for channel in voice_channels:
        embed=discord.Embed()
        embed = discord.Embed(title=str(channel), description="Use the reactions below to control the status of "+str(channel)+".", color=GREEN)
        embed.set_thumbnail(url=UNMUTED_URL)
        msg = await ctx.channel.send(embed=embed)
        for emoji in ('🔇', "🔈"):
            await msg.add_reaction(emoji)
    
async def check_channel(guild):
    for chan in guild.channels:
        if chan.name == BOT_CHANNEL:
            channel = client.get_channel(chan.id)
            try:
                async for x in channel.history():
                    await check_for_reaction(x)                
                await clean_channel(channel)
            except Exception as e:
                print(e)

########################## asyncio Methods ##########################
@tasks.loop(seconds=seconds)
async def check_task():
    async for partial_guild in client.fetch_guilds(limit=150):
        guild = client.get_guild(partial_guild.id)
        if guild:
            await check_channel(guild)
    
########################## Run ##########################
check_task.start()
client.run(TOKEN)