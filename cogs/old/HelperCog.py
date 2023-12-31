import asyncio
import urllib
import requests
from typing import Literal, Optional

import nextcord
from nextcord.ext import commands, tasks
from nextcord.ext.commands import Bot, Cog, Context

from ..extensions.EXFormatExtension import ex_format


class AnimeView(nextcord.ui.View):
    def __init__(self, url, message):
        super().__init__(timeout=5*60)
        self.message = message
        self.url = urllib.parse.quote_plus(url)
        self.json = requests.get(f"https://api.trace.moe/search?url={self.url}").json()
        results = self.json["result"]
        main_embed = nextcord.Embed(
            title="Your search image"
        )
        main_embed.set_image(url)
        main_embed.set_footer(text=f"Searched {self.json['frameCount']} frames")
        self.embeds = [main_embed]
        for result in results:
            embed = nextcord.Embed(
                description=f"```Anilist: {result['anilist']}```"
                f"```Episode: {result['episode']}```"
                f"```Time: {self.convert_time_format(result['from'])} - {self.convert_time_format(result['to'])}```"
            )
            embed.set_author(name=result["filename"], url=result["video"])
            embed.set_image(result["image"])
            embed.set_footer(text=f"~{round(result['similarity']*100)}% Similarity")
            self.embeds.append(embed)
        self.return_back = nextcord.ui.Button(label="return_back")
        async def return_back_callback(interaction):
            self.add_item(self.dropdown)
            self.remove_item(self.return_back)
            await self.message.edit(content=None, embed=self.embeds[0], view=self)
        self.return_back.callback = return_back_callback
        self.dropdown = nextcord.ui.Select(
            placeholder="Select the search result...",
            options=[
                nextcord.SelectOption(
                    label=str(embed.author.name)[:100],
                    description=str(embed.footer.text),
                    value=self.embeds.index(embed)
                ) for embed in self.embeds[1:][:25]
            ]
        )
        async def dropdown_callback(interaction):
            self.add_item(self.return_back)
            self.remove_item(self.dropdown)
            await self.message.edit(embed=self.embeds[int(self.dropdown.values[0])], view=self)
        self.dropdown.callback = dropdown_callback 
        self.add_item(self.dropdown)
        self.on_init.start()

    @staticmethod
    def convert_time_format(time):
        minutes = int(time / 60)
        seconds = int(time % 60)
        milliseconds = int((time - int(time)) * 100)
        formatted_time = f"{minutes:02d}:{seconds:02d}:{milliseconds:02d}"
        return formatted_time

    @tasks.loop(count=1)
    async def on_init(self):
        await self.message.edit(content=None, embed=self.embeds[0], view=self)   

    async def on_timeout(self):
        await self.message.edit(content="timeout...", view=None)


class HelperCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.on_init.start()

    @tasks.loop(count=1)
    async def on_init(self):
        pass

    def cog_unload(self):
        self.online_members.stop()
        pass


    @Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        try:
            if "●" in before.channel.name and len(before.channel.members) == 0:
                await asyncio.sleep(10)
                channel = self.bot.get_channel(before.channel.id)
                if channel is not None:
                    await channel.delete()
        except AttributeError:
            pass
        except BaseException as ex:
            print(ex_format(ex, "on_voice_helper"))

    @commands.command()
    async def image(self, ctx: Context, url: Optional[str] = None):
        allowed = [
            497644678506741760, 1135088921500459049, 1135987909367959582,
            857627224769298445, 1134833163848388688, 1134833348473262240
        ]
        if not any(role.id in allowed for role in ctx.author.roles):
            return
        try:
            if "http" not in str(url) and len(ctx.message.attachments) == 0:
                await ctx.reply("неверный url или attachments")
                return
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            message = await ctx.reply("loading...")
            view = AnimeView(url, message)
        except BaseException as ex:
            print(ex_format(ex, "image_helper"))
        
    @commands.command()
    async def helper(self, ctx: Context):
        if ctx.author.id not in self.bot.OWNERS:
            return
        await ctx.send("temp")

    @commands.command()
    async def user_info(self, ctx, userid: int):
        user = await ctx.bot.fetch_user(userid)
        
        joined = str(ctx.author.joined_at).split(' ')[0].split('-')
        created = str(user.created_at).split(' ')[0].split('-')
        
        if (int(joined[0]) - int(created[0])) < 1:
            await ctx.send(f'{joined[0]}, {created[0]}')
    
    @Cog.listener()
    async def on_message(self, message):
        # Проверяем, что сообщение отправлено в нужные чаты
        if message.channel.id == 1141374754352267264:
            # Выдаем роль с id 1149037221769400511
            role = message.guild.get_role(1149037221769400511)
            if role:
                await message.author.add_roles(role)
        elif message.channel.id == 1141374728502788299:
            # Выдаем роль с id 1149037331051986975
            role = message.guild.get_role(1149037331051986975)
            if role:
                await message.author.add_roles(role)


# on_ready cog!
def setup(bot: Bot):
    print("HelperCog loaded!")
    bot.add_cog(HelperCog(bot))
