import configparser
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import os

config = configparser.ConfigParser()
config.read('Folder_Extraction\path.config')

FOLDER_PATH = config.get('DEFAULT', 'path')
LOCATION = config.get('DEFAULT', 'LOCATION')
PROJECT_ID = config.get('DEFAULT', 'PROJECT_ID')
PROCESSOR_ID = config.get('DEFAULT', 'PROCESSOR_ID')
MIME_TYPE = config.get('DEFAULT', 'MIME_TYPE')


def cropandscrape(images,fieldname,reigon):
    image_path = FOLDER_PATH +'/temp/temp.png'
    cropped_image = images.crop(reigon)
    cropped_image.save(fp= image_path)
    docai_client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com"))
    name = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)
    with open(image_path, "rb") as image:
        image_content = image.read()
        raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        # Use the Document AI client to process the sample form
        result = docai_client.process_document(request=request )
        document_object = result.document
        print("Document processing complete.")
        # print_blocks(document_object.pages[0].blocks)
        return print(document_object.text)


def Scraping(FOLDER_PATH):

    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(FOLDER_PATH, filename)
            print(pdf_path)
            with open(pdf_path, "rb") as images:
                images = convert_from_path(os.path.join(FOLDER_PATH, filename), first_page=1, last_page=1,
                                           poppler_path=r'C:\Program Files\poppler-0.68.0\bin')[0]   
                company_name =cropandscrape(images=images,fieldname="Company_Name",reigon=(120, 80, 700, 220))
                date =cropandscrape(images=images,fieldname="Date",reigon= (1282, 145, 1700, 225))
                client = cropandscrape(images=images,fieldname="Client_name",reigon=(200, 220, 670, 310))
                amount = cropandscrape(images=images,fieldname="Amount",reigon=(1300, 1300, 1700, 1400))


def main():
    
    Scraping(FOLDER_PATH)


if __name__ == '__main__':
    main()
