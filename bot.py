# bot.py - Main bot file with whitelist features
import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
from google.cloud import translate_v2 as translate
from google.cloud import vision
import google.generativeai as genai
import asyncio
from datetime import datetime, time, timezone
import pytz
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import aiohttp
import re

# Import pattern detector
from pattern_detector import PatternDetector

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize APIs
translate_client = translate.Client()
vision_client = vision.ImageAnnotatorClient()

# Initialize pattern detector
detector = PatternDetector()

# Configuration files
CONFIG_FILE = "config.json"
SLURS_FILE = "slur_patterns.json"
LOGS_FILE = "violation_logs.json"
STATS_FILE = "daily_stats.json"
WHITELIST_FILE = "whitelist.json"

config = {
    "enabled": False,
    "monitored_channel_id": None,
    "log_channel_id": None,
    "gemini_api_keys": [],
    "current_key_index": 0
}

slur_patterns = []
violation_logs = []
whitelist = {
    "users": [],
    "roles": []
}

daily_stats = {
    "messages_scanned": 0,
    "messages_flagged": 0,
    "users_caught": set(),
    "hourly_scans": defaultdict(int),
    "date": str(datetime.now().date())
}

def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            if "gemini_api_keys" not in config:
                config["gemini_api_keys"] = []
            if "current_key_index" not in config:
                config["current_key_index"] = 0

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_slur_patterns():
    global slur_patterns
    patterns = []
    if os.path.exists(SLURS_FILE):
        try:
            with open(SLURS_FILE, 'r') as f:
                data = json.load(f)
            
            # Combine all categories
            for category, words in data.items():
                if not category.startswith('_'):
                    patterns.extend([w for w in words if not w.startswith('_')])
            
            slur_patterns = patterns
            print(f"Loaded {len(slur_patterns)} patterns from database")
        except Exception as e:
            print(f"Error loading patterns: {e}")
            slur_patterns = []
    else:
        print(f"Warning: {SLURS_FILE} not found")
        slur_patterns = []

def load_whitelist():
    global whitelist
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, 'r') as f:
            whitelist = json.load(f)
            if "users" not in whitelist:
                whitelist["users"] = []
            if "roles" not in whitelist:
                whitelist["roles"] = []
    else:
        whitelist = {"users": [], "roles": []}

def save_whitelist():
    with open(WHITELIST_FILE, 'w') as f:
        json.dump(whitelist, f, indent=4)

def is_whitelisted(user: discord.Member) -> bool:
    """Check if user is whitelisted"""
    # Check user whitelist
    if user.id in whitelist["users"]:
        return True
    
    # Check role whitelist
    user_role_ids = [role.id for role in user.roles]
    for role_id in whitelist["roles"]:
        if role_id in user_role_ids:
            return True
    
    return False

def load_logs():
    global violation_logs
    if os.path.exists(LOGS_FILE):
        with open(LOGS_FILE, 'r') as f:
            violation_logs = json.load(f)

def save_logs():
    with open(LOGS_FILE, 'w') as f:
        json.dump(violation_logs, f, indent=4)

def load_stats():
    global daily_stats
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            data = json.load(f)
            data["users_caught"] = set(data.get("users_caught", []))
            if data.get("date") != str(datetime.now().date()):
                daily_stats = {
                    "messages_scanned": 0,
                    "messages_flagged": 0,
                    "users_caught": set(),
                    "hourly_scans": defaultdict(int),
                    "date": str(datetime.now().date())
                }
            else:
                daily_stats = data
                daily_stats["hourly_scans"] = defaultdict(int, data.get("hourly_scans", {}))

def save_stats():
    stats_to_save = daily_stats.copy()
    stats_to_save["users_caught"] = list(daily_stats["users_caught"])
    with open(STATS_FILE, 'w') as f:
        json.dump(stats_to_save, f, indent=4)

def get_current_gemini_model():
    if not config["gemini_api_keys"]:
        return None
    current_key = config["gemini_api_keys"][config["current_key_index"]]
    genai.configure(api_key=current_key)
    return genai.GenerativeModel('gemini-pro')

def rotate_api_key():
    if len(config["gemini_api_keys"]) <= 1:
        return False
    config["current_key_index"] = (config["current_key_index"] + 1) % len(config["gemini_api_keys"])
    save_config()
    print(f"Rotated to API key #{config['current_key_index'] + 1}")
    return True

