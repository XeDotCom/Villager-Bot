from discord.ext import commands
import discord
from random import choice
import psycopg2
import json

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_count = 0
        self.cmd_count = 0
        with open("keys.json", "r") as k:
            keys = json.load(k)
        self.db = psycopg2.connect(host="localhost",database="villagerbot", user="pi", password=keys["postgres"])
        
    def cog_unload(self):
        self.db.close()
        
    @commands.Cog.listener()
    async def on_message(self, message):
        self.msg_count += 1
        if message.clean_content.startswith("!!"):
            self.cmd_count += 1
        
    @commands.command(name="ownerhelp", aliases=["helpowner", "owner"])
    @commands.is_owner()
    async def ownerhelp(self, ctx):
        embedMsg = discord.Embed(
            description = """
**!!unload** ***cog*** *unloads a cog*
**!!load** ***cog*** *loads a cog*
**!!reload** ***cog*** *reloads a cog, error if cog had not been loaded prior*
**!!activity** ***text*** *sets activity of bot to given text*
**!!nextactivity** *picks random activity from list*
**!!guilds** *lists guild member count, guild name, guild id*
**!!dms** *lists private channels (group msgs and dms)*
**!!leaveguild** ***guild id*** *leaves specified guild*
**!!getinvites** ***guild id*** *gets invite codes for specified guild*
**!!info2** *displays information about stuff*
**!!setbal** ***@user amount*** *set user balance to something*
**!!eval** ***statement*** *uses eval()*
**!!exec** ***statement*** *uses exec()*
**!!setpickaxe** ***user*** ***pickaxe type*** *sets pickaxe level of a user*
**!!botban** ***user*** *bans a user from using the bot*
**!!botunban** ***user*** *unbans a user from using the bot*
**!!inverseguildlookup** ***user*** *shows what servers a user is in*
**!!cogs** *lists the loaded cogs*""",
            color = discord.Color.green()
        )
        embedMsg.set_author(name="Villager Bot Owner Commands", url=discord.Embed.Empty, icon_url="http://172.10.17.177/images/villagerbotsplash1.png")
        await ctx.send(embed=embedMsg)

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension("cogs."+cog)
        except Exception as e:
            await ctx.send("Error while unloading extension: "+cog+"\n``"+str(e)+"``")
            return
        await ctx.send("Successfully unloaded cog: "+cog)

    @commands.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension("cogs."+cog)
        except Exception as e:
            await ctx.send("Error while loading extension: "+cog+"\n``"+str(e)+"``")
            return
        await ctx.send("Successfully loaded cog: "+cog)
            
    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, *, cog: str):
        try:
            self.bot.reload_extension("cogs."+cog)
        except Exception as e:
            await ctx.send("Error while reloading extension: "+cog+"\n``"+str(e)+"``")
            return
        await ctx.send("Successfully reloaded cog: "+cog)
        
    @commands.command(name="botban")
    @commands.is_owner()
    async def botban(self, ctx, user: discord.User):
        cur = self.db.cursor()
        cur.execute("SELECT id FROM bans WHERE bans.id='"+str(user.id)+"'")
        entry = cur.fetchone()
        if entry == None:
            cur.execute("INSERT INTO bans VALUES ('"+str(user.id)+"')")
            await ctx.send("Successfully banned "+str(user)+".")
            self.db.commit()
        else:
            await ctx.send(str(user)+" was already banned.")
        
    @commands.command(name="botunban")
    @commands.is_owner()
    async def botunban(self, ctx, user: discord.User):
        cur = self.db.cursor()
        cur.execute("SELECT id FROM bans WHERE bans.id='"+str(user.id)+"'")
        entry = cur.fetchone()
        if entry == None:
            await ctx.send(str(user)+" was not banned.")
        else:
            cur.execute("DELETE FROM bans WHERE bans.id='"+str(user.id)+"'")
            await ctx.send(str(user)+" was successfully unbanned.")
            self.db.commit()

    @commands.command(name="activity")
    @commands.is_owner()
    async def activity(self, ctx, *, message: str):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await self.bot.change_presence(activity=discord.Game(name=message))

    @commands.command(name="nextactivity")
    @commands.is_owner()
    async def nextactivity(self, ctx):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        playing = open("playing.txt", "r").readlines()
        await self.bot.change_presence(activity=discord.Game(name=choice(playing)))

    @commands.command(name="guilds")
    @commands.is_owner()
    async def guilds(self, ctx):
        i = 0
        rows = 35
        msg = ""
        for guild in self.bot.guilds:
            i += 1
            msg += "\n"+str(guild.member_count)+" **"+guild.name+"** *"+str(guild.id)+"*"
            if i%rows == 0:
                await ctx.send(msg)
                msg = ""
        if msg is not "":
            await ctx.send(msg)
            
    @commands.command(name="dms")
    @commands.is_owner()
    async def dmlist(self, ctx):
        i = 0
        rows = 30
        msg = ""
        for pchannel in self.bot.private_channels:
            i += 1
            try:
                msg += "\n*"+str(pchannel.id)+"*  "+str(pchannel)
            except Exception as e:
                msg += "\n"+str(e)
            if i%rows == 0:
                await ctx.send(msg)
                msg = ""
        if msg is not "":
            await ctx.send(msg)

    @commands.command(name="leaveguild")
    @commands.is_owner()
    async def leaveguild(self, ctx, *, guild: int):
        await self.bot.get_guild(guild).leave()
        
    @commands.command(name="getinvites")
    @commands.is_owner()
    async def getinvites(self, ctx, *, guild: int):
        invites = await self.bot.get_guild(guild).invites()
        i = 0
        rows = 30
        msg = ""
        for invite in invites:
            i += 1
            msg += "\n"+str(invite.code)
            if i%rows == 0:
                await ctx.send(msg)
                msg = ""
        if msg is not "":
            await ctx.send(msg)
        
    @commands.command(name="info2")
    @commands.is_owner()
    async def info2(self, ctx):
        infoEmbed = discord.Embed(
            description = "",
            color = discord.Color.green()
        )
        infoEmbed.add_field(name="__**Owner Info**__", value="""
Guild Count: {0}
DM Channel Count: {1}
User Count: {2}
Session Message Count: {3}
Session Command Count: {4}
Shard Count: {5}
Latency: {6} ms
""".format(str(len(self.bot.guilds)), str(len(self.bot.private_channels)), str(len(self.bot.users)), self.msg_count, self.cmd_count, self.bot.shard_count, str(self.bot.latency*1000)[:5]))
        await ctx.send(embed=infoEmbed)
        
    @commands.command(name="eval")
    @commands.is_owner()
    async def evalMessage(self, ctx, *, msg):
        try:
            evalMsg = eval(msg)
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=str(evalMsg)))
        except Exception as e:
            if type(e) == discord.HTTPException:
                if e.code == 50035:
                    with open("eval.txt", "w+") as evalF:
                        evalF.write(str(evalMsg))
                    with open("eval.txt", "r") as evalF:
                        await ctx.send(file=discord.File(evalF))
                else:
                    await ctx.send(str(e))
            else:
                await ctx.send(str(e))
                
    @commands.command(name="exec")
    @commands.is_owner()
    async def execMessage(self, ctx, *, msg):
        try:
            evalMsg = exec(msg)
            await ctx.send(embed=discord.Embed(color=discord.Color.green(), description=str(evalMsg)))
        except Exception as e:
            if type(e) == discord.HTTPException:
                if e.code == 50035:
                    with open("eval.txt", "w+") as evalF:
                        evalF.write(str(evalMsg))
                    with open("eval.txt", "r") as evalF:
                        await ctx.send(file=discord.File(evalF))
                else:
                    await ctx.send(str(e))
            else:
                await ctx.send(str(e))
                
    @commands.command(name="setpickaxe", aliases=["setpick"])
    @commands.is_owner()
    async def setpick(self, ctx, user: discord.User, pType: str):
        currency = self.bot.get_cog("Currency")
        await ctx.send(str(await currency.setpick(user.id, pType)))
        
    @commands.command(name="inverseguildlookup", aliases=["lookup"])
    @commands.is_owner()
    async def inverseguildlookup(self, ctx, user: discord.User):
        gds = ""
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.id == user.id:
                    gds+=str(guild)+" **|** "+str(guild.id)+"\n"
        if not gds == "":
            await ctx.send(gds)
        else:
            await ctx.send("No results...")
            
    @commands.command(name="cogs")
    @commands.is_owner()
    async def listCogs(self, ctx):
        for cog in self.bot.cogs:
            await ctx.send(self.bot.cogs[cog])
            
def setup(bot):
    bot.add_cog(Owner(bot))
