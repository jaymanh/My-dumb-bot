import discord
import requests
import io
import base64

import json
import html
import time

from PIL import Image, PngImagePlugin
from discord.ext import commands
from discord.ext import tasks

# Set the URL for the Stable Diffusion API
url = "http://127.0.0.1:7860"
chaturl = 'localhost:5000'
ChatURI = f"http://{chaturl}/api/v1/chat"

# Define the command prefix
prefix = "d!"

# Define the intents that your bot requires
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print("Logged in as {0}".format(bot.user))



@bot.command(name="img")

async def text_to_image(ctx, *, text):
    """Generate an image based off a text input. To add a negtive prompt add negative: and all text after will be a negtive prompt"""
    # Send a message to let the user know that the images are being generated
    wait_message = await ctx.send("Generating images, please wait...")

    if "negative:" in text:
        textsplit = text.split("negative:")
        payload = {
            "prompt": textsplit[0],
            "negative_prompt": "worst quality, low quality:1.4), 3d, cgi, 3d render,  (ugly:1.3), (fused fingers), (too many fingers), (bad anatomy:1.5), (watermark:1.5), (words), letters, untracked eyes, asymmetric eyes, floating head, (logo:1.5), (bad hands:1.3), (mangled hands:1.2), (missing hands), (missing arms), backward hands, floating jewelry, unattached jewelry, floating head, doubled head, unattached head, doubled head, head in body, (misshapen body:1.1), (badly fitted headwear:1.2), floating arms, (too many arms:1.5), limbs fused with body, (facial blemish:1.5), badly fitted clothes, imperfect eyes, untracked eyes, crossed eyes, hair growing from clothes, partial faces, hair not attached to head, " + textsplit[1],
            "steps": 20,
            "width": 960,
            "height": 512,
            "restore_faces": True,
            "batch_size": 8,  # Modify this to the desired batch size
            "sampler_index": "DDIM",
        }
    else:
        payload = {
        "prompt": text,
        "negative_prompt": "worst quality, low quality:1.4), 3d, cgi, 3d render, (ugly:1.3), (fused fingers), (too many fingers), (bad anatomy:1.5), (watermark:1.5), (words), letters, untracked eyes, asymmetric eyes, floating head, (logo:1.5), (bad hands:1.3), (mangled hands:1.2), (missing hands), (missing arms), backward hands, floating jewelry, unattached jewelry, floating head, doubled head, unattached head, doubled head, head in body, (misshapen body:1.1), (badly fitted headwear:1.2), floating arms, (too many arms:1.5), limbs fused with body, (facial blemish:1.5), badly fitted clothes, imperfect eyes, untracked eyes, crossed eyes, hair growing from clothes, partial faces, hair not attached to head",
        "steps": 20,
        "width": 960,
        "height": 512,
        "restore_faces": True,
        "batch_size": 8,  # Modify this to the desired batch size
        "sampler_index": "DDIM",
        }
    #print(payload)

    # Send the payload to the API and get the response
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)
    r = response.json()

    # Loop through the images and save them
    for idx, img_data in enumerate(r['images']):
        # Extract the image from the response and save it
        image = Image.open(io.BytesIO(base64.b64decode(img_data.split(",", 1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + img_data
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))

        # Save each image with a unique filename
        filename = f"output_{idx}.png"
        image.save(filename, pnginfo=pnginfo)

        # Send a message with the image attachment
        await ctx.send(file=discord.File(filename))

    # Delete the original message after all images have been sent
    await wait_message.delete()

@bot.command(name="upscale")
async def upscale_last(ctx, text):
    """Select and image and then upscale [num] e.g. upscale 1"""
    wait_message = await ctx.send("Generating image, please wait...")

    

    with open("output_"+text+".png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    # Set the payload for the upscale conversion
    payload = {
        "upscaling_resize": 4,
        "upscaler_1": "R-ESRGAN 4x+ Anime6B",
        "image": encoded_string
    }

    # Send the payload to the API and get the response
    response = requests.post(url=f'{url}/sdapi/v1/extra-single-image', json=payload)
    r = response.json()

    # Extract the image from the response and save it
    image_data = base64.b64decode(r['image'])
    with open('output.png', 'wb') as f:
        f.write(image_data)
    
    # Delete the original message and send a new message with the image attachment
    await wait_message.delete()
    await ctx.send(file=discord.File('output.png'))

@bot.command(name="model")
async def change_model(ctx, text):
    """Change the model to input[num] e.g. model 1"""
    
    if text == "1":
        model = "anything-v3-full.safetensors"
    elif text == "2":
        model = "anything-v4.5.ckpt"
    elif text == "3":
        model = "HassanBlend1.4-Pruned.ckpt"
    elif text == "4":
        model = "HassanBlend1.5.1.2-withVae.ckpt"
    elif text == "5":
        model = "HB-Fantasy1.5.ckpt"
    elif text == "6":
        model = "model.ckpt"
    elif text == "7":
        model = "sd-v1-4-full-ema.ckpt"
    elif text == "8":
        model = "sd-v1-5-inpainting.ckpt"
    elif text == "9":
        model = "v1-5-pruned.ckpt"
    elif text == "10":
        model = "v2-1_512-ema-pruned.ckpt"
    elif text == "11":
        model = "v2-1_512-nonema-pruned.ckpt"
    elif text == "12":
        model = "wd-1-4-anime_e2.ckpt"
    else:
        await ctx.send("Error: Model must be between 1 and 12")
        return
    
    wait_message = await ctx.send("Changing model to " + model)

    payload = {
        "sd_model_checkpoint": model
    }
    

    response = requests.post(url=f'{url}/sdapi/v1/options', json=payload)
    r = response.json()
    print(r)

    await wait_message.delete()
    await ctx.send("Model has changed.")

@bot.command(name="modellist")
async def List_models(ctx):
    """Lists all the models"""
    await ctx.send(
        '1 = anything-v3-full\n2 = anything-v4.5\n3 = HassanBlend1.4-Pruned\n4 = HassanBlend1.5.1.2-withVae\n5 = HB-Fantasy1.5\n6 = IDK its just called model for somereasonn\n7 = sd-v1-4-full-ema\n8 = sd-v1-5-inpainting\n9 = v1-5-pruned\n10 = v2-1_512-ema-pruned\n11 = v2-1_512-nonema-pruned\n12 = wd-1-4-anime_e2'
    )


chat_active = False
chat_channel = None

conversation_history = {'internal': [], 'visible': []}
i = 0

last_message_time = None


@bot.command(name="chat")
async def start_Chat(ctx):
    """Start chatting with the bot"""
    global chat_active
    global chat_channel

    # Check if the chat is already active
    if chat_active:
        await ctx.send("A chat is already in progress. Use `d!end_chat` to end the current chat.")
    else:
        chat_active = True
        chat_channel = ctx.channel
        await ctx.send("To end the conversation use d!end_chat")


@bot.event
async def on_message(message):
    if chat_active and message.channel == chat_channel:
        if message.author == bot.user:
            return
    
        text = message
        global conversation_history
        global i

        if chat_active and message.channel == chat_channel:
            text = message.content

        global last_message_time
        last_message_time = time.time()

        request = {
            'user_input': text,
            'max_new_tokens': 250,
            'auto_max_new_tokens': False,
            'max_tokens_second': 0,
            'history': conversation_history,
            'mode': 'chat',
            'character': '4chan',
            'instruction_template': 'Vicuna-v1.1', 
            'your_name': 'You',
            'regenerate': False,
            '_continue': False,
            'chat_instruct_command': 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',

            # Generation params. If 'preset' is set to different than 'None', the values
            # in presets/preset-name.yaml are used instead of the individual numbers.
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
            'grammar_string': '',
            'guidance_scale': 1,
            'negative_prompt': '',

            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'custom_token_bans': '',
            'skip_special_tokens': True,
            'stopping_strings': []
        }
        response = requests.post(ChatURI, json=request)

        if response.status_code == 200:
            result = response.json()

            # Extract the response from the API
            response_text = result['results'][0]['history']['visible'][-1][1]

            # Decode HTML entities in the response
            decoded_response = html.unescape(response_text)

            # Update the conversation history
            conversation_history['internal'].append([text, decoded_response])
            conversation_history['visible'].append([text, decoded_response])

            await chat_channel.send(decoded_response)
        else:
            await chat_channel.send("An error occurred while chatting with the bot.")

    await bot.process_commands(message)

@bot.command(name="end_chat")
async def end_chat(ctx):
    """Stop the chatbot"""
    global chat_active
    global chat_channel
    global conversation_history

    if chat_active and chat_channel == ctx.channel:
        chat_active = False
        chat_channel = None

        conversation_history = {'internal': [], 'visible': []}
        await ctx.send("Chat conversation ended. You can start a new chat with `d!chat`.")

@tasks.loop(minutes=1)
async def check_inactivity():
    global last_message_time
    global conversation_history
    global chat_active
    global chat_channel
    if chat_active and last_message_time is not None:
        elapsed_time = time.time() - last_message_time
        if elapsed_time >= 60:
            if chat_channel is not None:
                await chat_channel.send("Chat conversation ended due to inactivity.")
            # End the chat
            chat_active = False
            chat_channel = None
            conversation_history = {'internal': [], 'visible': []}
            last_message_time = None

@bot.event
async def on_ready():
    check_inactivity.start()




bot.run("")