def contains_slur(text):
    """Enhanced slur detection with pattern matching"""
    found, matches = detector.check_text(text, slur_patterns)
    if found:
        return True, matches
    
    # Also check normalized text
    normalized = detector.normalize_text(text)
    found_norm, matches_norm = detector.check_text(normalized, slur_patterns)
    return found_norm, matches_norm

async def check_with_gemini(text):
    max_retries = len(config["gemini_api_keys"]) if config["gemini_api_keys"] else 1
    
    for attempt in range(max_retries):
        try:
            gemini_model = get_current_gemini_model()
            if not gemini_model:
                return {"is_harmful": False, "severity": "unknown", "categories": [], "reason": "No API keys configured"}
            
            prompt = f"""Analyze this message for harmful content. Check for:
1. Death threats or threats of violence
2. Terrorist content or extremist rhetoric
3. Hate speech or severe harassment
4. Incitement to violence
5. Doxxing or sharing personal information maliciously
6. Slurs or discriminatory language

Message: "{text}"

Respond in JSON format:
{{
    "is_harmful": true/false,
    "severity": "low/medium/high/critical",
    "categories": ["list of applicable categories"],
    "reason": "brief explanation"
}}"""

            response = gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "quota" in error_msg or "rate limit" in error_msg:
                print(f"API key #{config['current_key_index'] + 1} rate limited. Rotating...")
                if rotate_api_key():
                    continue
                else:
                    return {"is_harmful": False, "severity": "unknown", "categories": [], "reason": "All API keys rate limited"}
            else:
                print(f"Gemini API error: {e}")
                return {"is_harmful": False, "severity": "unknown", "categories": [], "reason": f"API error: {e}"}
    
    return {"is_harmful": False, "severity": "unknown", "categories": [], "reason": "All API keys exhausted"}

async def translate_text(text, target_lang='en'):
    try:
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        result = translate_client.translate(text, target_language=target_lang)
        return result['translatedText'], result['detectedSourceLanguage']
    except Exception as e:
        print(f"Translation error: {e}")
        return text, 'unknown'

async def ocr_image(image_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return None
                image_data = await resp.read()
        
        image = vision.Image(content=image_data)
        response = vision_client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(response.error.message)
        
        texts = response.text_annotations
        if texts:
            return texts[0].description
        return None
        
    except Exception as e:
        print(f"OCR error: {e}")
        return None

async def log_violation(message, reason, translated_text, gemini_result=None, ocr_text=None):
    violation = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": message.author.id,
        "user_name": str(message.author),
        "channel_id": message.channel.id,
        "channel_name": message.channel.name,
        "message_content": message.content,
        "translated_text": translated_text,
        "ocr_text": ocr_text,
        "reason": reason,
        "gemini_analysis": gemini_result,
        "attachments": [att.url for att in message.attachments]
    }
    
    violation_logs.append(violation)
    save_logs()
    
    daily_stats["messages_flagged"] += 1
    daily_stats["users_caught"].add(message.author.id)
    save_stats()
    
    if not config.get("log_channel_id"):
        return
    
    log_channel = bot.get_channel(config["log_channel_id"])
    if not log_channel:
        return
    
    embed = discord.Embed(
        title="🚨 Potential Violation Detected",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="User", value=f"{message.author.mention} ({message.author.id})", inline=False)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=True)
    
    if message.content:
        original_content = message.content[:1000] if len(message.content) <= 1000 else message.content[:1000] + "..."
        embed.add_field(name="Original Message", value=f"```{original_content}```", inline=False)
    
    if translated_text and translated_text != message.content:
        translated_preview = translated_text[:1000] if len(translated_text) <= 1000 else translated_text[:1000] + "..."
        embed.add_field(name="Translated (English)", value=f"```{translated_preview}```", inline=False)
    
    if ocr_text:
        ocr_preview = ocr_text[:1000] if len(ocr_text) <= 1000 else ocr_text[:1000] + "..."
        embed.add_field(name="Text from Image (OCR)", value=f"```{ocr_preview}```", inline=False)
    
    if gemini_result and gemini_result.get("is_harmful"):
        embed.add_field(
            name="AI Analysis", 
            value=f"**Severity:** {gemini_result.get('severity', 'unknown')}\n**Categories:** {', '.join(gemini_result.get('categories', []))}\n**Reason:** {gemini_result.get('reason', 'N/A')}", 
            inline=False
        )
    
    if message.attachments:
        embed.add_field(name="Attachments", value="\n".join([att.url for att in message.attachments]), inline=False)
        for att in message.attachments:
            if att.content_type and att.content_type.startswith('image'):
                embed.set_thumbnail(url=att.url)
                break
    
    embed.add_field(name="Action Required", value="⚠️ Please review and take appropriate action", inline=False)
    embed.set_footer(text=f"User ID: {message.author.id}")
    
    await log_channel.send(embed=embed)

