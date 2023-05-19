import io
import os
import PyPDF2
from PIL import Image, ImageDraw, ImageEnhance
import pytesseract
from pdf2image import convert_from_path

# file path you want to extract images from
file ="C:/LLC/05052023_17895.pdf"
# open the file
with open(file, "rb") as f:
    pdf = PyPDF2.PdfReader(f)
    page = pdf.pages[0]

    # convert the page to an image
    image = convert_from_path(file, first_page=1, last_page=1)[0]

    # select the region
    region =(1282, 140, 1550, 220)# (left, upper, right, lower)

    # crop the image
    cropped_image = image.crop(region)

    # adjust the contrast
    contrast = ImageEnhance.Contrast(cropped_image)
    cropped_image = contrast.enhance(1.5)

    # convert the image to grayscale
    grayscale_image = cropped_image.convert('L')

    # apply thresholding to binarize the image
    threshold_value = 128
    binarized_image = grayscale_image.point(lambda x: 0 if x < threshold_value else 255)

    # display the pre-processed image
    binarized_image.show()

    # perform OCR on the image
    company_names = pytesseract.image_to_string(
        binarized_image, lang="eng").strip('\n\t \*').split('\n')

    # remove empty strings
    company_names = list(filter(None, company_names))

    # print the extracted text
    print(company_names)
