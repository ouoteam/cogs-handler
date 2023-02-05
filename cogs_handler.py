import os
import discord

# from pathlib import Path
from discord.ext import tasks, commands
from helpers.remote import get_remote_url

NOTIFY_CHANNEL = 1070956195130650704


class CogsHandler(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_git_changes.start()

    def get_all_cogs(self):
        for root, dirs, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py"):
                    yield root.replace(os.sep, ".") + "." + file[:-3]

    def cog_unload(self):
        print("[SKULL] YOU SHOULD NOT UNLOAD COGS HANDLER")

    @tasks.loop(minutes=3)
    async def check_git_changes(self):
        print(f"[INFO] Checking remote for updates")

    @check_git_changes.before_loop
    async def before_check_loop(self):
        await self.bot.wait_until_ready()
        await (self.bot.get_partial_messageable(NOTIFY_CHANNEL)).send(
            embed=discord.Embed(
                colour=discord.Colour.dark_theme(),
                title="開始檢查更新",
                fields=[discord.EmbedField("Git 儲存庫", get_remote_url())],
            )
        )

    @check_git_changes.after_loop
    async def after_check_loop(self):
        await (self.bot.get_partial_messageable(NOTIFY_CHANNEL)).send(
            embed=discord.Embed(
                colour=discord.Colour.dark_theme(),
                title="結束更新檢查",
            )
        )

    @check_git_changes.error
    async def check_loop_error(self, error):
        await (self.bot.get_partial_messageable(NOTIFY_CHANNEL)).send(
            embed=discord.Embed(
                colour=discord.Colour.dark_theme(),
                title="檢查發生錯誤",
                fields=[discord.EmbedField("內容", f"```{error}```")],
            )
        )

    cogs = discord.SlashCommandGroup("cogs", checks=[commands.is_owner().predicate])

    @cogs.command(description="載入插件")
    async def load(
        self,
        ctx,
        cog: discord.Option(str, description="插件名稱"),
    ):
        await ctx.defer()
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.respond(f"\❌`{cog}`: `{e}`")
        else:
            await ctx.respond(f"\✅成功載入插件 `{cog}`")

    @cogs.command(description="重載插件")
    async def reload(
        self,
        ctx,
        cog: discord.Option(str, description="插件名稱 (預設為重載全部)", required=False),
    ):
        await ctx.defer()
        if cog:
            try:
                self.bot.reload_extension(cog)
            except Exception as e:
                await ctx.respond(f"\❌`{cog}`: `{e}`")
            else:
                await ctx.respond(f"\✅成功重載插件 `{cog}`")
        else:
            output = ""
            for cog in self.bot.extensions:
                try:
                    self.bot.reload_extension(cog)
                    output += f"\n\✅成功重載插件 `{cog}`"
                except Exception as e:
                    output += f"\n\❌`{cog}`: `{e}`"
            else:
                await ctx.respond(output)


def setup(bot):
    bot.add_cog(CogsHandler(bot))
