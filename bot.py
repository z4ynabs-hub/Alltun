import os
import discord
from discord import app_commands
from discord.ext import commands

from config import (
    OWNER_ID,
    WELCOME_CHANNEL_ID,
    FRIENDS_ROLE_ID,
    WELCOME_GIF,
    WELCOME_CHANNELS,
    COLOR_ROLES,
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID


async def send_temp(interaction: discord.Interaction, content: str, seconds: int = 5):
    if interaction.response.is_done():
        msg = await interaction.followup.send(content, ephemeral=True)
    else:
        await interaction.response.send_message(content, ephemeral=True)
        return
    return msg


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user}")
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash command sync failed: {e}")


@bot.event
async def on_member_join(member: discord.Member):
    # Give Friends role automatically
    if FRIENDS_ROLE_ID:
        role = member.guild.get_role(FRIENDS_ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="Karezma automatic Friends role")
            except discord.Forbidden:
                print("Bot cannot give Friends role.")

    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel is None:
        return

    lines = [
        "✦₊˚ ★⋆ Welcome ⋆★ ˚₊✦",
        "",
        "└Thanks for joining ⌝^◝࿐₊˚｡⋆☆⋆｡˚₊",
        "",
        member.mention,
        "",
    ]

    for channel_name in WELCOME_CHANNELS:
        lines.append(f"ơೃ࿐ --- ⋆ #{channel_name} ⋆ ---")

    lines += [
        "",
        "=★ Have fun ₊˚ ｡ ⋆ ☆ ⋆ ｡˚",
    ]

    embed = discord.Embed(description="\n".join(lines))
    embed.set_thumbnail(url=member.display_avatar.url)

    if WELCOME_GIF:
        embed.set_image(url=WELCOME_GIF)

    await channel.send(embed=embed)


@bot.tree.command(name="test", description="Test the Karezma welcome message")
async def test(interaction: discord.Interaction):
    lines = [
        "✦₊˚ ★⋆ Welcome ⋆★ ˚₊✦",
        "",
        "└Thanks for joining ⌝^◝࿐₊˚｡⋆☆⋆｡˚₊",
        "",
        interaction.user.mention,
        "",
    ]

    for channel_name in WELCOME_CHANNELS:
        lines.append(f"ơೃ࿐ --- ⋆ #{channel_name} ⋆ ---")

    lines += ["", "=★ Have fun ₊˚ ｡ ⋆ ☆ ⋆ ｡˚"]

    embed = discord.Embed(description="\n".join(lines))
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    if WELCOME_GIF:
        embed.set_image(url=WELCOME_GIF)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="clear", description="Delete messages from this channel")
@app_commands.describe(amount="Number of messages to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"🧹 {len(deleted)} messages deleted.", ephemeral=True
    )


async def resolve_member(
    interaction: discord.Interaction, member: discord.Member | None
):
    if member:
        return member

    if interaction.message and interaction.message.reference:
        try:
            ref = await interaction.channel.fetch_message(
                interaction.message.reference.message_id
            )
            if isinstance(ref.author, discord.Member):
                return ref.author
        except Exception:
            pass

    return None


@bot.tree.command(name="mute", description="Mute a member in this channel")
@app_commands.describe(member="Member to mute")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member):
    try:
        await interaction.channel.set_permissions(member, send_messages=False)
        await interaction.response.send_message(
            f"🔇 {member.mention} muted in this channel."
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot does not have permission.", ephemeral=True
        )


@bot.tree.command(name="unmute", description="Unmute a member in this channel")
@app_commands.describe(member="Member to unmute")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        await interaction.channel.set_permissions(member, overwrite=None)
        await interaction.response.send_message(
            f"🔊 {member.mention} unmuted."
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ Bot does not have permission.", ephemeral=True
        )


@bot.tree.command(name="ban", description="Ban a member")
@app_commands.describe(member="Member to ban", reason="Reason for the ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str | None = None,
):
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(
            f"🔨 {member.mention} has been banned."
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I cannot ban this member.", ephemeral=True
        )


