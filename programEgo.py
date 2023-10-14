import discord
from discord.ext import commands
import requests
import json
import config

# Initialize the Discord bot with a command prefix
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Define your Discord bot token and OpenAI API key
discord_bot_token = config.discord_bot_token
openai_api_key = config.openai_api_key

# Event handler for bot ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Function to generate item descriptions using OpenAI GPT-3
def generate_item_description(prompt):
    openai_url = "https://api.openai.com/v1/engines/ft:davinci-002:personal::89TMV60Q/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "prompt": prompt,
        "max_tokens": 150
    }

    response = requests.post(openai_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        # Clean up the response and remove any unwanted text
        cleaned_response = response.json()["choices"][0]["text"]

        # Ensure the response starts with "Item Name:" to maintain consistency
        if not cleaned_response.startswith("Item Name:"):
            cleaned_response = f"Item Name: {cleaned_response}"

        # Split the response into lines and keep only non-empty lines
        lines = [line.strip() for line in cleaned_response.split("\n") if line.strip()]
        cleaned_response = "\n".join(lines)

        return cleaned_response
    else:
        return "Failed to generate item description."

# Function to format the item description in the desired manner
def format_item_description(response):
    # Initialize variables for item attributes
    item_name = "Unknown"
    cost = "Unknown"
    rarity = "Unknown"
    description = "Unknown"
    additional_effects = "None"

    # Split the response into lines and iterate through them
    lines = response.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("Item Name:"):
            item_name = line.replace("Item Name:", "").strip()
        elif line.startswith("Cost:"):
            cost = line.replace("Cost:", "").strip()
        elif line.startswith("Rarity:"):
            rarity = line.replace("Rarity:", "").strip()
        elif line.startswith("Description:"):
            description = line.replace("Description:", "").strip()
        elif line.startswith("Additional Effects:"):
            additional_effects = line.replace("Additional Effects:", "").strip()

    # Ensure that the cost is in the correct format (e.g., "X gold pieces")
    if not any(currency in cost for currency in ["gold pieces", "silver pieces"]):
        cost = f"{cost} gold pieces"

    # Extract the description more cleanly by removing any unwanted text
    description_parts = description.split("Additional Effects:")
    description = description_parts[0].strip()

    # Ensure that additional effects contain useful information
    if additional_effects.lower().startswith("none"):
        additional_effects = "None"

    # Format the response
    formatted_response = f"Item Name: {item_name}\nCost: {cost}\nRarity: {rarity}\nDescription: {description}\nAdditional Effects: {additional_effects}"

    return formatted_response

@bot.command()
async def createitem(ctx, *, item_type):
    # Define the OpenAI GPT-3 prompt
    prompt = f"Create a {item_type}."

    # Send a request to OpenAI GPT-3
    response = generate_item_description(prompt)

    # Send the generated item description to the Discord channel
    formatted_response = format_item_description(response)
    await ctx.send(formatted_response)

@bot.command()
async def repeat(ctx, *, message):
    target_channel_id = 1162096190356209715
    target_channel = bot.get_channel(target_channel_id)

    if target_channel:
        await target_channel.send(message)
    else:
        await ctx.send("Could not find the target channel.")

# Start the Discord bot
bot.run(discord_bot_token)
