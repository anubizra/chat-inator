Live Streaming Chat Bot for YouTube and Twitch managed through Discord
===

Accounts Setup and Configuration
---

**Discord Bot**
- Follow the steps in this tutorial to setup and register a discord bot with your
Discord server. `https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token`
- Once complete you will need to copy the `Token` you generated and paste it into
the `config.json` file as the value for `DiscordBotToken`

**YouTube Live Chat Bot**

This is the account that will write messages to your YouTube Live Chat (Bot)
- Create a Google account for the bot
- Navigate to: https://console.developers.google.com/apis/credentials
- Create an OAuth Client ID for your bot
- Download the client_secret.json and place it in the Config folder
- In the `config.json` file make sure `ClientSecret` value points to `Config/client_secret.json` or 
whatever the name of the file you downloaded was.

**Twitch Live Chat Bot**

This is the account that will write messages to your Twitch Chat
- Navigate to `https://twitchapps.com/tmi/`
- Use the `Connect to Twitch` button and authorize using your Twitch Streamer account
- Copy the returned oauth string. ie: `oauth:<token>`
- Open the config.json file in the root of this project
- Paste the oauth token into the "OAuthToken" field.
- Set the `Nickname` and `Channel` values to your Twitch username in all lowercase

Setup
---
Install the following python packages:
- google-api-python-client
- discord.py

Packages can be installed at the commandline using pip:

`pip install -U <package-name>`

ie: 

```
pip install -U google-api-python-client
pip install -U discord.py
```

Start the Chat Bot
---
Execute the bot at the command line using the following command:
```
python bot.py
```
You should see something like the following if everything started up:
```
Discord Worker Started | Logged in as <botname> (<botid>)
```

Discord Chat Bot Commands
-

**COMMAND: blah**

The `blah` command is strictly a test command that you can use to make sure the bot is listening 
in discord.
```
!blah <text>
```
Example
```
!blah hello
```
Response
```
bot:hello
```
**COMMAND: connect**

The connect command will allow you to attach the bot to either YouTube, Twitch, or Both.
```
!connect <service>
```
Example
```
!connect twitch
!connect youtube
```
Response
```
Connecting to TWITCH Chat Service...
Connecting to YOUTUBE Chat Service...
```
*note: the first time you connect to YouTube you will asked to authorize both your YouTube streamer
account and your YouTube bot account. A web browser window will be opened asking for authorization
to YouTube.
- The first autorization will be for your YouTube Streamer account. The one you stream as.
- The second authorization will be for the YouTube Bot account you setup ealier in the 
`YouTube Live Chat Bot` section

You should only have to do this once. Watch the command window you have the bot.py python program 
running in for errors. Once complete you should have two new files in the root folder of the program.
- YouTuber-oauth2.json
- Bot-oauth2.json

If you want to change the accounts you use or just remove access to the bot for YouTube just delete 
these files and the next time you run the `!connect youtube` command you will need to go threw 
the process again.

For Twitch all the connection settings are in the `config.json` you setup earlier.

**COMMAND: send**

Once you have connected to Twitch, YouTube, or both you can send messages the connected chats using
the `!send` command.
```
!send <message>
```

Example
```
!send What do you think you're doing!?
```
You should see this message appear in the chat for the services you have connected.

Chat Bot Relay
---
With the bot connected to Twitch, YouTube, or both the bot will act as a relay between the connected 
services and discord.
- If someone on Twitch posts a message you should see it appear in Discord and YouTube
- If someone on YouTube posts a message you should see it appear in Discord and Twitch
- To send a message to both chats youself, use the Discord `!send` command