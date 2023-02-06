import os
import discord
from discord.ext import tasks, commands
from helpers.remote import (
    get_remote_url,
    get_local_commit,
    get_updates_info,
    merge_up_to,
)

NOTIFY_CHANNEL = 1070956195130650704


class UpdateActionsView(discord.ui.View):
    def __init__(self, commit_id: str):
        super().__init__(timeout=None)
        self.commit_id = commit_id

    @discord.ui.button(
        label="合併到這個提交",
        custom_id="merge-up-to-this-commit",
        style=discord.ButtonStyle.danger,
    )
    async def merge_button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        await interaction.followup.send(f"```{merge_up_to(self.commit_id)}```")
        button.disabled = True
        await interaction.message.edit(view=self)


class CogsHandler(discord.Cog):
    def __init__(self, bot: discord.Bot):
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
        if updates := get_updates_info():
            await (self.bot.get_partial_messageable(NOTIFY_CHANNEL)).send(
                " ".join([f"<@{owner}>" for owner in self.bot.owner_ids]),
                embed=discord.Embed(
                    colour=discord.Colour.dark_theme(),
                    title="有新更新",
                    fields=[
                        discord.EmbedField("目標提交代碼", f"```{updates[0]}```"),
                        discord.EmbedField("目標提交訊息", updates[1]),
                    ],
                ),  # .set_footer(text=f"本機提交代碼: {get_local_commit()}")
                view=UpdateActionsView(updates[0]),
            )

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
    async def check_loop_error(self, error: Exception):
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


def setup(bot: discord.Bot):
    bot.add_cog(CogsHandler(bot))
