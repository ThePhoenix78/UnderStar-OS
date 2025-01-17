# coding: utf-8
from itertools import cycle
from pathlib import Path
import os.path
import time
import sys
import system.sys_app as sys_apps
import save.system.installed_app as installed_app
from system.lib import *

Lib = Lib_UsOS()

SYS_FOLDER = "system"
TOKEN_FOLDER = "token"
SAVE_FOLDER = "save"
APP_FOLDER = "app"
BOT_TOKEN_PATH = f"{TOKEN_FOLDER}/classbot_token"
UPDATE_FILE = f"{SYS_FOLDER}/app/update/update.pyw"
PREFIX = "?"
CODING = "utf-8"

programmer = os.path.basename(sys.argv[0])


vals = [SYS_FOLDER, TOKEN_FOLDER, SAVE_FOLDER, APP_FOLDER]

for name in vals:
    Path(name).mkdir(exist_ok=True)

BOT_TOKEN = "" 

try:
    with open(BOT_TOKEN_PATH, "r", encoding=CODING) as f:
        BOT_TOKEN = f.readlines()[0].strip()
except FileNotFoundError:
    with open(BOT_TOKEN_PATH, "w", encoding=CODING) as f:
        f.write("TOKEN_HERE")
        input("please insert the bot token in the file classbot_token")
        sys.exit(0)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord_commands.Bot(intents=intents, command_prefix=PREFIX, help_command=None)
client.remove_command('help')


status = cycle(["UnderStar OS"])


def get_apps(sys: bool=False) -> dict:
    """"""
    return sys_apps.all_app if sys else installed_app.all_app

async def import_apps(sys :bool=False) -> None:
    """"""
    for app_name,app in get_apps(sys).items():
        print(f"\nIMPORT {app_name}: ")
        loaded = 0
        errors = 0
        error_lst=[]

        app.Lib.init(client, installed_app)
        app.Lib.set_app_name(app_name)
        
        for command in app.Lib.app.commands:
            try:
                new_com=discord_commands.Command(command.command,name=f"{app_name}-{command.name}" if not command.force_name else command.name,help=command.help,aliases=command.aliases,checks=command.checks)
                if not new_com in client.all_commands.keys():
                    client.add_command(new_com)
                    loaded+=1
            except Exception as error:
                errors+=1
                error_lst.append(error)
        print(f"Command : {loaded} loaded | {errors} error : {error_lst}")

        loaded = 0
        errors = 0
        error_lst=[] 

        for command in app.Lib.app.slashs:
            try:
                #new_com=commands.Command(command.command,name=f"{app_name}-{command.name}",help=command.help,aliases=command.aliases,checks=command.checks)
                new_com=discord.app_commands.Command(name=f"{app_name.lower()}-{command.name.lower()}" if not command.force_name else command.name, description=command.description,callback=command.command)
                new_com.guild_only = False
                #new_com.default_permissions=discord.Permissions(8)
                if not new_com.name in [com.name for com in client.tree._get_all_commands()]:
                    if command.guilds == None:
                        guilds = discord.app_commands.tree.MISSING
                    elif command.guilds == []:
                        guilds = [discord.Object(id=608779766958653440)]
                    else:
                        guilds = command.guilds
                        if sys:
                            guilds = client.guilds
                        else:
                            guilds = [discord.Object(id=608779766958653440)]+app.Lib.guilds.get_app_guilds(app_name=app.Lib.app_name)
                    client.tree.add_command(new_com, guild=command.guild, guilds = guilds) #command.guilds
                    loaded+=1
            except Exception as error:
                errors+=1
                error_lst.append(error)
            
        print(f"Slash : {loaded} loaded | {errors} error : {error_lst}")


