import os
import re
import warnings
from PIL import ImageEnhance, ImageFilter, Image
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import shutil
import logging
import configparser

config = configparser.ConfigParser()
config.read('path.config')

folder_path = config.get('DEFAULT', 'input_path')
output_path = config.get('DEFAULT', 'output_path')
log_file = config.get('DEFAULT', 'log_file')
company_file = config.get('DEFAULT', 'company_file')

warnings.filterwarnings("ignore", category=DeprecationWarning)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

text1 = ""
logging.basicConfig(filename=log_file, level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')
logging.info(
    '=================================New Extraction started===============================')


class DataExtraction():

    def Extract_company(folder_path, output_path, text1, company_file):

        def scrapable(filename, variable, variablevalue):
            if (variablevalue == None or str(variablevalue).strip() == ""):
                logging.exception("cannont scrape value of " +
                                  variable + " of file " + filename)
                return False
            return True

        for filename in os.listdir(folder_path):
             if filename.endswith('.pdf'):
                # convert pdf to an img and extract data from img
                images = convert_from_path(os.path.join(folder_path, filename), first_page=1, last_page=1,
                                           poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
                company_region = (40, 60, 800, 220)
                comapny_image = images[0].crop(company_region)
                contrast = ImageEnhance.Contrast(comapny_image)
                comapny_image = contrast.enhance(1.2)
                # comapny_image = comapny_image.convert('L')
                # thresholding
                threshold_value = 90
                comapny_image = comapny_image.point(lambda x: 0 if x < threshold_value else 255)
                comapny_image.show()
                company_names = pytesseract.image_to_string(
                    comapny_image, lang="eng").strip('\n\t \*').split('\n')
                # print(company_names)
                # remove empty strings
                company_names = list(filter(None, company_names))
                print(company_names)

                with open(company_file, 'r') as rf:
                    matching_company = ''
                    for company in rf:
                        company = company.strip()
                        if any(name.lower() in company.lower() for name in company_names):
                            if len(company_names) >= 4:
                                for name in company_names:
                                    if ((company_names[0]+' '+company_names[1]).lower() == company.lower()):
                                        matching_company = company
                                        break
                                    elif ((company_names[0]+' '+company_names[2]).lower().split(',')[0] == company.lower()):
                                        matching_company = company
                                        break
                                    elif ((company_names[0]+' '+company_names[2]).lower()[:-9] == company.lower()):
                                        matching_company = company
                                        break
                                    elif ((company_names[0]+' '+company_names[3]).lower().split(',')[0] == company.lower()):
                                        matching_company = company
                                        break
                            elif len(company_names) == 3:
                                for name in company_names:
                                    if ((company_names[0]+' '+company_names[2]).lower().split(',')[0] == company.lower()):
                                        matching_company = company
                                        print(matching_company)
                                        logging.info(matching_company)
                                        break


                client_region = (195, 213, 800, 317)
                client_image = images[0].crop(client_region)
                contrast = ImageEnhance.Contrast(client_image)
                client_image = contrast.enhance(1.1)
                client_image = client_image.convert('L')
                # thresholding
                threshold_value = 90
                client_image = client_image.point(lambda x: 0 if x < threshold_value else 255)
                client_image.show()
                Client = pytesseract.image_to_string(client_image, lang="eng").strip('\n\t \*').replace('/','-').split('\n')[0]
                print(Client)
                logging.info("Pay to the order of: " + Client)
                if not scrapable(filename, 'Client Name', Client):
                    continue

                date_region = (1150, 660, 1430, 860)
                date_image = images[0].crop(date_region)
                sharp = ImageEnhance.Sharpness(date_image)
                date_image = sharp.enhance(1.6)
                contrast= ImageEnhance.Contrast(date_image)
                date_image= contrast.enhance(1.3)
                date_image = date_image.convert('L')
                threshold_value = 90
                date_image = date_image.point(lambda x: 0 if x < threshold_value else 255)

                date_image = date_image.filter(ImageFilter.EDGE_ENHANCE)
                # cropped_image = cropped_image.convert('L')
                date_image = date_image.convert('1', dither=Image.NONE)

                # cropped_image = cropped_image.filter(ImageFilter.SHARPEN)
                # cropped_image = cropped_image.filter(ImageFilter.SHARPEN)

                # cropped_image = cropped_image.convert('L')
                # cropped_image = cropped_image.convert('1', dither=Image.NONE)
                
                #image filter
                # contrast = ImageEnhance.Contrast(cropped_image)
                # cropped_image = contrast.enhance(0.5)
                # thresholding
                # cropped_image.show()
                # threshold_value = 80
                # binarized_image = cropped_image.point(lambda x: 0 if x < threshold_value else 255)

                date_image.show()
                date = pytesseract.image_to_string(date_image, lang="eng").split('\n')[0].replace('§', '5')
                print('DATE: ',date)
                date = date.replace(')', '').replace('\n', '').replace('\t', '')
                if not scrapable(filename, "data", date):
                    continue
                components = date.split('/')
                try: 
                    month = int(components[0])
                    day = int(components[1])
                    year = int(components[2])
                except ValueError:
                    logging.error("Invalid date format")
                    continue

                if month and day is not None:
                    formated_date = "{:02d}{:02d}".format(month, day)
                print(formated_date)
                
                print (year)
                logging.info("Formated Date: " + formated_date)

                cash_region = (1300, 1300, 1700, 1400)
                cropped_image3 = images[0].crop(cash_region)
                contrast = ImageEnhance.Contrast(cropped_image3)
                cropped_image = contrast.enhance(1.1)
                grayscale_image = cropped_image.convert('L')
                # thresholding
                threshold_value = 90
                binarized_image = grayscale_image.point(lambda x: 0 if x < threshold_value else 255)
                amount = pytesseract.image_to_string(
                    binarized_image, lang="eng").strip('\n\t')
                binarized_image.show()
                if not scrapable(filename, "amount", amount):
                    continue
                print(amount)
                logging.info("Amount: " + amount)
                text1 = (str(year) + " " +matching_company)
                logging.info (f'New Folder Name: {text1}')
                new_filename1 = f"{formated_date} {Client} ${amount}.pdf".encode("ascii", "ignore").decode().replace("*", "").replace("/", "-")
                logging.info("file name replace with: " + new_filename1)

                try:
                    folder_path_new = os.path.join(output_path, text1)
                    if not os.path.exists(folder_path_new):
                        os.makedirs(folder_path_new)
                        logging.info(f"Folder created for {text1}")

                        # move pdf file to the folder with same name
                    shutil.move(os.path.join(folder_path, filename),
                                os.path.join(folder_path_new, filename))
                    logging.info(f"PDF file moved to folder {text1}")

                    file_path = os.path.join(folder_path_new, Client)
                    if not os.path.exists(file_path):
                        os.makedirs(file_path)
                    shutil.move(os.path.join(folder_path_new, filename),
                                os.path.join(file_path, new_filename1))

                except Exception as e:
                    logging.info(
                        f"Error occurred while processing {filename}:{str(e)} ")

        return logging.info("Data Extacted Scuessfully")
    


    Extract_company(folder_path, output_path, text1, company_file)
    
warnings.resetwarnings()
