import discord
import requests
import shutil
import os, sys

def token():
    TOKEN_FILE = sys.path[0]+"/auth/discordToken"
    fname = open(TOKEN_FILE)
    token = fname.read()
    return token


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))
        secret_passphrase = "wah"
        if message.content == secret_passphrase:# and message.author.id == 224020595103236096:

            await message.channel.send("no u")
            '''
            atts = 0
            embs = 0

            async for msg in message.channel.history(limit=1000):
                atts += len(msg.attachments)
                embs += len(msg.embeds)
                print("Attachments ({}), Embeds({})".format(len(msg.attachments), len(msg.embeds)))
                for embed in msg.embeds:
                    print(embed.url)
                for att in msg.attachments:
                    print(att.url)
                    download_image(att.url,str(message.channel.id),str(msg.id))
            print("Attachments ({}), Embeds({})".format(atts, embs))
            '''