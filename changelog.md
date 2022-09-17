# previous versions
the changelog for previous versions of the bot is available here: https://github.com/kyllian1212/Rin/blob/master/changelog.md

------------------------------------------------------------------------
# v1.0.0 - xx/09/2022

## **huge bot changes**
* pretty much the entire bot has been rewritten from the ground up! with discord.py being updated to 2.0.0, it means the bot finally supports slash commands and other cool new things.
* the bot now has a sqlite database, which should help a lot in writing new features and having more flexibility/readability in the code. it will also allow the bot to finally support multiple servers instead of just the porter robinson discord
* the bot has been split into multiple files for easier code readability.

## **slash commands!!**
* the following commands are now slash commands:
  * !!info > /info
  * !!fiftyfifty > /fiftyfifty
  * !!roll > /roll
  * !!october_18 > /october_18
* !!say and !!saytts are still normal commands however and wont be slash commands

## **new features**
* **/set_archive_channel, /archive and /unarchive**: allows the bot to archive channels automatically! including moving it to the category of your choice and setting the appropriate role permissions.
* **/rin_timeout, /rin_kick and /rin_ban**: allows the bot to timeout, kick, ban someone and dm them (or not) the reason. 
* **/add_song_to_presence_queue**: you can now add songs to the "presence queue"! its the song that will be displayed as Rin's presence (Listening to `song`). she will have a default list of songs from now on that she'll go through randomly, and whenever someone adds songs to the queue she'll switch to those after the previous one is finished until there are no more songs in the queue. this is currently only possible with spotify links but i'll look into having other streaming platforms be supported
* **/rebuild_database**: this one is less important but if there's any issue with the bot's database or an update, this will destroy the entire database and rebuild it from scratch (which means all data in the database will be erased)
* maybe the pronouns stuff for this version too we'll see (placeholder)

## **reporting messages**
* **/set_log_channel:** will set which channel the reported messages will go to in the server you're in.
* the report function deleting messages will now depend on if you have the "Administrator" or "Manage Messages" permissions instead of depending on a specific role.
* changed the reaction listener from `on_reaction_add` to `on_raw_reaction_add`, which means every message, no matter when it has been sent, is now able to be reported.
* added message creation date/time to the report
* the displayed report date/time should now adapt depending on which timezone you're in

## **default song library**
* added 3 songs in the default song library:
  * The Prince by Madeon
  * Love You Back by Madeon
  * Everything Goes On by Porter Robinson

## **other cool things**
* added a temporary countdown for second sky 2022 (this is specifically for PRD)