def get_help(ctx: discord_commands.context.Context) -> list[discord.Embed]:
    """"""
    embeds = []
    embed = discord.Embed(title="OS Commands", description=f"Préfix : `{PREFIX}` | Version : `{BOT_VERSION}`", color=discord.Color.red())
    try:
        coms = [com for com in client.all_commands]
        coms.sort()
        nb = 0
        page = 1
        nb_page = len(coms)//25
        embed.set_author(name=f'Liste des commandes {(page+"/"+nb_page) if nb_page > 1 else ""}')
        for com in coms:
            #print(com)
            if all([check(ctx) for check in client.all_commands[com].checks]+[True]):
                embed.add_field(name=f"**{com}**", value=f'{client.all_commands[com].help if client.all_commands[com].help != None else "Aucune aide disponible"}')
                nb+=1
            if nb==25:
                nb=0
                embeds.append(embed.copy())
                embed = discord.Embed(title="OS Commands", color=discord.Color.red())
                embed.set_author(name=f'Liste des commandes {page}/{nb_page}')
                page+=1
    except Exception as error:
        print(error)

    return embeds


def convert_time(value: int):
    """"""
    val3, val2, val = 0, value//60, value % 60
    message = f"{val2}min {val}s."

    if val2 > 60:
        val3, val2 = val2//60, val2 % 60
        message = f"{val3}h {val2}min {val}s."

    return message

timer = time.time()

# -------------------------------- Slash Command -------------------

@client.tree.command(name = "info", description = "Donne des infos sur le bot", guild=None)
async def info(ctx:discord.Interaction):
    embed = discord.Embed(title="INFO")
    embed.add_field(name=f"Version  :", value=f"`{BOT_VERSION}`")
    embed.add_field(name=f"Ping  :", value=f"` {round(client.latency * 1000)} `")
    embed.add_field(name=f"Time up  :", value=f"`{convert_time(int(time.time()-timer))}`")
    await ctx.response.send_message(embed=embed, ephemeral=True)


# -------------------------------- COMMANDE -------------------------------

@client.command(name="os-test", help="Envoie une pizza gatuite")
async def test(ctx:discord_commands.context.Context):
    await ctx.send(":pizza:")


@client.command(name="os-ping", aliases=["os-ver", "ver", "ping"], help="Donne des infos sur le bot")
@discord_commands.check(Lib.is_in_staff)
async def version(ctx:discord_commands.context.Context):
    embed = discord.Embed(title="INFO")
    embed.add_field(name=f"Version :", value=f"` {BOT_VERSION}   `")
    embed.add_field(name=f"Ping :", value=f"` {round(client.latency * 1000)} `")
    embed.add_field(name=f"Time up :", value=f"`{convert_time(int(time.time()-timer))}`")
    await ctx.send(embed=embed)


@client.command(name="os-help", aliases=["help"], help="Pour avoir ce message")
async def help(ctx:discord_commands.context.Context,*args):
    if args==():
        await ctx.send(embeds=get_help(ctx))
    else :
        if args[0] in get_apps().keys():
            sys_com = False
        elif args[0] in get_apps(True).keys():
            sys_com = True
        if len(args)==1:
            try:
                await get_apps(sys_com)[args[0]].Lib.help(ctx)
            except Exception as error:
                if type(error) == AttributeError:
                    await ctx.send(content=f"L'application `{args[0]}` n'a pas de fonction d'aide")
                else:
                    await ctx.send(content=f"La fonction d'aide de l'application `{args[0]}` ne fonctionne pas. Merci de contacter son développeur.")
        else:
            if f"{args[0]}-{args[1]}" in client.all_commands.keys():
                embed = discord.Embed(title=f"Aide sur la commande `{args[1]}`", description=f"Commande : `{PREFIX}{args[0]}-{args[1]}`", color=discord.Color.red())
                embed.set_author(name=f'App : {args[0]}')
                aide=client.all_commands[f"{args[0]}-{args[1]}"].help if client.all_commands[f"{args[0]}-{args[1]}"].help!="" else "Pas d'aide pour cette commande"
                alias=""
                for command in client.all_commands.keys():
                    if command!=f"{args[0]}-{args[1]}" and client.all_commands[command]==client.all_commands[f"{args[0]}-{args[1]}"]:
                        alias+=f"{command}, "
                embed.add_field(name=f"**{aide}**", value=f"Alias : {alias[:-1]}")
            else:
                embed = discord.Embed(title=f"La Command `{args[1]}` n'existe pas", description=f"Préfix de l'app : `{PREFIX}{args[0]}-`", color=discord.Color.red())
                embed.set_author(name=f"App : {args[0]}")
                #embed.add_field(name=f"**La Command {args[1]} n'existe pas**", value=f"Commande d'aide de l'application {args[0]} : !{args[0]}-help")
            try:
                await ctx.send(embed=embed)
            except Exception as error:
                print(error)

