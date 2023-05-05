import io
import os
import PyPDF2
from PIL import Image, ImageDraw, ImageEnhance
from pdf2image import convert_from_path

# file path you want to extract images from
file ="D:/Downloads/04252023_11513.pdf"
# open the file
with open(file, "rb") as f:
    pdf = PyPDF2.PdfReader(f)
    page = pdf.pages[0]

    # convert the page to an image
    image = convert_from_path(file, first_page=1, last_page=1)[0]

    # display the image
    image.show()

    # select the region
    draw = ImageDraw.Draw(image)
    region =(1280, 149, 1700, 225)# (left, upper, right, lower)

    # adjust the contrast
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(1.5)

    # crop the image
    cropped_image = image.crop(region)

    # display the cropped image
    cropped_image.show()
