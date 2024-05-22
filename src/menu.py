# This is a sample Python script.

import json 
import pytesseract
import cv2 as cv2
import requests
from ColorDetection import compare
from SpecifyCheckingArea import select
from capture_image import capture_frame
from PIL import Image
from io import BytesIO
import base64
from Image_Processing import encode_image_to_base64
from Object.Coordinates import Coordinates
from Object.Coordinates import serialize_coordinates
from async_checking import async_checking,load_partial_image,read_txt_file

file_path = 'coordinate.txt'


class SampleObject:
    def __init__(self, id, picture, remark):
        self.id = id
        self.picture = picture
        self.remark = remark


def menu(name):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    if name == 1:
        capture_frame(False)
        import matplotlib.pyplot as plt
        img = cv2.imread('Source/source_image.jpg')
        imgplot = plt.imshow(img)
        plt.show()
        areas = []
        with open(file_path, 'r') as file:
            for line in file:
                top_left_x: int = int(line.strip().split(',')[0])
                top_left_y: int = int(line.strip().split(',')[1])
                bottom_right_x: int = int(line.strip().split(',')[2])
                bottom_right_y: int = int(line.strip().split(',')[3])
                top_left = (top_left_x, top_left_y)
                bottom_right = (bottom_right_x, bottom_right_y)
                print((top_left_x, top_left_y))
                print((bottom_right_x, bottom_right_y))
                areas.append([top_left, bottom_right])
        if not areas is None:
            compare(areas)
    else:
        if name == 0:                      
            partNo = "Test"
            with open('SampleId.txt', 'r') as file:
                for line in file:
                    id = int(line.strip())
            url = f"http://10.100.10.83:5000/api/VisualIspection/PD/GetSamplePicture?id={id}"
            response = requests.get(url)
            # Convert Base64 bytes to string (optional, depending on your use case)

            # print(
            #     response.content
            # )
            result_list = json.loads(response.content)
            json_item = result_list[0]
           

            base64str = json_item['picture']
            # print(base64str)
            # source_path = 'Sources/source_image.jpg'
            # image = Image.open(source_path)
            # buffered = BytesIO()
            # image.save(buffered, format="JPEG")
            # # Encode the image as a Base64 string
            # base64_encoded_str = base64.b64encode(buffered.getvalue()).decode()

            # Decode the Base64 string, making sure to remove the "data:image/jpeg;base64," part
            image_data = base64.b64decode(base64str)

            # Convert to a PIL image
            image = Image.open(BytesIO(image_data))

            # Save the image to a file
            image.save('Sources/source_image.jpg')

            areas = select('Sources/source_image.jpg')

            # with open(file_path, 'w') as file:
            for item in areas:
                    # file.write(f'{item[0][0]},{item[0][1]},{item[1][0]},{item[1][1]}\n')
                topLeft = f'{item[0][0]},{item[0][1]}'
                bottomRight = f'{item[1][0]},{item[1][1]}'
                coordinates = Coordinates(0,partNo,"1",str(id),topLeft,bottomRight)            
                url = "http://10.100.10.83:5000/api/VisualIspection/QD/InsertCoordinates"
                

                data = json.dumps(coordinates, default=serialize_coordinates)
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=data, headers=headers)

                if response.status_code == 200 or response.status_code == 201:
                    print("Data successfully sent.")               
                else:
                    print("Failed to send data:", response.status_code)
                    print("Failed to send data:", response.request.body)

            url1 = f"http://10.100.10.83:5000/api/VisualIspection/PD/getCoordinates?partNo={partNo}"
            response1 = requests.get(url1)
            # Convert Base64 bytes to string (optional, depending on your use case)

            # print(
            #     response.content
            # )
            result_list1 = json.loads(response1.content)
            with open(file_path, 'w') as file:
                for item in result_list1:
                     topLeft = item['topLeft']
                     bottomRight = item['bottomRight']
                     file.write(f's,{topLeft},{bottomRight}\n')
        else:
            capture_frame(True)

            url = "http://10.100.10.83:5000/api/VisualIspection/QD/InputSample"
            # url = "https://my-json-server.typicode.com/JasonNguyen1205/GitRepo/sample"
            source_path = 'Sources/source_image.jpg'
            picture = encode_image_to_base64(source_path)

            data = json.dumps({
                "id": 0,
                "picture": picture,
                "remark": "strwerwering"
            })
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=data, headers=headers)

            if response.status_code == 200 or response.status_code == 201:
                print("Data successfully sent.")
                lines_to_write = int(response.content)
                with open('SampleId.txt', 'w') as file:
                    file.writelines(str(lines_to_write))
            else:
                print("Failed to send data:", response.status_code)
                print("Failed to send data:", response.request.body)

