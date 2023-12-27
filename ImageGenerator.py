import streamlit as st
import requests
from openai import OpenAI
from PIL import Image, ImageDraw
from io import BytesIO

client = OpenAI(api_key=OPENAI_KEY)

# Variablen: 
#   n: 1<=n<=10
#   size: 256x256, 512x512, 1024x1024
#   prompt
#   qualtity: hd, standard
def dalle2_image(input_prompt):
    response = client.images.generate(
        model="dall-e-2",
        prompt=input_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )   
    image_url = response.data[0].url
    return image_url

def dalle3_image(input_prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=input_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )   
    image_url = response.data[0].url
    return image_url

def variations(input_image):
    response = client.images.create_variation(
        image=input_image,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    return image_url

def image_edit(input_image, input_mask, input_prompt):
    response = client.images.edit(
        image=input_image,
        mask=input_mask,
        prompt=input_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    return image_url
    
def create_mask(input_image):
    # Dimensions of the image
    #width = input_image.size[0]
    #height = input_image.size[1]
    
    left, top, right, bottom = 300, 200, 500, 400
    
    draw = ImageDraw.Draw(input_image)
    draw.rectangle([left, top, right, bottom], fill=(0, 0, 0, 0))
    
    
    # Create a new blank image (mask) with an alpha channel
    #mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    # Let's make a rectangular area in the center of the mask fully transparent
    #left, top, right, bottom = 300, 200, 500, 400
    #mask_draw = ImageDraw.Draw(mask)
    #mask_draw.rectangle([left, top, right, bottom], fill=(0, 0, 0, 0))
    
    # Save the mask as a PNG file
    draw.save("edit_mask.png")
    
    return draw

def mask():
    
    # Step 1: Open the original image
    original_image_path = "generated_image.png"
    original_image = Image.open(original_image_path)
 
    # Step 2: Create a blank image mask (black background)
    mask = Image.new("L", original_image.size, 255)
 
    # Step 3: Use ImageDraw to draw on the mask
    draw = ImageDraw.Draw(mask)
 
    # Example: Draw a white rectangle on the mask
    rectangle_coords = (400, 400, 1000, 1000)
    draw.rectangle(rectangle_coords, fill=0)
 
    # Step 4: Save the mask
    mask.save("mask.png")
 
    # Step 5: Apply the mask to the original image (optional)
    masked_image = Image.composite(original_image, Image.new("RGBA", original_image.size, "white"), mask)
    masked_image.save("generated_image_dalle2_mask.png")
    
    return mask

    

  
st.title('Generate your own images with DALL-E 2 and DALL-E 3')     
tab1, tab2, tab3 = st.tabs(["Generate Image", "Generate Image Variations", "Generate Image Edit"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        #st.header('Generate an Image using either DALL-E 2 or DALL-E 3')
        prompt = st.text_area('Describe what you want to see on the image in the prompt.', placeholder='A dog sitting on a sun bench eating pizza, bright colors')

        model = st.selectbox("Select the model you want to use.", ("DALLE2", "DALLE3"), placeholder="Select model...")
        #st.write('You selected:', model)
        submitted1 = st.button('Submit')
    
    with col2:
        if prompt.strip() != "" and submitted1:
            with st.spinner("Loading..."):
                if model == "DALLE2":
                    image_url = dalle2_image(prompt)
                if model == "DALLE3":
                    image_url = dalle3_image(prompt)
                image = st.image(image_url, caption='Generated by OpenAI') 
                image_data = requests.get(image_url).content
                with open('generated_image.png', 'wb') as handler:
                    handler.write(image_data)
                st.download_button(label="Download image", data=image_data, mime="image/png", file_name="generated_image")
        else:
            st.warning('Please enter text')
        
with tab2:
    #image2 = Image.open('DALLE1.png')
    #st.image(image2, caption='Input image')
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_image = st.file_uploader(label='Upload an image of which you would like to generate a variation here.')
        submitted2 = st.button('Create variation')
    
    with col2:
        if submitted2 and uploaded_image != None:
            image_url = variations(uploaded_image)
            image = st.image(image_url, caption='Generated by OpenAI')

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_image = st.file_uploader(label='Upload an image which you want to edit here.') 
        #uploaded_mask = st.file_uploader(label='Upload a mask for the image you want to edit here') 
        prompt = st.text_area('Text description of the desired edit', placeholder='More skyscrapers')
        submitted3 = st.button('Edit')
    
    with col2:
        if uploaded_image != None and submitted3 and prompt.strip() != "":
            #mask = open(mask("generated_image.png"), "rb")
            mask()
            mask_path = "mask.png"
            mask = open(mask_path, "rb")
            image_url = image_edit(input_image=open("generated_image.png", "rb"), input_mask=mask, input_prompt=prompt)
            st.image(image_url, caption='Generated by OpenAI')
            


        

        


    
