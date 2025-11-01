import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

# TOKEN değerini al
token = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Sync error: {e}")

@bot.tree.command(name="roulette", description="Play Russian Roulette with a role. 1/{chance} members will be kicked.")
@app_commands.describe(role="The role to play with", chance="The 1/x chance for each member")
async def roulette(interaction: discord.Interaction, role: discord.Role, chance: int):
    await interaction.response.defer(ephemeral=False)
    interaction.response.send_message("The bullets are being loaded...", ephemeral=True)
    if chance < 2:
        await interaction.followup.send("Chance must be at least 2.", ephemeral=True)
        return

    members = [m for m in role.members if not m.bot]

    if not members:
        await interaction.followup.send("No non-bot members found in that role.", ephemeral=True)
        return

    unlucky = [m for m in members if random.randint(1, chance) == 1]

    if not unlucky:
        await interaction.followup.send(f"🎲 No one was kicked this time! Lucky!", ephemeral=False)
        return

    kicked = []
    failed = []

    for m in unlucky:
        try:
            await m.kick(reason="Lost the Russian roulette")
            kicked.append(m)
        except Exception as e:
            print(f"Failed to kick {m}: {e}")
            failed.append(m)

    msg = f"💀 {len(kicked)} member(s) were kicked from {role.mention}.\n"
    if kicked:
        msg += "**Kicked:** " + ", ".join([m.mention for m in kicked]) + "\n"
    if failed:
        msg += "**Failed:** " + ", ".join([m.mention for m in failed])

    await interaction.followup.send(msg)

bot.run(token)