async def TakeCoordinates(part_No):
    partNo = part_No
    checkType = "s"
    with open('SampleId.txt', 'r') as file:
        for line in file:
            id = int(line.strip())
    url = f"http://10.100.10.83:5000/api/VisualIspection/PD/GetSamplePicture?id={id}"
    response = requests.get(url)
            # Convert Base64 bytes to string (optional, depending on your use case)

            # print(
            #     response.content
            # )
    result_list = json.loads(response.content)
    json_item = result_list[0]
           

    base64str = json_item['picture']
            # print(base64str)
            # source_path = 'Sources/source_image.jpg'
            # image = Image.open(source_path)
            # buffered = BytesIO()
            # image.save(buffered, format="JPEG")
            # # Encode the image as a Base64 string
            # base64_encoded_str = base64.b64encode(buffered.getvalue()).decode()

            # Decode the Base64 string, making sure to remove the "data:image/jpeg;base64," part
    image_data = base64.b64decode(base64str)
    
    #         # Convert to a PIL image
    image = Image.open(BytesIO(image_data))

    #         # Save the image to a file
    image.save('Sources/source_image.jpg')
    sampleImage = cv2.imread('Sources/source_image.jpg')
    #Vincent test
    areas = select('Sources/source_image.jpg')

            # with open(file_path, 'w') as file:
    for item in areas:
                    # file.write(f'{item[0][0]},{item[0][1]},{item[1][0]},{item[1][1]}\n')
        topLeft = f'{item[0][0]},{item[0][1]}'
        bottomRight = f'{item[1][0]},{item[1][1]}'
        coordinates = Coordinates(0,partNo,"1",str(id),topLeft,bottomRight,0,110)            
        url = "http://10.100.10.83:5000/api/VisualIspection/QD/InsertCoordinates"
                

        data = json.dumps(coordinates, default=serialize_coordinates)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully sent.")               
        else:
            print("Failed to send data:", response.status_code)
            print("Failed to send data:", response.request.body)
    #Vincent End
    url1 = f"http://10.100.10.83:5000/api/VisualIspection/PD/getCoordinates?partNo={partNo}"
    response1 = requests.get(url1)
            # Convert Base64 bytes to string (optional, depending on your use case)

            # print(
            #     response.content
            # )
    result_list1 = json.loads(response1.content)
    with open("ocr_Sample.txt", 'w') as file:
        pass  # This line is optional; it's just to keep the with statement valid
    with open(file_path, 'w') as file:
        for item in result_list1:
            topLeft = item['topLeft']
            bottomRight = item['bottomRight']
            top_left_x: int = int(topLeft.strip().split(",")[0])
            top_left_y: int = int(topLeft.strip().split(",")[1])
            bottom_right_x: int = int(bottomRight.strip().split(",")[0])
            bottom_right_y: int = int(bottomRight.strip().split(",")[1])
            top_Left_Partial = (top_left_x,top_left_y)
            bottom_Right_Partial = (bottom_right_x,bottom_right_y)
            partial_area_image = await load_partial_image(
                sampleImage, top_Left_Partial, bottom_Right_Partial)
            angle =  read_text_from_image(partial_area_image)
            print(f"Angle: {angle}")
            # if checking_content.strip(' \n\x0c') is None or checking_content.strip(' \n\x0c')  =='':
            # checking_content = pytesseract.image_to_string(Image.fromarray(partial_area_image), lang="eng", timeout=10)            
            # if angle.strip(' \n\x0c') is None or angle.strip(' \n\x0c')  =='':
            if angle == -1:
                checkType ="c"
            else:
                checkType ="s"
            file.write(f'{checkType},{topLeft},{bottomRight},{angle}\n')

