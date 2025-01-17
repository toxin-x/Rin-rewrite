"""Reactions Module"""

from datetime import datetime
import discord
from discord.ext import commands
from discord.utils import get

from main import db


class ReactionsCog(commands.Cog):
    """Class to handling raw reactions"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handler for raw reactions"""
        channel = await self.bot.fetch_channel(payload.channel_id)
        reacted_message: discord.Message = await channel.fetch_message(
            payload.message_id
        )
        log_channel_id = db.fetchone_singlecolumn(
            0,
            "SELECT log_channel_id FROM bot_log_channel WHERE guild_id = ?",
            payload.guild_id,
        )
        description = ""

        if log_channel_id is None and payload.emoji.name == "🚫":
            await channel.send(
                embed=discord.Embed(
                    title="there are no log channel set for this server",
                    description="please set a log channel with the /set_log_channel command",
                    color=0xFF0000,
                ),
                delete_after=10,
            )
        elif payload.member.bot == False == False and payload.emoji.name == "🚫":
            if (
                payload.member.guild_permissions.administrator is True
                or payload.member.guild_permissions.manage_messages is True
                or payload.user_id == reacted_message.author.id
            ):
                await reacted_message.delete()
                description = "*The message has been deleted as it has been reported by an admin.*"

            if (
                not payload.user_id == reacted_message.author.id
                and get(reacted_message.reactions, emoji=payload.emoji.name).count == 1
            ):
                log_channel = await self.bot.fetch_channel(log_channel_id)
                now = str(
                    datetime.now().astimezone().strftime("%d/%m/%Y - %H:%M:%S (UTC%z)")
                )
                message_creation_timestamp = int(reacted_message.created_at.timestamp())
                reacted_message_author_roles = None
                long_message = False
                is_member = True
                guild = self.bot.get_guild(payload.guild_id)

                # check if user is a member of the server or not
                if guild.get_member(reacted_message.author.id) is None:
                    is_member = False
                    description += "\n*This user is currently not on the server.*"

                if is_member is True:
                    for role in reacted_message.author.roles:
                        if role.name != "@everyone":
                            if reacted_message_author_roles is None:
                                reacted_message_author_roles = str(role.mention)
                            else:
                                reacted_message_author_roles = (
                                    str(reacted_message_author_roles)
                                    + ", "
                                    + str(role.mention)
                                )

                reported_message_embed = discord.Embed(
                    title="Reported Message - ID: " + str(reacted_message.id),
                    description=description,
                    color=0xFF0000,
                )

                if reacted_message.author.avatar is None:
                    reported_message_embed.set_thumbnail(
                        url="https://cdn.discordapp.com/embed/avatars/0.png"
                    )
                else:
                    reported_message_embed.set_thumbnail(
                        url=reacted_message.author.avatar.url
                    )

                reported_message_embed.add_field(
                    name="Username", value=reacted_message.author.name, inline=True
                )

                if is_member is True:
                    reported_message_embed.add_field(
                        name="Nickname", value=reacted_message.author.nick, inline=True
                    )

                reported_message_embed.add_field(
                    name="User ID",
                    value="<@" + str(reacted_message.author.id) + ">",
                    inline=True,
                )
                reported_message_embed.add_field(
                    name="Channel",
                    value="<#" + str(reacted_message.channel.id) + ">",
                    inline=True,
                )

                if is_member is True:
                    reported_message_embed.add_field(
                        name="User Roles",
                        value=str(reacted_message_author_roles),
                        inline=True,
                    )
                reported_message_embed.add_field(
                    name="Message creation date/time",
                    value="<t:"
                    + str(message_creation_timestamp)
                    + ":D> - <t:"
                    + str(message_creation_timestamp)
                    + ":T>",
                    inline=True,
                )
                # if the message is too long
                if len(reacted_message.content) >= 1000:
                    long_message = True
                    message_length = len(reacted_message.content)

                    reacted_message_content_part2 = reacted_message.content[
                        999:message_length
                    ]

                    reacted_message_content_part1 = reacted_message.content[0:999]

                    reported_message_embed.add_field(
                        name="Message",
                        value=reacted_message_content_part1,
                        inline=False,
                    )

                    reported_message_part2_embed = discord.Embed(
                        description="*The message is over 1000 characters, so it has been split into 2 Discord embeds.*",
                        color=0xFF0000,
                    )

                    reported_message_part2_embed.add_field(
                        name="Message (part 2)",
                        value=reacted_message_content_part2,
                        inline=False,
                    )

                    reported_message_part2_embed.set_footer(
                        text="Reported by "
                        + str(payload.member.name)
                        + "#"
                        + str(payload.member.discriminator)
                        + "  •  "
                        + now,
                        icon_url=payload.member.avatar.url,
                    )
                else:
                    # even if message is deleted, you can still jump to the context with jump_url
                    message = (
                        reacted_message.content
                        + "\n"
                        + "[Jump to context]("
                        + reacted_message.jump_url
                        + ")"
                    )

                    reported_message_embed.add_field(
                        name="Message", value=message, inline=False
                    )

                    reported_message_embed.set_footer(
                        text="Reported by "
                        + str(payload.member.name)
                        + "#"
                        + str(payload.member.discriminator)
                        + "  •  "
                        + now,
                        icon_url=payload.member.avatar.url,
                    )

                files = []
                file_names = []

                for idx, attachment in enumerate(reacted_message.attachments):
                    # max # of files to attach to a message == 10
                    if idx > 10:
                        continue

                    files.append(await attachment.to_file(spoiler=True))
                    file_names.append(attachment.filename)

                if files:
                    reported_message_embed.add_field(
                        name="Attachments", value="\n".join(file_names), inline=False
                    )

                await log_channel.send(embed=reported_message_embed, files=files)
                if long_message is True:
                    await log_channel.send(embed=reported_message_part2_embed)


async def setup(bot):
    """Adds cog to bot"""
    await bot.add_cog(ReactionsCog(bot))
