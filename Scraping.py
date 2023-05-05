import os

from PIL import ImageEnhance
from pdf2image import convert_from_path
import pytesseract
import shutil
import logging
import configparser


config = configparser.ConfigParser()
config.read('path.config')

folder_path = config.get('DEFAULT', 'input_path')
output_path = config.get('DEFAULT', 'output_path')
log_file = config.get('DEFAULT', 'log_file')
company_file = config.get('DEFAULT', 'company_file')

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
                images = convert_from_path(os.path.join(folder_path, filename), first_page=1, last_page=1, poppler_path= r'C:\Program Files\poppler-0.68.0\bin')

                company_region = (180, 85, 670, 220)
                cropped_image = images[0].crop(company_region)
                # contrast = ImageEnhance.Contrast(cropped_image)
                # image = contrast.enhance(1.5)

                company_names = pytesseract.image_to_string(
                    cropped_image, lang="eng").strip('\n\t \*').split('\n')
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

                client_region = (180, 220, 600, 310)
                cropped_image = images[0].crop(client_region)
                Client = pytesseract.image_to_string(
                    cropped_image, lang="eng").strip('\n\t \*').split('\n')[0]
                print(Client)
                logging.info("Pay to the order of: " +Client)

                if not scrapable(filename, 'Client Name', Client):
                    continue
                date_region = (1280, 149, 1700, 225)
                cropped_image2 = images[0].crop(date_region)
                date = pytesseract.image_to_string(
                    cropped_image2, lang="eng").strip('\n\t')[0:4]
                print(date)
                if not scrapable(filename, "data", date):
                    continue
                components = date.split('/')
                print(components)
                month = int(components[0])
                day = int(components[1])
                year = components[2] if len(
                    components) > 2 and components[2] != '' else None
                # Use str.format() to print the date in the desired format
                if year is not None:
                    year = int(year)
                    formated_date = "{:02d}{:02d}{:02d}".format(
                        month, day, year % 100)
                else:
                    formated_date = "{:02d}{:02d}".format(month, day)

                print(formated_date)
                logging.info("Formated Date: "+ formated_date)

                year_region = (1250, 140, 1700, 200)
                cropped_image2 = images[0].crop(year_region)
                year = pytesseract.image_to_string(
                    cropped_image2, lang="eng").strip('\n\t')[-4:]
                if not scrapable(filename, "year", year):
                    continue
                print(year)
                logging.info("Year: "+ year)

                cash_region = (1300, 1300, 1700, 1400)
                cropped_image3 = images[0].crop(cash_region)
                amount = pytesseract.image_to_string(
                    cropped_image3, lang="eng").strip('\n\t')
                if not scrapable(filename, "amount", amount):
                    continue
                print(amount)
                logging.info("Amount: "+ amount)

                text1 = (year + " " + matching_company)
                logging.info("New Folder Name: " + text1)

                new_filename1 = f"{formated_date} {Client} ${amount}.pdf".encode(
                    "ascii", "ignore").decode().replace("*", "").replace("/", "-")
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