async def generate_daily_report():
    if not config.get("log_channel_id"):
        return
    
    log_channel = bot.get_channel(config["log_channel_id"])
    if not log_channel:
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Daily Moderation Report - {daily_stats["date"]}', fontsize=16, fontweight='bold')
    
    categories = ['Messages\nScanned', 'Messages\nFlagged', 'Unique\nUsers']
    values = [
        daily_stats["messages_scanned"],
        daily_stats["messages_flagged"],
        len(daily_stats["users_caught"])
    ]
    colors = ['#5865F2', '#ED4245', '#FEE75C']
    ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=1.5)
    ax1.set_title('Overall Statistics', fontweight='bold')
    ax1.set_ylabel('Count')
    for i, v in enumerate(values):
        ax1.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')
    
    hours = list(range(24))
    scans_per_hour = [daily_stats["hourly_scans"].get(str(h), 0) for h in hours]
    ax2.plot(hours, scans_per_hour, marker='o', linewidth=2, markersize=6, color='#5865F2')
    ax2.fill_between(hours, scans_per_hour, alpha=0.3, color='#5865F2')
    ax2.set_title('Messages Scanned Per Hour', fontweight='bold')
    ax2.set_xlabel('Hour (24h format)')
    ax2.set_ylabel('Messages Scanned')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(range(0, 24, 2))
    
    if daily_stats["messages_scanned"] > 0:
        clean = daily_stats["messages_scanned"] - daily_stats["messages_flagged"]
        flagged = daily_stats["messages_flagged"]
        sizes = [clean, flagged]
        labels = [f'Clean\n({clean})', f'Flagged\n({flagged})']
        colors_pie = ['#57F287', '#ED4245']
        explode = (0, 0.1)
        ax3.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', 
                startangle=90, explode=explode, textprops={'fontweight': 'bold'})
        ax3.set_title('Clean vs Flagged Messages', fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'No data yet', ha='center', va='center', fontsize=12)
        ax3.set_title('Clean vs Flagged Messages', fontweight='bold')
    
    ax4.axis('off')
    summary_text = f"""
    📊 DAILY SUMMARY
    ━━━━━━━━━━━━━━━━━━━━━━━━━
    
    📨 Total Messages Scanned: {daily_stats["messages_scanned"]}
    
    🚨 Messages Flagged: {daily_stats["messages_flagged"]}
    
    👥 Unique Users Caught: {len(daily_stats["users_caught"])}
    
    📈 Flag Rate: {(daily_stats["messages_flagged"] / daily_stats["messages_scanned"] * 100) if daily_stats["messages_scanned"] > 0 else 0:.2f}%
    
    ⏰ Peak Hour: {max(daily_stats["hourly_scans"].items(), key=lambda x: x[1])[0] if daily_stats["hourly_scans"] else "N/A"}:00
    
    🔑 API Key: #{config["current_key_index"] + 1} of {len(config["gemini_api_keys"])}
    
    👤 Whitelisted Users: {len(whitelist["users"])}
    👥 Whitelisted Roles: {len(whitelist["roles"])}
    """
    ax4.text(0.1, 0.9, summary_text, fontsize=11, verticalalignment='top', 
             family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
    buffer.seek(0)
    plt.close()
    
    file = discord.File(buffer, filename='daily_report.png')
    embed = discord.Embed(
        title="📊 Daily Moderation Report",
        description=f"Report for **{daily_stats['date']}**",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    embed.set_image(url="attachment://daily_report.png")
    embed.set_footer(text="Next report in 24 hours")
    
    await log_channel.send(embed=embed, file=file)
    
    daily_stats["messages_scanned"] = 0
    daily_stats["messages_flagged"] = 0
    daily_stats["users_caught"] = set()
    daily_stats["hourly_scans"] = defaultdict(int)
    daily_stats["date"] = str(datetime.now().date())
    save_stats()

@tasks.loop(time=time(hour=5, minute=0, tzinfo=pytz.timezone('US/Eastern')))
async def daily_report_task():
    await generate_daily_report()

@bot.event
async def on_ready():
    load_config()
    load_slur_patterns()
    load_logs()
    load_stats()
    load_whitelist()
    await bot.tree.sync()
    daily_report_task.start()
    print(f'{bot.user} has connected to Discord!')
    print(f'Loaded {len(slur_patterns)} patterns from database')
    print(f'Loaded {len(violation_logs)} violation logs')
    print(f'Whitelisted users: {len(whitelist["users"])}, roles: {len(whitelist["roles"])}')
    print(f'Monitoring enabled: {config["enabled"]}')
    print(f'Active API keys: {len(config["gemini_api_keys"])}')

# Whitelist commands
@bot.tree.command(name="whitelist_user", description="Add a user to the whitelist")
@app_commands.describe(user="The user to whitelist")
async def whitelist_user(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if user.id in whitelist["users"]:
        await interaction.response.send_message(f"⚠️ {user.mention} is already whitelisted.", ephemeral=True)
        return
    
    whitelist["users"].append(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Added {user.mention} to whitelist. They will bypass all filters.", ephemeral=True)

@bot.tree.command(name="unwhitelist_user", description="Remove a user from the whitelist")
@app_commands.describe(user="The user to remove from whitelist")
async def unwhitelist_user(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if user.id not in whitelist["users"]:
        await interaction.response.send_message(f"⚠️ {user.mention} is not whitelisted.", ephemeral=True)
        return
    
    whitelist["users"].remove(user.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Removed {user.mention} from whitelist.", ephemeral=True)

@bot.tree.command(name="whitelist_role", description="Add a role to the whitelist")
@app_commands.describe(role="The role to whitelist")
async def whitelist_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if role.id in whitelist["roles"]:
        await interaction.response.send_message(f"⚠️ {role.mention} is already whitelisted.", ephemeral=True)
        return
    
    whitelist["roles"].append(role.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Added {role.mention} to whitelist. All members with this role will bypass filters.", ephemeral=True)

@bot.tree.command(name="unwhitelist_role", description="Remove a role from the whitelist")
@app_commands.describe(role="The role to remove from whitelist")
async def unwhitelist_role(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if role.id not in whitelist["roles"]:
        await interaction.response.send_message(f"⚠️ {role.mention} is not whitelisted.", ephemeral=True)
        return
    
    whitelist["roles"].remove(role.id)
    save_whitelist()
    await interaction.response.send_message(f"✅ Removed {role.mention} from whitelist.", ephemeral=True)

@bot.tree.command(name="whitelist_list", description="View all whitelisted users and roles")
async def whitelist_list(interaction: discord.Interaction):
    embed = discord.Embed(title="⚪ Whitelist", color=discord.Color.blue())
    
    # Users
    if whitelist["users"]:
        users_text = []
        for user_id in whitelist["users"]:
            user = bot.get_user(user_id)
            if user:
                users_text.append(f"{user.mention} ({user.id})")
            else:
                users_text.append(f"Unknown User ({user_id})")
        embed.add_field(name=f"👤 Users ({len(whitelist['users'])})", value="\n".join(users_text) or "None", inline=False)
    else:
        embed.add_field(name="👤 Users", value="None", inline=False)
    
    # Roles
    if whitelist["roles"]:
        roles_text = []
        for role_id in whitelist["roles"]:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_text.append(f"{role.mention} ({role.id})")
            else:
                roles_text.append(f"Unknown Role ({role_id})")
        embed.add_field(name=f"👥 Roles ({len(whitelist['roles'])})", value="\n".join(roles_text) or "None", inline=False)
    else:
        embed.add_field(name="👥 Roles", value="None", inline=False)
    
    embed.set_footer(text="Whitelisted users/roles bypass all filters")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="addkey", description="Add a Gemini API key")
@app_commands.describe(api_key="The API key to add")
async def addkey(interaction: discord.Interaction, api_key: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if api_key in config["gemini_api_keys"]:
        await interaction.response.send_message("⚠️ This API key is already added.", ephemeral=True)
        return
    
    config["gemini_api_keys"].append(api_key)
    save_config()
    await interaction.response.send_message(f"✅ API key added! Total keys: {len(config['gemini_api_keys'])}", ephemeral=True)

@bot.tree.command(name="listkeys", description="List all API keys")
async def listkeys(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if not config["gemini_api_keys"]:
        await interaction.response.send_message("⚠️ No API keys configured.", ephemeral=True)
        return
    
    key_list = "\n".join([
        f"{'➡️' if i == config['current_key_index'] else '  '} Key #{i+1}: {key[:8]}...{key[-4:]}" 
        for i, key in enumerate(config["gemini_api_keys"])
    ])
    
    await interaction.response.send_message(f"**API Keys ({len(config['gemini_api_keys'])} total):**\n```{key_list}```\n➡️ = Currently active", ephemeral=True)

@bot.tree.command(name="removekey", description="Remove an API key")
@app_commands.describe(key_number="Key number to remove")
async def removekey(interaction: discord.Interaction, key_number: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    if key_number < 1 or key_number > len(config["gemini_api_keys"]):
        await interaction.response.send_message(f"❌ Invalid key number. Must be 1-{len(config['gemini_api_keys'])}", ephemeral=True)
        return
    
    removed_key = config["gemini_api_keys"].pop(key_number - 1)
    if config["current_key_index"] >= len(config["gemini_api_keys"]) and config["gemini_api_keys"]:
        config["current_key_index"] = 0
    save_config()
    
    await interaction.response.send_message(f"✅ Removed key #{key_number}: {removed_key[:8]}...{removed_key[-4:]}", ephemeral=True)

@bot.tree.command(name="user", description="Check user violation history")
@app_commands.describe(user="The user to check")
async def check_user(interaction: discord.Interaction, user: discord.User):
    user_violations = [log for log in violation_logs if log["user_id"] == user.id]
    
    if not user_violations:
        embed = discord.Embed(
            title="✅ Clean Record",
            description=f"{user.mention} has no recorded violations.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Check if whitelisted
        if user.id in whitelist["users"]:
            embed.add_field(name="Whitelist Status", value="⚪ User is whitelisted", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📋 User Violation History",
        description=f"**User:** {user.mention} ({user.id})\n**Total Violations:** {len(user_violations)}",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    
    # Check if whitelisted
    if user.id in whitelist["users"]:
        embed.add_field(name="Whitelist Status", value="⚪ User is whitelisted (bypasses filters)", inline=False)
    
    for i, violation in enumerate(user_violations[-5:], 1):
        timestamp = datetime.fromisoformat(violation["timestamp"]).strftime("%Y-%m-%d %H:%M UTC")
        content = violation["message_content"][:100] + "..." if len(violation["message_content"]) > 100 else violation["message_content"]
        
        embed.add_field(
            name=f"Violation #{len(user_violations) - 5 + i}",
            value=f"**Time:** {timestamp}\n**Reason:** {violation['reason']}\n**Message:** `{content}`",
            inline=False
        )
    
    if len(user_violations) > 5:
        embed.set_footer(text=f"Showing last 5 of {len(user_violations)} violations")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setup", description="Set monitored channel")
@app_commands.describe(channel="Channel to monitor")
async def setup(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    config["monitored_channel_id"] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ Monitoring channel set to {channel.mention}", ephemeral=True)

@bot.tree.command(name="setlog", description="Set log channel")
@app_commands.describe(channel="Channel for logs")
async def setlog(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    config["log_channel_id"] = channel.id
    save_config()
    await interaction.response.send_message(f"✅ Log channel set to {channel.mention}", ephemeral=True)

@bot.tree.command(name="toggle", description="Enable/disable bot")
@app_commands.describe(enabled="Turn on or off")
async def toggle(interaction: discord.Interaction, enabled: bool):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    config["enabled"] = enabled
    save_config()
    status = "enabled" if enabled else "disabled"
    await interaction.response.send_message(f"✅ Moderation bot is now **{status}**", ephemeral=True)

@bot.tree.command(name="status", description="Check bot status")
async def status(interaction: discord.Interaction):
    monitored_channel = bot.get_channel(config.get("monitored_channel_id"))
    log_channel = bot.get_channel(config.get("log_channel_id"))
    
    monitored_name = monitored_channel.mention if monitored_channel else "Not set"
    log_name = log_channel.mention if log_channel else "Not set"
    
    embed = discord.Embed(title="🛡️ Bot Status", color=discord.Color.blue())
    embed.add_field(name="Enabled", value="✅ Yes" if config["enabled"] else "❌ No", inline=True)
    embed.add_field(name="Monitored Channel", value=monitored_name, inline=True)
    embed.add_field(name="Log Channel", value=log_name, inline=True)
    embed.add_field(name="Patterns in Database", value=str(len(slur_patterns)), inline=True)
    embed.add_field(name="API Keys", value=str(len(config["gemini_api_keys"])), inline=True)
    embed.add_field(name="Current Key", value=f"#{config['current_key_index'] + 1}" if config["gemini_api_keys"] else "None", inline=True)
    embed.add_field(name="Today's Scans", value=str(daily_stats["messages_scanned"]), inline=True)
    embed.add_field(name="Today's Flags", value=str(daily_stats["messages_flagged"]), inline=True)
    embed.add_field(name="Total Violations", value=str(len(violation_logs)), inline=True)
    embed.add_field(name="Whitelisted Users", value=str(len(whitelist["users"])), inline=True)
    embed.add_field(name="Whitelisted Roles", value=str(len(whitelist["roles"])), inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="forcereport", description="Generate daily report now")
async def forcereport(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Administrator permissions required.", ephemeral=True)
        return
    
    await interaction.response.send_message("⏳ Generating report...", ephemeral=True)
    await generate_daily_report()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if not config["enabled"] or message.channel.id != config.get("monitored_channel_id"):
        return
    
    # Check if user is whitelisted
    if isinstance(message.author, discord.Member) and is_whitelisted(message.author):
        print(f"Skipping whitelisted user: {message.author}")
        return
    
    try:
        daily_stats["messages_scanned"] += 1
        current_hour = datetime.now().hour
        daily_stats["hourly_scans"][str(current_hour)] += 1
        save_stats()
        
        translated_text = message.content
        detected_lang = 'en'
        
        if message.content:
            translated_text, detected_lang = await translate_text(message.content)
        
        has_slur_original, found_slurs_original = contains_slur(message.content)
        has_slur_translated, found_slurs_translated = contains_slur(translated_text)
        
        has_slur = has_slur_original or has_slur_translated
        all_found_slurs = list(set(found_slurs_original + found_slurs_translated))
        
        ocr_text = None
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image'):
                    ocr_text = await ocr_image(attachment.url)
                    if ocr_text:
                        translated_ocr, _ = await translate_text(ocr_text)
                        has_slur_ocr, found_slurs_ocr = contains_slur(translated_ocr)
                        if has_slur_ocr:
                            has_slur = True
                            all_found_slurs.extend(found_slurs_ocr)
                        translated_text += f"\n[Image text: {translated_ocr}]"
        
        gemini_result = await check_with_gemini(translated_text)
        
        should_report = False
        violation_reason = []
        
        if has_slur:
            should_report = True
            violation_reason.append(f"Slurs detected: {', '.join(list(set(all_found_slurs))[:5])}")
        
        if gemini_result.get("is_harmful"):
            should_report = True
            categories = gemini_result.get("categories", [])
            violation_reason.append(f"AI detected: {', '.join(categories)}")
        
        if should_report:
            await message.delete()
            
            try:
                dm_embed = discord.Embed(
                    title="⚠️ Message Removed",
                    description="Your message was removed by the moderation system.",
                    color=discord.Color.orange()
                )
                dm_embed.add_field(
                    name="Why was my message removed?",
                    value="\n".join(violation_reason),
                    inline=False
                )
                dm_embed.add_field(
                    name="What should I do?",
                    value="Please be more careful with your language. Repeated violations may result in moderation action.",
                    inline=False
                )
                dm_embed.add_field(name="Server", value=message.guild.name, inline=True)
                dm_embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                dm_embed.set_footer(text="If you believe this was a mistake, contact server moderators")
                
                await message.author.send(embed=dm_embed)
            except discord.Forbidden:
                print(f"Could not DM user {message.author}")
            
            reason_text = " | ".join(violation_reason)
            await log_violation(message, reason_text, translated_text, gemini_result, ocr_text)
            
    except Exception as e:
        print(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
        exit(1)
    
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Translation and OCR may not work.")
    
    bot.run(TOKEN)
