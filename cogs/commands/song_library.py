from datetime import datetime
import discord
import templates.embeds as embeds
from discord import app_commands
from discord.ext import commands
import spotipy

from main import db
from main import sp

class SongLibraryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rebuild_song_library", description="Deletes the entire song library and rebuilds it")
    @app_commands.checks.has_permissions(administrator=True)
    async def rebuild_song_library(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            await interaction.followup.send(embed=discord.Embed(
                    title="Rebuilding song library...", 
                    description="This might take some time.", 
                    color=0xff0000), ephemeral=True)
            db.clear_song_library()
            db.create_song_library()
            await interaction.followup.edit(embed=discord.Embed(
                    title="Song library rebuilt successfully!", 
                    color=0xff0000))
        except:
            await embeds.error_executing_command(interaction, edit=True, title_detail="rebuilding the song library.")
            raise

    @app_commands.command(name="add_song_to_presence_queue", description="Adds a song in the presence queue for Rin to listen to")
    @app_commands.describe(url="URL of the song (Spotify only, single tracks only. No full albums or playlists links)")
    async def add_song_to_presence_queue(self, interaction: discord.Interaction, url: str):
        try:
            await interaction.response.defer()
            user_id = interaction.user.id
            check_number_of_user_queued_songs = db.fetchone_singlecolumn(0, "SELECT count(user_id) FROM bot_user_song_library WHERE user_id = ? GROUP BY user_id", user_id)
            if not check_number_of_user_queued_songs == None and check_number_of_user_queued_songs >= 3:
                await interaction.followup.send(embed=discord.Embed(title="You cannot put more than 3 tracks in the queue!", description="Please wait until Rin has listened to one of your 3 tracks before putting more.", color=0xff0000), ephemeral=True)
            elif "open.spotify.com/track/" in url:
                try:
                    artists = ""
                    artist_count = 0
                    album_art_url = ""
                    for artist in sp.track(url)['album']['artists']:
                        artist_count += 1
                        if artist_count == 1:
                            artists = artist['name']
                        else:
                            artists = artists + ", " + artist['name']
                    for album_art in sp.track(url)['album']['images']:
                        if album_art['height'] == 640 and album_art['width'] == 640:
                            album_art_url = album_art['url']
                    song_title = sp.track(url)['name']
                    album = sp.track(url)['album']['name']
                    length_in_seconds = int(sp.track(url)['duration_ms']/1000)

                    if (length_in_seconds > 900):
                        await interaction.followup.send(embed=discord.Embed(title="You cannot put songs that are longer than 15 minutes!", color=0xff0000), ephemeral=True)
                    else:      
                        db.update_db("INSERT INTO bot_user_song_library(user_id, artist, song_title, album, length_in_seconds) VALUES (?, ?, ?, ?, ?)", user_id, artists, song_title, album, length_in_seconds)
                        
                        successful_embed = discord.Embed(title="Song successfully added to queue!", color=0x00aeff)
                        successful_embed.set_thumbnail(url=album_art_url)
                        successful_embed.add_field(name="Song title", value=song_title, inline=True)
                        successful_embed.add_field(name="Artist(s)", value=artists, inline=True)
                        successful_embed.add_field(name="Album", value=album, inline=False)
                        await interaction.followup.send(embed=successful_embed)
                except spotipy.exceptions.SpotifyException as err:
                    description = ""
                    match err.http_status:
                        case 400:
                            description = "Invalid track ID (" + str(err.http_status) + ")"
                        case 403:
                            description = "Forbidden (" + str(err.http_status) + ")."
                        case 404:
                            description = "Track was not found (" + str(err.http_status) + ")"
                        case 429:
                            description = "Rate limit exceeded (" + str(err.http_status) + "), wait a few minutes and try again. If you see this again, please contact <@171000921927581696>!"
                        case 500:
                            description = "Internal server error (" + str(err.http_status) + "). That's on Spotify's side, sorry :("
                        case 502:
                            description = "Bad Gateway (" + str(err.http_status) + "). That's on Spotify's side, sorry :("
                        case _:
                            description = "An error has occurred (" + str(err.http_status) + "). If you see this, please contact <@171000921927581696>!"
                    await interaction.followup.send(embed=discord.Embed(title="An error has occurred while retrieving the song", description=description, color=0xff0000), ephemeral=True)
                    raise
            else:
                await interaction.followup.send(embed=discord.Embed(title="URL is invalid!", description="Make sure to only use a correct Spotify link and only single tracks (no playlists or albums!)", color=0xff0000), ephemeral=True)
        except:
            await embeds.error_executing_command(interaction)
            raise

    @app_commands.command(name="check_presence_queue", description="Displays the queued songs for display on presence")
    @app_commands.describe(archive="Shows the list of songs that were already played by the bot (False by default)")
    @app_commands.checks.has_permissions(administrator=True)
    async def check_presence_queue(self, interaction: discord.Interaction, archive: bool = False):
        try:
            await interaction.response.defer()
            start = 0
            limit = 10
            view = NextPreviousButtons(start=start, limit=limit, archive=archive)
            if archive == True:
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(start) + ", " + str(limit))
                title = "Archived songs:"
            else:
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(start) + ", " + str(limit))
                title = "Songs in queue:"
            
            if not songs_in_queue == []:
                queue_embed=discord.Embed(title=title, color=0x00aeff)
                if archive == True:
                    for song in songs_in_queue:
                        timestamp = str(int(datetime.strptime(str(song[6]), "%Y-%m-%d %H:%M:%S").timestamp()))
                        queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">\nPlayed on <t:" + timestamp + ":D> - <t:" + timestamp + ":T>", inline=False)
                else:
                    for song in songs_in_queue:
                        queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">", inline=False)
                await interaction.followup.send(embed=queue_embed, ephemeral=True, view=view)
            else:
                await interaction.followup.send(embed=discord.Embed(title="Currently no songs in queue", color=0x00aeff), ephemeral=True)
        except:
            await embeds.error_executing_command(interaction)
            raise
    
    @app_commands.command(name="delete_song_from_presence_queue", description="Removes a song from the queue")
    @app_commands.describe(id="Song ID to be removed (the song number when you do /check_presence_queue)")
    @app_commands.checks.has_permissions(administrator=True)
    async def delete_song_from_presence_queue(self, interaction: discord.Interaction, id: int):
        try:
            await interaction.response.defer()
            db.update_db("DELETE FROM bot_user_song_library WHERE id = ?", id)
            await interaction.followup.send(embed=discord.Embed(title="Song successfully deleted!", color=0x00aeff), ephemeral=True)
        except:
            await interaction.followup.send(embed=discord.Embed(title="Error while deleting the song!", description="(You've probably entered a invalid song ID)", color=0xff0000), ephemeral=True)
    
    @app_commands.command(name="interrupt_current_song", description="Temporarily stops the currently playing song")
    @app_commands.checks.has_permissions(administrator=True)
    async def interrupt_current_song(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            await self.bot.change_presence(activity=None)
            await interaction.followup.send(embed=discord.Embed(title="Song successfully stopped!", color=0x00aeff), ephemeral=True)
        except:
            await embeds.error_executing_command(interaction)
            raise

    @rebuild_song_library.error
    @check_presence_queue.error
    @delete_song_from_presence_queue.error
    @interrupt_current_song.error
    async def error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await embeds.missing_permissions(interaction)

#honestly the code in this class is catastrophic lol but changing button.disabled doesn't work properly for some reason so it doesn't help
class NextPreviousButtons(discord.ui.View):
    def __init__(self, *, timeout=300, start, limit, archive):
        super().__init__(timeout=timeout)
        self.start = start
        self.limit = limit
        self.archive = archive
        self.children[0].disabled = True
        if archive == True:
            if len(db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(start) + ", " + str(limit+1))) < 11:
                self.children[1].disabled = True
        else:
            if len(db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(start) + ", " + str(limit+1))) < 11:
                self.children[1].disabled = True

    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji='⬅️')
    async def previous(self, interaction:discord.Interaction, button:discord.ui.Button):
        try:
            self.start -= 10
            if self.start == 0:
                self.children[0].disabled = True
            else:
                self.children[0].disabled = False
            if self.archive == True:
                if len(db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit+1))) < 11:
                    self.children[1].disabled = True
                else:
                    self.children[1].disabled = False
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit))
                title = "Archived songs:"
            else:
                if len(db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit+1))) < 11:
                    self.children[1].disabled = True
                else:
                    self.children[1].disabled = False
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit))
                title = "Songs in queue:"
                
            queue_embed=discord.Embed(title=title, color=0x00aeff)
            if self.archive == True:
                for song in songs_in_queue:
                    timestamp = str(int(datetime.strptime(str(song[6]), "%Y-%m-%d %H:%M:%S").timestamp()))
                    queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">\nPlayed on <t:" + timestamp + ":D> - <t:" + timestamp + ":T>", inline=False)
            else:
                for song in songs_in_queue:
                    queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">", inline=False)
            await interaction.followup.edit(embed=queue_embed, view=self)
        except:
            await embeds.error_executing_command(interaction, edit=True)
            raise
    
    @discord.ui.button(style=discord.ButtonStyle.blurple, emoji='➡️')
    async def next(self, interaction:discord.Interaction, button:discord.ui.Button):
        try:
            self.start += 10
            self.children[0].disabled = False
            if self.archive == True:
                if len(db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit+1))) < 11:
                    self.children[1].disabled = True
                else:
                    self.children[0].disabled = False
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library_archive ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit))
                title = "Archived songs:"
            if self.archive == False:
                if len(db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit+1))) < 11:
                    self.children[1].disabled = True
                else:
                    self.children[0].disabled = False
                songs_in_queue = db.fetchall("SELECT * FROM bot_user_song_library ORDER BY id ASC LIMIT " + str(self.start) + ", " + str(self.limit))
                title = "Songs in queue:"

            queue_embed=discord.Embed(title=title, color=0x00aeff)
            if self.archive == True:
                for song in songs_in_queue:
                    timestamp = str(int(datetime.strptime(str(song[6]), "%Y-%m-%d %H:%M:%S").timestamp()))
                    queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">\nPlayed on <t:" + timestamp + ":D> - <t:" + timestamp + ":T>", inline=False)
            else:
                for song in songs_in_queue:
                    queue_embed.add_field(name="Song " + str(song[0]), value="**" + song[3] + "** by " + song[2] + "\nAdded by <@" + song[1] + ">", inline=False)
            await interaction.followup.edit(embed=queue_embed, view=self)
        except:
            await embeds.error_executing_command(interaction, edit=True)
            raise
            
async def setup(bot: commands.Bot):
    await bot.add_cog(SongLibraryCog(bot))