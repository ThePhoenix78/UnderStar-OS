# coding: utf-8
from itertools import cycle
from pathlib import Path
import discord
from discord.ext import commands, tasks
import os.path
import time
import sys
import save.system.installed_app as apps
import system.sys_app as sys_apps
import asyncio
from system.lib import is_in_staff




bot_version = "0.1"
sys_folder = "system"
token_folder = "token"
save_folder = "save"
app_folder = "app"
classbot_token = f"{token_folder}/classbot_token"
update_file = f"{sys_folder}/app/update/update.pyw"
prefix="?"

programmer = os.path.basename(sys.argv[0])


vals = [sys_folder,app_folder]

for name in vals:
    Path(name).mkdir(exist_ok=True)

bot_token = "" 

try:
    with open(classbot_token, "r") as f:
        bot_token = f.readlines()[0].strip()
except FileNotFoundError:
    with open(classbot_token, "w") as f:
        f.write("TOKEN_HERE")
        input("please insert the bot token in the file classbot_token")
        sys.exit(0)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix=prefix, help_command=None)
client.remove_command('help')



status = cycle(["UnderStar OS"])

def get_apps(sys=False) -> dict:
    return sys_apps.all_app if sys else apps.all_app

async def import_apps(sys=False):
    for app_name,app in get_apps(sys).items():
        print(app_name, app.app.commands)
        app.init_client(client)
        
        for command in app.app.commands:
            new_com=commands.Command(command.command,name=f"{app_name}-{command.name}" if not command.force_name else command.name,help=command.help,aliases=command.aliases,checks=command.checks)
            if not new_com in client.all_commands.keys():
                client.add_command(new_com)
            
        for task in app.app.task:
            new_task=tasks.Loop(task.fonction,seconds=task.seconds, hours=task.hours,minutes=task.minutes, time=task.time, count=task.count, reconnect=task.reconnect)
            #await new_task.start()
            
        for command in app.app.slashs:
            #new_com=commands.Command(command.command,name=f"{app_name}-{command.name}",help=command.help,aliases=command.aliases,checks=command.checks)
            new_com=discord.app_commands.Command(name=f"{app_name}-{command.name}" if not command.force_name else command.name, description=command.description,callback=command.command)
            #new_com.default_permissions=discord.Permissions(8)
            if not new_com.name in [com.name for com in client.tree._get_all_commands()]:
                client.tree.add_command(new_com, guild=command.guild, guilds=command.guilds)
            
        
                    
        
            


def get_help(ctx:commands.context.Context, is_slash: bool = False):
    embed = discord.Embed(title="OS Commands", description=f"Préfix : `{prefix}`", color=discord.Color.red())
    embed.set_author(name='Liste des commandes')
    try:
        coms = [com for com in client.all_commands]
        coms.sort()
        for com in coms:
            #print(com)
            if all([check(ctx) for check in client.all_commands[com].checks]+[True]):
                embed.add_field(name=f"**{com}**", value=f'{client.all_commands[com].help if client.all_commands[com].help != None else "Aucune aide disponible"}')
    except Exception as error:
        print(error)

    return embed


def convert_time(value: int):
    val3, val2, val = 0, value//60, value % 60
    message = f"{val2}min {val}s."

    if val2 > 60:
        val3, val2 = val2//60, val2 % 60
        message = f"{val3}h {val2}min {val}s."

    return message


def is_dev(ctx):
    if ctx.author.id in [608779421683417144]:
        return True

    member = ctx.message.author
    roles = [role.name for role in member.roles]
    admins = ["Bot Dev"]

    for role in roles:
        if role in admins:
            return True


def is_in_maintenance(ctx):
    if ctx.author.id in [366055261930127360, 649532920599543828]:
        return True

    member = ctx.message.author
    roles = [role.name for role in member.roles]
    admins = ["Admin", "Modo", "Bot Dev"]

    for role in roles:
        if role in admins:
            return True

        if "maint." in role:
            return True

timer = time.time()

# -------------------------------- Slash Command (test) -------------------

@client.tree.command(name = "info", description = "donne des infos sur le bot", guild=None) #, guilds=[discord.Object(id=649021344058441739)] Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
@discord.app_commands.check(is_in_staff)
async def first_command(ctx:discord.Interaction):
    embed = discord.Embed(title="INFO")
    embed.add_field(name=f"Version :", value=f"` {bot_version}   `")
    embed.add_field(name=f"Ping :", value=f"` {round(client.latency * 1000)} `")
    embed.add_field(name=f"Time up :", value=f"`{convert_time(int(time.time()-timer))}`")
    await ctx.response.send_message(embed=embed)




# -------------------------------- COMMANDE -------------------------------