async def take_sample():
    await capture_frame(True)
    import matplotlib.pyplot as plt
    img = Image.open('Sources/source_image.jpg')
    imgplot = plt.imshow(img)
    plt.show()
    url = "http://10.100.10.83:5000/api/VisualIspection/QD/InputSample"
            # url = "https://my-json-server.typicode.com/JasonNguyen1205/GitRepo/sample"
    source_path = 'Sources/source_image.jpg'
    picture = encode_image_to_base64(source_path)

    data = json.dumps({
        "id": 0,
        "picture": picture,
        "remark": "Test"
    })
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200 or response.status_code == 201:
        print("Data successfully sent.")
        lines_to_write = int(response.content)
        with open('SampleId.txt', 'w') as file:
            file.writelines(str(lines_to_write))
    else:
        print("Failed to send data:", response.status_code)
        print("Failed to send data:", response.request.body)
# main(2)
# main(0)
# main(1)
# main(0)
# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     #main(2)
#     #main(2)
#     main(0)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
DICTIONARY_FILE = "dictionary.txt"
OCR_FILE = "ocr.txt"
def read_text_from_image(image99):    
    angle_final = -1
    # Load the image
    # image99 = cv.imread(path)
    text = ''
    # Convert the image to grayscale
    # Convert to grayscale
    gray = cv2.cvtColor(image99, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('Results/grayScale.jpg',gray)

    dictionary_text = read_txt_file(DICTIONARY_FILE)
    sample_text = read_txt_file(OCR_FILE)
    # Split the dictionary text into words
    dictionary_words = dictionary_text.split()
    sample_words = sample_text.split("\n")
    #  Initialize a list to store matched parts
    matched_parts = []
    # # Apply adaptive thresholding
    # _, thresh = cv.threshold(gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    for angle in range(0,361,45):
        # Open the image file
        imageR = Image.open('Results/grayScale.jpg')

        # Rotate the image by 90 degrees counter-clockwise
        rotated_image = imageR.rotate(angle)

        # Save the rotated image
        rotated_image.save(f"Rotate/rotated_image_{angle}.jpg")

        img_rotate = cv2.imread(f"Rotate/rotated_image_{angle}.jpg")
        
        gray = cv2.cvtColor(img_rotate, cv2.COLOR_BGR2GRAY)
        

        cv2.imwrite('Results/sample.jpg',gray)        
        # Apply thresholding to the edge difference image
        threshold_value = 110  # Adjust this value as needed
        ret, thresholded = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite('Results/threshold_sample.jpg',thresholded)
        # Perform OCR on the thresholded image
        temp_text = pytesseract.image_to_string(thresholded,nice = 10) 

        # if len(temp_text) > len(text):
        #     text = temp_text.strip(' \n\x0c')        
        with open("ocr_Sample.txt",'a') as file:
            file.write(temp_text)
        print(f'{temp_text}')
         # Split the long string into words
        long_string_words = temp_text.strip(' \n\x0c').split()      
        # Iterate through each word in the long string
        for word in long_string_words:
            # Check if the word exists in the dictionary text
            if word in dictionary_words:
                if word not in matched_parts:
                    # If found, add it to the matched parts list
                    matched_parts.append(word)
            text = ' '.join(matched_parts)
            if text is None:
                if len(temp_text) > len(text):
                    text = temp_text.strip(' \n\x0c')
            if text in sample_words:
                angle_final = angle
                break
        if angle_final > -1:
            break
    # # Apply Gaussian blur and adaptive thresholding
    # blur = cv.GaussianBlur(gray, (5, 5), 0)
    # thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY_INV, 11, 4) 

    
    print(f'Final: {text}')
    return angle_final
