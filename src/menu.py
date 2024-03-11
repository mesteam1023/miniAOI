# This is a sample Python script.

import json

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
from async_checking import async_checking

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
            url = f"http://fvn-s-web01.friwo.local:5000/api/VisualIspection/PD/GetSamplePicture?id={id}"
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
                url = "http://fvn-s-web01.friwo.local:5000/api/VisualIspection/QD/InsertCoordinates"
                

                data = json.dumps(coordinates, default=serialize_coordinates)
                headers = {'Content-Type': 'application/json'}
                response = requests.post(url, data=data, headers=headers)

                if response.status_code == 200 or response.status_code == 201:
                    print("Data successfully sent.")               
                else:
                    print("Failed to send data:", response.status_code)
                    print("Failed to send data:", response.request.body)

            url1 = f"http://fvn-s-web01.friwo.local:5000/api/VisualIspection/PD/getCoordinates?partNo={partNo}"
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

            url = "http://fvn-s-web01.friwo.local:5000/api/VisualIspection/QD/InputSample"
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

def TakeCoordinates():
    partNo = "Test"
    with open('SampleId.txt', 'r') as file:
        for line in file:
            id = int(line.strip())
    url = f"http://fvn-s-web01.friwo.local:5000/api/VisualIspection/PD/GetSamplePicture?id={id}"
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
        url = "http://fvn-s-web01.friwo.local:5000/api/VisualIspection/QD/InsertCoordinates"
                

        data = json.dumps(coordinates, default=serialize_coordinates)
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print("Data successfully sent.")               
        else:
            print("Failed to send data:", response.status_code)
            print("Failed to send data:", response.request.body)

    url1 = f"http://fvn-s-web01.friwo.local:5000/api/VisualIspection/PD/getCoordinates?partNo={partNo}"
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

def take_sample():
    capture_frame(True)

    url = "http://fvn-s-web01.friwo.local:5000/api/VisualIspection/QD/InputSample"
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
