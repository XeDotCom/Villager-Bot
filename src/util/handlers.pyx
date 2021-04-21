from discord.ext import commands
import discord
import random

cpdef tuple handle_error(self: object, ctx: object, e: BaseException):
    if isinstance(e, commands.CommandOnCooldown):
        if ctx.command.name == "mine":
            if await self.db.fetch_item(ctx.author.id, "Efficiency I Book") is not None:
                e.retry_after -= 0.5

            if "haste ii potion" in self.d.chuggers.get(ctx.author.id, []):
                e.retry_after -= 1
            elif "haste i potion" in self.d.chuggers.get(ctx.author.id, []):
                e.retry_after -= 0.5

        seconds = round(e.retry_after, 2)

        if seconds <= 0.05:
            return (ctx.reinvoke(),)

        hours = int(seconds / 3600)
        minutes = int(seconds / 60) % 60
        seconds -= round((hours * 60 * 60) + (minutes * 60), 2)

        time = ""

        if hours == 1:
            time += f"{hours} {ctx.l.misc.time.hour}, "
        elif hours > 0:
            time += f"{hours} {ctx.l.misc.time.hours}, "

        if minutes == 1:
            time += f"{minutes} {ctx.l.misc.time.minute}, "
        elif minutes > 0:
            time += f"{minutes} {ctx.l.misc.time.minutes}, "

        if seconds == 1:
            time += f"{round(seconds, 2)} {ctx.l.misc.time.second}"
        elif seconds > 0:
            time += f"{round(seconds, 2)} {ctx.l.misc.time.seconds}"

        return (self.bot.send(ctx, random.choice(ctx.l.misc.cooldown_msgs).format(time)),)
    elif isinstance(e, commands.NoPrivateMessage):
        return (self.bot.send(ctx, ctx.l.misc.errors.private),)
    elif isinstance(e, commands.MissingPermissions):
        return (self.bot.send(ctx, ctx.l.misc.errors.user_perms),)
    elif isinstance(e, (commands.BotMissingPermissions, discord.errors.Forbidden)):
        return (self.bot.send(ctx, ctx.l.misc.errors.bot_perms),)
    elif getattr(e, "original", None) is not None and isinstance(e.original, discord.errors.Forbidden):
        return (self.bot.send(ctx, ctx.l.misc.errors.bot_perms),)
    elif isinstance(e, commands.MaxConcurrencyReached):
        # await self.bot.send(ctx, ctx.l.misc.errors.concurrency)
        return (self.bot.send(ctx, ctx.l.misc.errors.nrn_buddy),)
    elif isinstance(e, commands.MissingRequiredArgument):
        return (self.bot.send(ctx, ctx.l.misc.errors.missing_arg),)
    elif isinstance(
        e,
        (
            commands.BadArgument,
            commands.errors.UnexpectedQuoteError,
            commands.errors.ExpectedClosingQuoteError,
            commands.errors.BadUnionArgument,
        ),
    ):
        return (self.bot.send(ctx, ctx.l.misc.errors.bad_arg),)
    elif getattr(ctx, "custom_err", None) == "not_ready":
        return (self.bot.send(ctx, ctx.l.misc.errors.not_ready),)
    elif getattr(ctx, "custom_err", None) == "bot_banned":
        pass
    elif getattr(ctx, "custom_err", None) == "econ_paused":
        return (self.bot.send(ctx, ctx.l.misc.errors.nrn_buddy),)
    elif getattr(ctx, "custom_err", None) == "disabled":
        return (self.bot.send(ctx, ctx.l.misc.errors.disabled),)
    elif getattr(ctx, "custom_err", None) == "ignore":
        return tuple()
    else:
        # errors to ignore
        for e_type in (commands.CommandNotFound, commands.NotOwner):
            if isinstance(e, e_type) or isinstance(getattr(e, "original", None), e_type):
                return tuple()

        return (
            self.bot.send(ctx, ctx.l.misc.errors.andioop.format(self.d.support)),
            self.debug_error(ctx, e),
        )

cpdef tuple handle_message(self: object, m: object, replies: bool):
    if m.author.bot:
        return tuple()

    self.d.msg_count += 1

    if m.content.startswith(f"<@!{self.bot.user.id}>"):
        prefix = self.d.default_prefix

        if m.guild is not None:
            prefix = self.d.prefix_cache.get(m.guild.id, self.d.default_prefix)

        lang = self.bot.get_lang(m)

        embed = discord.Embed(color=self.d.cc, description=lang.misc.pingpong.format(prefix, self.d.support))

        embed.set_author(name="Villager Bot", icon_url=self.d.splash_logo)
        embed.set_footer(text=lang.misc.petus)

        return (m.channel.send(embed=embed),)

    if m.guild is not None:
        if m.guild.id == self.d.support_server_id:
            if m.type in (
                discord.MessageType.premium_guild_subscription,
                discord.MessageType.premium_guild_tier_1,
                discord.MessageType.premium_guild_tier_2,
                discord.MessageType.premium_guild_tier_3,
            ):
                return (
                    self.db.add_item(m.author.id, "Barrel", 1024, 1),
                    self.bot.send(m.author, f"Thanks for boosting the support server! You've received 1x **Barrel**!"),
                )

        content_lowered = m.content.lower()

        if "@someone" in content_lowered:
            someones = [
                u
                for u in m.guild.members
                if (
                    not u.bot
                    and u.status == discord.Status.online
                    and m.author.id != u.id
                    and u.permissions_in(m.channel).read_messages
                )
            ]

            if len(someones) > 0:
                invis = ("||||\u200B" * 200)[2:-3]
                return (m.channel.send(f"@someone {invis} {random.choice(someones).mention} {m.author.mention}"),)
        else:
            if not m.content.startswith(self.d.prefix_cache.get(m.guild.id, self.d.default_prefix)) and replies:
                if "emerald" in content_lowered:
                    return (m.channel.send(random.choice(self.d.hmms)),)
                elif "creeper" in content_lowered:
                    return (m.channel.send("awww{} man".format(random.randint(1, 5) * "w")),)
                elif "reee" in content_lowered:
                    return (m.channel.send(random.choice(self.d.emojis.reees)),)
                elif "amogus" in content_lowered:
                    return (m.channel.send(self.d.emojis.amogus),)

        return tuple()