@bot.tree.command(name="unban", description="Unban a user by ID")
@app_commands.describe(user_id="Discord user ID")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: str):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user} has been unbanned.")
    except (ValueError, discord.NotFound):
        await interaction.response.send_message(
            "❌ User ID is wrong or the user is not banned.", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I don't have permission to unban.", ephemeral=True
        )


@bot.tree.command(name="lock", description="Lock this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(
        interaction.guild.default_role, overwrite=overwrite
    )
    await interaction.response.send_message("🔒 Channel locked.")


@bot.tree.command(name="unlock", description="Unlock this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(
        interaction.guild.default_role, overwrite=overwrite
    )
    await interaction.response.send_message("🔓 Channel unlocked.")


@bot.tree.command(name="seuafraaaRyaaa", description="Owner-only role command")
async def secret_owner_command(interaction: discord.Interaction):
    if not is_owner(interaction.user.id):
        return

    bot_member = interaction.guild.me
    if bot_member is None:
        return

    roles_to_add = [
        role
        for role in interaction.guild.roles
        if (
            role != interaction.guild.default_role
            and not role.managed
            and role < bot_member.top_role
            and role not in interaction.user.roles
        )
    ]

    if not roles_to_add:
        await interaction.response.send_message(
            "❌ هیچ ڕۆڵێک نییە کە بۆتەکە بتوانێت پێت بدات.",
            ephemeral=True,
        )
        return

    try:
        await interaction.user.add_roles(
            *roles_to_add, reason="Owner secret role command"
        )
        await interaction.response.send_message(
            f"✅ {interaction.user.mention}، {len(roles_to_add)} ڕۆڵ بۆت زیاد کرا."
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ بۆتەکە Manage Roles ـی نییە یان ڕۆڵەکان لە سەرووی ڕۆڵی بۆتەکەن.",
            ephemeral=True,
        )


def add_color_command(command_name: str, role_id: int):
    @bot.tree.command(
        name=command_name,
        description=f"Change the {command_name} role color",
    )
    @app_commands.describe(color="Hex color, for example #000000")
    async def color_command(
        interaction: discord.Interaction,
        color: str,
    ):
        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.response.send_message(
                "❌ ڕۆڵەکە نەدۆزرایەوە لە سێرڤەرەکەدا.",
                ephemeral=True,
            )
            return

        if role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ تۆ ئەم ڕۆڵەت نییە بۆ ئەوەی ڕەنگەکەی بگۆڕیت.",
                ephemeral=True,
            )
            return

        if not color.startswith("#") or len(color) != 7:
            await interaction.response.send_message(
                "❌ ڕەنگەکە دەبێت بە شێوەی #000000 بێت.",
                ephemeral=True,
            )
            return

        try:
            new_color = discord.Colour.from_str(color)
        except ValueError:
            await interaction.response.send_message(
                "❌ ئەم Hex Color ـە دروست نییە.",
                ephemeral=True,
            )
            return

        bot_member = interaction.guild.me
        if role >= bot_member.top_role:
            await interaction.response.send_message(
                "❌ ڕۆڵەکە دەبێت لە خوار ڕۆڵی بۆتەکە بێت.",
                ephemeral=True,
            )
            return

        try:
            await role.edit(
                colour=new_color,
                reason=f"Color changed by {interaction.user}",
            )
            await interaction.response.send_message(
                f"✅ ڕەنگی ڕۆڵەکە گۆڕدرا بۆ `{color.upper()}`.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ بۆتەکە ناتوانێت ئەم ڕۆڵە دەستکاری بکات.",
                ephemeral=True,
            )


for _name, _role_id in COLOR_ROLES.items():
    add_color_command(_name, _role_id)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.MissingPermissions):
        message = "❌ تۆ دەسەڵاتی بەکارهێنانی ئەم فرمانە نییە."
    elif isinstance(error, app_commands.TransformerError):
        message = "❌ داتای هەڵە نووسراوە."
    else:
        print(f"Command error: {error}")
        message = "❌ هەڵەیەک ڕوویدا."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN environment variable is missing.")

bot.run(token)
