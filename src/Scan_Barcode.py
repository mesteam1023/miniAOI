import os
import glob
from dbr import *
import requests
import base64
import re

async def detectBarcode(path):
    substring_to_remove  = r"{GS}"
    new_string =""
    try:
        api_url = 'http://10.100.27.165:5000/api/detectbarcode'
        params = {'image':f'{path}'}
        response = requests.post(url=api_url, json=params)

        if response is not None:
            if response.status_code == 200:
                gets = response.json()
                for item in gets:
                    if substring_to_remove in  item:
                        # Remove the substring using regex
                        new_string = item.replace(substring_to_remove, "")
                    else:
                        new_string = item
            else:
                print(f"{response.status_code}")
                print(f"{response.reason}")
        else:
            print("Response none")
    except Exception as e:
        print(e)
        gets = None
        return
    
    # try:
    #     barcode_data=[]
    #     # 1.Initialize license.
    #     # The string "DLS2eyJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSJ9" here is a free public trial license. Note that network connection is required for this license to work.
    #     # You can also request a 30-day trial license in the customer portal: https://www.dynamsoft.com/customer/license/trialLicense?architecture=dcv&product=dbr&utm_source=samples&package=python
    #     error = BarcodeReader.init_license("DLC2MTcxNDM1NTQxMQABwBamTi5Gn+rysN2TG6qiqhJOP3mBq66Qzu3z+RhvRVcCwHhH+BfLk5PJidlz0yDKff3LfBgMx2bei0+iB9giuU8kw1g3emncdt3po4XKRO4qWCnQQ6duDzslkrm538OEciSYvANM0rmkiHxEODro4RxaLCi24c9Cm4OajVLoh4w9WnJbkZ98rJLZzlEJq/O9COl9i5yL0hzAQPO75PKnds5p4RiZuYGaLPwsHLrGxGtQhXarckVmw9w6EbT9wlVAxKZdWv2pFcqRySuZ8vYM7oRPaQoitEZqhkF2wvl68gFfRVUrvLC3Xf/Y2Lqq+FIHTV86B67JXi2cJXo/mgY892N70uHyQukoywRAw4WvbwHH16LDnIvFMXohDvJd49U/9obDd+/FkQT9Bg5czuLKBrpbYszCLggNfplONTsDlRH9vAMd9jWFwzgnaOtghr4RM3fwBtQYjNGgsM+PkdF9iAP7MUOYK9oCC67tq/YbFVO7wihfZz3rOjxkxVLhp69vaSLUriKQ7xTqP0Psx/S/HPL3KKlhPlbqYxHug8qBZHigoQI8re+t2Kivdg9ugSc//cnhP1vN6XUaFWNP9+n/NHDZWaKxNlN5Y1hMHNXj57jvqAtt9p9Rz92co7CJgoBj/DfNhIc=")
    #     if error[0] != EnumErrorCode.DBR_OK:
    #         print("License error: " + error[1])

    #     # 2.Create an instance of Barcode Reader.
    #     reader = BarcodeReader.get_instance()
    #     if reader == None:
    #         raise BarcodeReaderError("Get instance failed")

    #     # while True:
    #     try:
    #         # Replace by your own image path
    #         # image_folder = (
    #         #     os.path.dirname(os.path.abspath(__file__)) + os.path.sep + "images"
    #         # )

    #         # for idx, img in enumerate(glob.glob(os.path.join(image_folder, "*.*"))):
    #         #     print("Test", idx + 1, img)

    #             # 3. Decode barcodes from an image file
    #         text_results = reader.decode_file(path)

    #         # 4.Output the barcode text.
    #         if text_results != None and len(text_results) > 0:
    #             for text_result in text_results:
    #                 print(
    #                     "Barcode Format : ", text_result.barcode_format_string
    #                 )
    #                 print("Barcode Text : ", text_result.barcode_text)
    #                 print(
    #                     "Localization Points : ",
    #                     text_result.localization_result.localization_points,
    #                 )
    #                 print("Exception : ", text_result.exception)
    #                 barcode_data.append(text_result.barcode_text)
    #                 print("-------------")                    
                    
    #         print(40 * "#")
    #         os.remove(path)
    #         # break
            
    #     except Exception as e:
    #         pass
            
    #     reader.recycle_instance()

    # except BarcodeReaderError as bre:
    #     print(bre)
    
    return new_string