# ---------------------------------- EVENTS ------------------------------------

#App Commands
@client.event
async def on_raw_app_command_permissions_update(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_app_command_permissions_update(payload)

@client.event
async def on_app_command_completion(interaction, command):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_app_command_completion(interaction, command)

@client.tree.error
async def on_app_command_error(ctx: discord.Interaction, error: discord.app_commands.AppCommandError):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_app_command_error(ctx, error)

    if isinstance(error, discord.app_commands.CheckFailure):
        await ctx.response.send_message('Tu ne remplis pas les conditions pour executer cette commande.', ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await ctx.response.send_message('Le bot ne peut pas executer cette commande car il lui manque des autorisations. Merci de contacter le STAFF', ephemeral=True)

#AutoMod
@client.event
async def on_automod_rule_create(rule):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_automod_rule_create(rule)

@client.event
async def on_automod_rule_update(rule):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_automod_rule_update(rule)

@client.event
async def on_automod_rule_delete(rule):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_automod_rule_delete(rule)

@client.event
async def on_automod_action(execution):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_automod_action(execution)

#Channels
@client.event
async def on_guild_channel_delete(channel):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_channel_delete(channel)

@client.event
async def on_guild_channel_create(channel):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_channel_create(channel)

@client.event
async def on_guild_channel_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_channel_update(before, after)

@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_channel_pins_update(channel, last_pin)

@client.event
async def on_private_channel_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_private_channel_update(before, after)

@client.event
async def on_private_channel_pins_update(channel, last_pin):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_private_channel_pins_update(channel, last_pin)

@client.event
async def on_typing(channel, user, when):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_typing(channel, user, when)

@client.event
async def on_raw_typing(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_typing(payload)

#Connection

@client.event
async def on_connect(self):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_connect(self)

@client.event
async def on_disconnect(self):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_disconnect(self)

@client.event
async def on_shard_connect(shard_id):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_shard_connect(shard_id)

@client.event
async def on_shard_disconnect(shard_id):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_shard_disconnect(shard_id)

#Commande
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, discord_commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments')

    elif isinstance(error, discord_commands.CommandOnCooldown):
        value = int(f"{error.retry_after:.0f}")
        message = "Try again in "
        message += convert_time(value)

        em = discord.Embed(title="Slow it down bro!", description=message)
        await ctx.send(embed=em)
        
    print("error h", error)
    
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_command_error(ctx, error)

#Debug
@client.event
async def on_error(event, *args, **kwargs):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_error(event, *args, **kwargs)

@client.event
async def on_socket_event_type(event_type):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_socket_event_type(event_type)

@client.event
async def on_socket_raw_receive(msg):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_socket_raw_receive(msg)

@client.event
async def on_socket_raw_send(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_socket_raw_send(payload)

#Gateway

@client.event
async def on_ready():
    client.info = await client.application_info()
    change_status.start()
    #maintenance.start()

    with open(f'{SYS_FOLDER}/icon.png', 'rb') as image:
        pass
        #await client.user.edit(avatar=image.read())

    print("version : ", programmer, BOT_VERSION)
    print("Logged in as : ", client.user.name)
    print("ID : ", client.user.id)
    await import_apps(True)
    await import_apps()
    
    #await sync(client, "sync" in sys.argv)
    #print(client.guilds)
    await client.tree.sync()

    with open(f"{SAVE_FOLDER}/{SYS_FOLDER}/guilds.json") as f:
        data = json.load(f)
    for guild in client.guilds:
        pass
        if "sync" in sys.argv:
            client.tree.copy_global_to(guild=discord.Object(id=guild.id))
        await client.tree.sync(guild=discord.Object(id=guild.id))

        if str(guild.id) not in data.keys():
            data.update({str(guild.id):{"apps":[], "admin":[guild.owner.id], "password":None, "theme":"bleu"}})
            with open(f"{SAVE_FOLDER}/{SYS_FOLDER}/guilds.json", "w") as f:
                json.dump(data, fp=f)

    if "sync" in sys.argv:
        os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])

    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_ready()

@client.event
async def on_resumed():
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_resumed()

@client.event
async def on_shard_ready(shard_id):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_shard_ready(shard_id)

@client.event
async def on_shard_resumed(shard_id):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_shard_resumed(shard_id)

#Guilds
@client.event
async def on_guild_available(guild):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_available(guild)

@client.event
async def on_guild_unavailable(guild):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_unavailable(guild)

@client.event
async def on_guild_join(guild):
    with open(f"{SAVE_FOLDER}/{SYS_FOLDER}/guilds.json") as f:
        data = json.load(f)
    if str(guild.id) in data.keys():
        data.update({str(guild.id):{"apps":[], "admin":[guild.owner.id], "password":None, "theme":"bleu"}})
        with open(f"{SAVE_FOLDER}/{SYS_FOLDER}/guilds.json", "w") as f:
            json.dump(data, fp=f)

    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_join(guild)

@client.event
async def guild_remove(guild):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_remove(guild)

@client.event
async def on_guild_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_update(before, after)

@client.event
async def on_guild_emojis_update(guild, before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_emojis_update(guild, before, after)

@client.event
async def on_guild_stickers_update(guild, before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_stickers_update(guild, before, after)

@client.event
async def on_invite_create(invite):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_invite_create(invite)

@client.event
async def on_invite_delete(invite):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_invite_delete(invite)

#Integrations
@client.event
async def on_integration_create(integration):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_integration_create(integration)

@client.event
async def on_integration_update(integration):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_integration_update(integration)

@client.event
async def on_guild_integrations_update(guild):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_integrations_update(guild)

@client.event
async def on_webhooks_update(channel):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_webhooks_update(channel)

@client.event
async def on_raw_integration_delete(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_integration_delete(payload)

#Interactions
@client.event
async def on_interaction(interaction):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_interaction(interaction)
    pass

#Members
@client.event
async def on_member_join(member):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_member_join(member)

@client.event
async def on_member_remove(member):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_member_remove(member)

@client.event
async def on_raw_member_remove(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_member_remove(payload)

@client.event
async def on_member_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_member_update(before, after)

@client.event
async def on_user_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_user_update(before, after)

@client.event
async def on_member_ban(guild, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_member_ban(guild, user)

@client.event
async def on_member_unban(guild, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_member_unban(guild, user)

@client.event
async def on_presence_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_presence_update(before, after)

#Messages
@client.event
async def on_message(message):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_message(message)

@client.event
async def on_message_edit(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_message_edit(before, after)

@client.event
async def on_message_delete(message):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_message_delete(message)

@client.event
async def on_bulk_message_delete(messages):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_bulk_message_delete(messages)

@client.event
async def on_raw_message_edit(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_message_edit(payload)

@client.event
async def on_raw_message_delete(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_message_delete(payload)

@client.event
async def on_raw_bulk_message_delete(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_bulk_message_delete(payload)

#Reactions
@client.event
async def on_reaction_add(reaction, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_reaction_add(reaction, user)

@client.event
async def on_reaction_remove(reaction, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_reaction_remove(reaction, user)

@client.event
async def on_reaction_clear(message, reactions):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_reaction_clear(message, reactions)

@client.event
async def on_reaction_clear_emoji(reaction):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_reaction_clear_emoji(reaction)

@client.event
async def on_raw_reaction_add(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_reaction_add(payload)

@client.event
async def on_raw_reaction_remove(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_reaction_remove(payload)

@client.event
async def on_raw_reaction_clear(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_reaction_clear(payload)

@client.event
async def on_raw_reaction_clear_emoji(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_reaction_clear_emoji(payload)

#Roles
@client.event
async def on_guild_role_create(role):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_role_create(role)

@client.event
async def on_guild_role_delete(role):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_role_delete(role)

@client.event
async def on_guild_role_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_guild_role_update(before, after)

#Scheduled Events
@client.event
async def on_scheduled_event_create(event):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_scheduled_event_create(event)

@client.event
async def on_scheduled_event_delete(event):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_scheduled_event_delete(event)

@client.event
async def on_scheduled_event_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_scheduled_event_update(before, after)

@client.event
async def on_scheduled_event_user_add(event, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_scheduled_event_user_add(event, user)

@client.event
async def on_scheduled_event_user_remove(event, user):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_scheduled_event_user_remove(event, user)

#Stages
@client.event
async def on_stage_instance_create(stage_instance):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_stage_instance_create(stage_instance)

@client.event
async def on_stage_instance_delete(stage_instance):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_stage_instance_delete(stage_instance)

@client.event
async def on_stage_instance_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_stage_instance_update(before, after)

#Threads
@client.event
async def on_thread_create(thread):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_create(thread)

@client.event
async def on_thread_join(thread):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_join(thread)

@client.event
async def on_thread_update(before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_update(before, after)

@client.event
async def on_thread_remove(thread):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_remove(thread)

@client.event
async def on_thread_delete(thread):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_delete(thread)

@client.event
async def on_raw_thread_update(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_thread_update(payload)

@client.event
async def on_raw_thread_delete(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_thread_delete(payload)

@client.event
async def on_thread_member_join(member):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_member_join(member)

@client.event
async def on_thread_member_remove(member):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_thread_member_remove(member)

@client.event
async def on_raw_thread_member_remove(payload):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_raw_thread_member_remove(payload)

#Voice
@client.event
async def on_voice_state_update(member, before, after):
    for app in list(get_apps().values())+list(get_apps(True).values()):
        if app!=None:
            await app.Lib.event.on_voice_state_update(member, before, after)


# ----------------------------COMMANDE MAINTENANCE----------------------------------


@client.command(name="restart", help="Pour restart le bot")
@discord_commands.check(Lib.is_in_staff)
async def reboot(ctx:discord_commands.context.Context):
    await client.change_presence(activity=discord.Game("Restarting..."), status=discord.Status.dnd)

    await ctx.send("Restarting bot")
    os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])


@client.command(help="stop le bot")
@discord_commands.check(Lib.is_in_staff)
async def stop(ctx:discord_commands.context.Context):
    await ctx.send("Stopping")
    await client.change_presence(activity=discord.Game("Shutting down..."), status=discord.Status.dnd)
    exit(1)
    quit()


@client.command(aliases=["upt"], help="Pour update le bot")
@discord_commands.check(Lib.is_in_staff)
async def update(ctx:discord_commands.context.Context):
    await ctx.send("updating code !")
    await client.change_presence(activity=discord.Game("Updating..."), status=discord.Status.idle)
    
    val = os.system(f"start {UPDATE_FILE}")

    await client.change_presence(activity=discord.Game("Back from updt !"), status=discord.Status.online)
    print(val)
    if val==0:
        await ctx.send("Done")
        await client.close()
    else:
        await ctx.send("Error!")
        exit(0)


# -------------------------------------- TASKS -----------------------------------


@discord_tasks.loop(seconds=127)
async def change_status():
    if "sync" in sys.argv:
        await client.change_presence(activity=discord.Game("Re-Sync..."), status=discord.Status.dnd)
    else:
        await client.change_presence(activity=discord.Game(next(status)))

"""
resetSystem = False


@tasks.loop(seconds=43201)
async def maintenance():
    global resetSystem
    if resetSystem:
        await client.change_presence(activity=discord.Game("Restarting..."), status=discord.Status.idle)
        os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])

    resetSystem = True
"""
client.run(BOT_TOKEN)