@client.command(name="os-test")
async def test(ctx):
    await ctx.send(":pizza:")


@client.command(name="os-ping", aliases=["os-ver"])
@commands.check(is_in_staff)
async def version(ctx:commands.context.Context):
    value = int(time.time()-timer)
    message = convert_time(value)
    final_message = f"version : {bot_version}\nping : {round(client.latency * 1000)}ms :ping_pong:\ntime up : {message}"
    await ctx.send(final_message)


@client.command(name="os-help", aliases=["help"], help="pour avoir ce message")
async def help(ctx:commands.context.Context,*args):
    print(args)
    if args==():
        await ctx.send(embed=get_help(ctx, False))
    elif args[0] in get_apps().keys():
        if len(args)==1:
            await get_apps()[args[0]].help(ctx)
        else:
            if f"{args[0]}-{args[1]}" in client.all_commands.keys():
                embed = discord.Embed(title=f"Aide sur la commande `{args[1]}`", description=f"Commande : `{prefix}{args[0]}-{args[1]}`", color=discord.Color.red())
                embed.set_author(name=f'App : {args[0]}')
                aide=client.all_commands[f"{args[0]}-{args[1]}"].help if client.all_commands[f"{args[0]}-{args[1]}"].help!="" else "Pas d'aide pour cette commande"
                alias=""
                for command in client.all_commands.keys():
                    if command!=f"{args[0]}-{args[1]}" and client.all_commands[command]==client.all_commands[f"{args[0]}-{args[1]}"]:
                        alias+=f"{command}, "
                embed.add_field(name=f"**{aide}**", value=f"Alias : {alias[:-1]}")
            else:
                embed = discord.Embed(title=f"La Command `{args[1]}` n'existe pas", description=f"Préfix de l'app : `{prefix}{args[0]}-`", color=discord.Color.red())
                embed.set_author(name=f"App : {args[0]}")
                #embed.add_field(name=f"**La Command {args[1]} n'existe pas**", value=f"Commande d'aide de l'application {args[0]} : !{args[0]}-help")
            try:
                await ctx.send(embed=embed)
            except Exception as error:
                print(error)

# ---------------------------------- EVENTS ------------------------------------
@client.event
async def on_ready():
    change_status.start()
    #maintenance.start()

    with open(f'{sys_folder}/icon.png', 'rb') as image:
        pass
        #await client.user.edit(avatar=image.read())

    print("version : ", programmer, bot_version)
    print("Logged in as : ", client.user.name)
    print("ID : ", client.user.id)
    await import_apps(True)
    await import_apps()
    for guild in client.guilds:
        client.tree.copy_global_to(guild=discord.Object(id=guild.id))
        await client.tree.sync(guild=discord.Object(id=guild.id))
        await client.tree.sync()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments')

    elif isinstance(error, commands.CommandOnCooldown):
        value = int(f"{error.retry_after:.0f}")
        message = "Try again in "
        message += convert_time(value)

        em = discord.Embed(title="Slow it down bro!", description=message)
        await ctx.send(embed=em)
    print("error h", error)

@client.tree.error
async def on_app_command_error(ctx: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        await ctx.response.send_message('Tu ne remplis pas les conditions pour executer cette commande.', ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await ctx.response.send_message('Le bot ne peut pas executer cette commande car il lui manque des autorisations. Merci de contacter le STAFF', ephemeral=True)

# ----------------------------COMMANDE MAINTENANCE----------------------------------


@client.command(name="re", help="Pour restart le bot")
@commands.check(is_in_staff)
async def reboot(ctx:commands.context.Context):
    await client.change_presence(activity=discord.Game("Restarting..."), status=discord.Status.dnd)

    await ctx.send("Restarting bot")
    os.execv(sys.executable, ["None", os.path.basename(sys.argv[0])])


@client.command(help="stop le bot")
@commands.check(is_in_staff)
async def stop(ctx:commands.context.Context):
    await ctx.send("Stopping")
    await client.change_presence(activity=discord.Game("Shutting down..."), status=discord.Status.dnd)
    exit(1)
    quit()


@client.command(aliases=["upt"], help="Pour update le bot")
@commands.check(is_dev)
async def update(ctx:commands.context.Context, *, ipe=programmer):
    await ctx.send("updating code !")
    await client.change_presence(activity=discord.Game("Updating..."), status=discord.Status.idle)

    val = os.system(f"start {update_file}")

    await client.change_presence(activity=discord.Game("Back from updt !"), status=discord.Status.online)
    print(val)
    if val==0:
        await ctx.send("Done")
        await client.close()
    else:
        await ctx.send("Error!")
        exit(0)


# -------------------------------------- TASKS -----------------------------------


@tasks.loop(seconds=127)
async def change_status():
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
client.run(bot_token)
