import asyncio
import base64
import json
import random
import subprocess
import cv2 as cv
import numpy as np
import pytesseract
from PIL import Image, ImageFont, ImageDraw
from spellchecker import SpellChecker
from capture_image import capture_frame, take_picture, raspi_io


async def read_out_locations_need_to_be_checked(coordinate_file_path):
    areas = []
    with open(coordinate_file_path, "r") as file:
        for line in file:
            check_type = line.strip().split(",")[0]
            top_left_x: int = int(line.strip().split(",")[1])
            top_left_y: int = int(line.strip().split(",")[2])
            bottom_right_x: int = int(line.strip().split(",")[3])
            bottom_right_y: int = int(line.strip().split(",")[4])
            top_left = (top_left_x, top_left_y)
            bottom_right = (bottom_right_x, bottom_right_y)
            areas.append((check_type, [top_left, bottom_right]))
    return areas


IMAGE_PATH = "Sources/source_image.jpg"


async def load_image(image_path):
    img = cv.imread(image_path)
    source = cv.imread(SOURCE_PATH)
    return img, source


async def tranform_image(image_path, image=None, alpha=1.5, beta=-50.0, rotate=0):
    global resized

    # Load the image
    if image is None:
        pil_img = Image.open(image_path)
        rotated_img = pil_img.rotate(rotate, expand=True)
        image = np.array(rotated_img)
    else:
        pil_img = Image.fromarray(np.array(image))
        rotated_img = pil_img.rotate(rotate, expand=True)
        image = np.array(rotated_img)

        # Median Blur
    median_blur = cv.medianBlur(image, 1)

    try:
        gray_image = cv.cvtColor(median_blur, cv.COLOR_BGR2GRAY)
    except Exception as e:
        print(e)
        gray_image = image
    # Apply edge detection (using Canny edge detector as an example)

    sharpened = sharpen_image(gray_image)

    adjusted = cv.convertScaleAbs(sharpened, alpha=3, beta=100)

    # adjusted = gray_image
    _, thresh = cv.threshold(adjusted, 150, 255, cv.THRESH_BINARY)

    if thresh.shape[0] > thresh.shape[1] and thresh.shape[1] < 300:
        zoom = (300 / thresh.shape[1]) + 1
        resized = cv.resize(
            thresh,
            (int(adjusted.shape[1] * zoom), int(thresh.shape[0] * zoom)),
            interpolation=cv.INTER_LINEAR_EXACT,
        )

    if thresh.shape[1] > thresh.shape[0] and thresh.shape[0] < 300:
        zoom = (300 / adjusted.shape[0]) + 1
        resized = cv.resize(
            thresh,
            (int(adjusted.shape[1] * zoom), int(thresh.shape[0] * zoom)),
            interpolation=cv.INTER_LINEAR_EXACT,
        )

    # Gaussian Blur
    # gaussian_blur = cv.GaussianBlur(resized, (1, 1), 0)

    # # Median Blur
    # median_blur = cv.medianBlur(resized, 5)

    # sharpened = sharpen_image(median_blur)

    # Display the original and processed images
    # # cv.imshow('Original Image', adjusted)
    # cv.waitKey(0)
    # # cv.imshow('Grayscale Image', gray_image)
    # cv.waitKey(0)
    # # cv.imshow('Edge Detection', sharpened)
    # cv.waitKey(0)
    # # cv.imshow('Threshold', thresh)
    # cv.waitKey(0)
    # # cv.imshow('Resized', resized)
    # cv.waitKey(0)
    # # cv.imshow('Gaussian Blur', gaussian_blur)
    # cv.waitKey(0)
    # # cv.imshow('Median Blur', median_blur)

    # Wait for a key press and then close all windows
    # cv.destroyAllWindows()
    return median_blur, sharpened, gray_image


async def sharpen_image(image):
    kernel = np.array([[-1, -1, -1], [-1, 255, -1], [-1, -1, -1]])
    sharpened = cv.filter2D(image, -1, kernel)
    return sharpened


async def correct_color(image):
    try:
        hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    except Exception as e:
        hsv = cv.cvtColor(cv.cvtColor(image, cv.COLOR_GRAY2BGR), cv.COLOR_BGR2HSV)

    h, s, v = cv.split(hsv)

    # Adjust the saturation and value channels
    h = cv.equalizeHist(h)
    s = cv.equalizeHist(s)
    v = cv.equalizeHist(v)

    enhanced_hsv = cv.merge([h, s, v])
    return cv.cvtColor(enhanced_hsv, cv.COLOR_HSV2BGR)


async def insert_image_into_white_base(image1, position, width=400, height=400):
    # Create a blank 300x300 black image

    base_image = np.zeros((width, height, 3), dtype="uint8")
    base_image[:] = (255, 255, 255)
    # Load another image (replace with the path to your image)
    # Ensure the image to insert is smaller than 300x300
    insert_image = image1  # Replace with the correct path
    insert_height, insert_width = insert_image.shape[:2]
    x_offset = 0
    y_offset = 0
    # Coordinates where to insert the image on the base image
    x_offset, y_offset = position  # Example y coordinate

    # Insert the image
    base_image[
        y_offset : y_offset + insert_height, x_offset : x_offset + insert_width
    ] = insert_image

    return base_image


IMAGE_PATH = "captured_image.jpg"
SOURCE_PATH = "Sources/source_image.jpg"
COORDINATE_FILE_PATH = "coordinate.txt"


async def aoi(area):
    final_result = []
    image, source_image = await load_image(IMAGE_PATH)

    if image is None:
        print("Could not read input image")
        final_result.append(False)
        return
    if source_image is None:
        print("Could not read source image")
        final_result.append(False)
        return
    if image.shape != source_image.shape:
        print("Input and source images must be of the same size")
        final_result.append(False)
        return

    ocr_result_final = await process_image(image)
    if ocr_result_final:
        return ocr_result_final

    return None


async def process_image(image):
    ocr_result_final = []
    ocr_result = []
    longest = ""

    img_resized = await preprocess_image(image)

    thresh = 30
    while thresh < 180:
        ocr_result = []
        thresh += 20
        img_adjust = await adjust_image(img_resized, thresh)
        text = await extract_text_from_image(img_adjust)
        if text is None or text == "" or longest == "" or longest is None:
            continue
        if len(text) > len(longest):
            longest = text
        idx = False
        if text is not None:
            ocr_result.append(text)
            try:
                idx = content_text.find(text)
            except Exception as e:
                print(e)

            if idx > 0:
                print(f"OK: {text}")
                ocr = await find_best_ocr_result(ocr_result)
                await ocr_result_final.append(ocr)
                break

            if ocr_result:
                longest = spell.correction(longest)
                ocr = longest
                ocr_result.append(longest)

    if ocr_result_final:
        ocr = spell.correction(longest)
        return ocr

    return None


async def preprocess_image(image):
    img_ocr = cv.imread(f"rotated_image.jpg")
    shape = img_ocr.shape[:2]
    h, w = shape
    print(w, h)

    if w > h:
        ratio = 300 / w
        w = int(w * ratio)
        h = int(h * ratio)
    else:
        ratio = 300 / h
        w = int(w * ratio)
        h = int(h * ratio)
    img_resized = cv.resize(img_ocr, (w, h), interpolation=cv.INTER_LINEAR_EXACT)
    img_resized = await insert_image_into_white_base(
        img_resized, (int(150 - w / 2), int(150 - h / 2)), 300, 300
    )
    return img_resized


async def adjust_image(image, thresh):
    try:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    except Exception as e:
        print(e)
        gray = image

    _, img_adjust = cv.threshold(gray, thresh, 255, cv.THRESH_BINARY_INV)

    img_adjust = await sharpen_image(img_adjust)

    return img_adjust


async def extract_text_from_image(image):
    global count
    img = None
    markup1 = None
    markup2 = None
    markup3 = None
    img = Image.fromarray(image)
    count += 1
    #
    text = pytesseract.image_to_string(img)
    img.save(f"ocr{count}.jpg")
    print(text)
    if text != "" and text is not None:
        corrected = spell.correction(text)
        print(corrected)
    else:
        #markup1 = await preprocess_image(img)
        markup2 = await adjust_image(img, 90)
        markup3 = await correct_color(markup2)
        # # cv.imshow(f"ocr{count}.jpg", markup3)
        count += 1
        text_img = Image.fromarray(markup3)
        text = pytesseract.image_to_string(text_img)
        corrected = spell.correction(text)
        text_img.save(f"ocr{count}.jpg")
        print(corrected)

    if corrected is not None:
        return corrected.strip()
    else:
        return ""


async def find_best_ocr_result(ocr_result):
    longest = spell.correction(ocr_result[0])
    return longest


async def add_unicode_text_to_image(
    image_cv, text, position, font_path, font_size, text_color=None, bg_color=(0, 0, 0)
):
    if text_color is None:
        text_color = random_color()
    """
    Adds Unicode text with a background to an image at the specified position.

    :param image_path: Path to the image file.
    :param text: Unicode text to be added.
    :param position: Tuple (x, y) specifying the position to add the text.
    :param font_path: Path to a .ttf font file that supports Unicode.
    :param font_size: Size of the font.
    :param text_color: Text color in RGB format (default is white).
    :param bg_color: Background color in RGB format (default is black).
    :return: Image with text as a numpy array in OpenCV format.
    """

    # Convert from OpenCV BGR to PIL RGB format
    image_pil = Image.fromarray(cv.cvtColor(image_cv, cv.COLOR_BGR2RGB))

    # Prepare to draw on the image
    draw = ImageDraw.Draw(image_pil)

    # Load the font and specify the size
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text size and position
    background_area = (position[0], position[1], position[0], position[1])

    # Draw the background
    draw.rectangle(background_area, fill=bg_color)

    # Draw the text
    draw.text(position, text, font=font, fill=text_color)

    # Convert back to OpenCV format and return
    return cv.cvtColor(np.array(image_pil), cv.COLOR_RGB2BGR)


DICTIONARY_FILE = "dictionary.txt"


def add_special_words_to_dictionary():
    global spell
    spell = SpellChecker(language=None, case_sensitive=False)
    spell.word_frequency.load_text_file(DICTIONARY_FILE, encoding="utf-8")
    return spell


async def load_partial_image(image, top_left, bottom_right):
    return image[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]


async def calculate_average_color(image):
    return np.mean(image, axis=(0, 1))


async def compare_color_and_save_mask(image, source, roi, threshold=90):
    if roi is None:
        roi = ((0, 0), (image.shape[1], image.shape[0]))
    else:
        roi = roi
    top_left, bottom_right = roi
    region_width = bottom_right[0] - top_left[0]
    region_height = bottom_right[1] - top_left[1]

    # template_resized = cv.resize(source, (region_width, region_height))
    try:
        template_hsv = cv.cvtColor(source, cv.COLOR_BGR2HSV)
    except Exception as e:
        template_hsv = cv.cvtColor(
            cv.cvtColor(source, cv.COLOR_GRAY2BGR), cv.COLOR_BGR2HSV
        )

    try:
        image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    except Exception as e:
        image_hsv = cv.cvtColor(cv.cvtColor(image, cv.COLOR_GRAY2BGR), cv.COLOR_BGR2HSV)

    main_image_hsv = image_hsv[
        top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]
    ]

    avg_color_template = await calculate_average_color(template_hsv)
    avg_color_main_image = await calculate_average_color(main_image_hsv)
    diff = avg_color_main_image - avg_color_template

    # avg_color_template = np.uint8([[avg_color_template]])
    # avg_color_template = cv.cvtColor(avg_color_template, cv.COLOR_HSV2BGR)
    # avg_color_main_image = np.uint8([[avg_color_main_image]])
    # avg_color_main_image = cv.cvtColor(avg_color_main_image, cv.COLOR_HSV2BGR)
    # color_difference = np.linalg.norm(avg_color_template - avg_color_main_image)
    # Create a blank mask
    color_difference = np.linalg.norm(diff)

    mask = np.zeros(image.shape[:2], dtype="uint8")
    result = mask.copy()
    # If color difference is significant, fill the ROI in the mask
    if color_difference > threshold:
        result[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]] = 255
        cv.rectangle(result, top_left, bottom_right, (0, 0, 255), 1)
    else:
        result[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]] = 0
        cv.rectangle(result, top_left, bottom_right, (0, 255, 0), 1)

    mask_path = f"Results/color_{roi}.jpg"

    # Save the mask
    # # cv.imshow(mask_path, diff)

    return color_difference > threshold, roi


async def calculate_async(area):
    global image, source_image
    global final_result_image
    final_result_image = final_result_image
    final_result = []
    final_data = []
    checking_type, item = area
    result = False
    checking_content = ""
    top_left, bottom_right = item
    # source_top_left: int = int(top_left-(5,5))
    # source_top_left_y: int = int(item.strip().split(',')[1]-5)
    # source_bottom_right_x: int = int(item.strip().split(',')[2]+5)
    # source_bottom_right_y: int = int(item.strip().split(',')[3]+5)

    offset = 2
    source_top_left = (max(0, top_left[0] - offset), max(0, top_left[1] - offset))
    source_bottom_right = (
        min(image.shape[1], bottom_right[0] + offset),
        min(image.shape[0], bottom_right[1] + offset),
    )
    # hsv_partial_image = load_partial_image(hsv_image, top_left, bottom_right)
    # hsv_partial_path = 'Sources/hsv_partial_image.jpg'
    # # cv.imshow(hsv_partial_path, hsv_partial_image)
    partial_image = await load_partial_image(image, top_left, bottom_right)
    partial_path = "Sources/partial_image.jpg"
    # if partial_image is not None:
    # # cv.imshow(partial_path, partial_image)
    # # cv.imshow(partial_image)
    partial_source_image = await load_partial_image(
        source_image, top_left, bottom_right
    )
    partial_source_path = "Sources/partial_source_image.jpg"
    # # cv.imshow(partial_source_path, partial_source_image)
    # # cv.imshow(partial_source_image)
    partial_area_image = await load_partial_image(
        image, source_top_left, source_bottom_right
    )
    partial_area_path = "Sources/partial_area_image.jpg"
    # # cv.imshow(partial_area_path, partial_area_image)
    # # cv.imshow(partial_area_image)

    # partial_area_image = cv.GaussianBlur(partial_area_image, (5, 5), 0)
    # partial_source_image = cv.GaussianBlur(partial_source_image, (5, 5), 0)
    # partial_image = cv.GaussianBlur(partial_image, (5, 5), 0)
    # image = cv.GaussianBlur(image, (5, 5), 0)
    if checking_type == "c":
        wrong_color, roi = await compare_color_and_save_mask(
            image, partial_source_image, item, 90
        )
        top_left, bottom_right = roi

        # wrong_color = is_similar(image, source_image)
        # wrong_color, color_mask = check_wrong_color(partial_image, red_color_ranges)
        print(f"Wrong Color: {wrong_color}")
        if not wrong_color:
            result = True
            final_color = (0, 255, 0)
        else:
            result = False
            final_color = (0, 0, 255)
        final_result.append(result)
        cv.rectangle(partial_area_image, (0, 0), (5, 5), final_color, -1)
        cv.rectangle(final_result_image, top_left, bottom_right, final_color, 1)
    else:
        wrong_position = await check_not_in_position(
            partial_area_image, partial_source_image, item, image
        )
        if not wrong_position:
            result = True
            final_color = (0, 255, 0)
        else:
            result = False
            final_color = (0, 0, 255)
        final_result.append(result)
        cv.rectangle(partial_area_image, (0, 0), (5, 5), final_color, -1)
        cv.rectangle(final_result_image, top_left, bottom_right, final_color, 1)
        checking_content = await extract_text_from_image(partial_image)

        final_result_image = await add_unicode_text_to_image(
            final_result_image,
            str(checking_content),
            position=bottom_right,
            font_path="Fonts/TitilliumWeb-Italic.ttf",
            font_size=10,
            text_color=(0, 0, 255),
        )
    _, encoded_image = cv.imencode(".jpg", partial_area_image)
    image_bytes = encoded_image.tobytes()
    tmp = {
        "topLeft": f"{item[0][0]},{item[0][1]}",
        "bottomRight": f"{item[1][0]},{item[1][1]}",
        "checkType": checking_type,
        "result": str(result),
        # "finalResultImage": base64.b64encode(image_bytes).decode(),
        # 'finalResultImage': '',
        "checkingContent": checking_content,
    }
    final_data.append(tmp)
    cv.imwrite(f"Results/{item}-result.jpg", partial_area_image)
    # # cv.imshow(partial_area_image)

    if False in final_result:
        print("Defected")
        visual_inspection_result = "FAIL"
        visual_inspection_result_color = (255, 0, 0)

    else:
        print("Similar")
        visual_inspection_result = "PASS"
        visual_inspection_result_color = (0, 255, 0)

    # cv.imshow(
    #     "final_result_image",
    #     final_result_image,
    # )

    # # cv.imshow(final_result_image)
    return final_data


async def check_not_in_position(image, template, area, original_image):
    original_top_left, original_bottom_right = area
    captured_image = original_image[
        original_top_left[1] : original_bottom_right[1],
        original_top_left[0] : original_bottom_right[0],
    ]
    target_image_gray = cv.cvtColor(captured_image, cv.COLOR_BGR2GRAY)
    image_gray = await convert_to_gray(image)
    template_gray = await convert_to_gray(template)
    w, h = target_image_gray.shape[::-1]
    methods = [
        cv.TM_CCOEFF_NORMED,
        cv.TM_CCORR_NORMED,
        cv.TM_SQDIFF_NORMED,
        cv.TM_CCORR,
        cv.TM_CCOEFF,
        cv.TM_SQDIFF,
    ]
    for method in methods:
        res = cv.matchTemplate(image_gray, template_gray, method)
        _, max_val, max_loc, min_loc = cv.minMaxLoc(res)
        top_left = min_loc if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED] else max_loc
        threshold = 0.85
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            outer_top_left, bottom_right = await get_outer_top_left_and_bottom_right(
                top_left, pt, w, h
            )
            template_crop = await get_template_crop(
                template, outer_top_left, bottom_right
            )
            similar_area = await get_similar_area(
                captured_image, top_left, bottom_right
            )
            edge_difference, edges = await compare_features(
                template_crop, similar_area, detect_edges
            )
            corner_difference, corners = await compare_features(
                template_crop, similar_area, detect_corners
            )
            wrong_color, roi = await get_color(
                edge_difference, corner_difference, similar_area, template_crop
            )
            if edge_difference < 5 and corner_difference < 9 and not wrong_color:
                return False

    return True


async def convert_to_gray(image):
    try:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    except Exception:
        gray = image
    return gray


async def get_outer_top_left_and_bottom_right(top_left, pt, w, h):
    outer_top_left = (top_left[0] + pt[0], top_left[1] + pt[1])
    bottom_right = (outer_top_left[0] + w, outer_top_left[1] + h)
    return outer_top_left, bottom_right


async def get_template_crop(template, outer_top_left, bottom_right):
    template_crop = template[
        outer_top_left[1] : bottom_right[1], outer_top_left[0] : bottom_right[0]
    ]
    return template_crop


async def get_similar_area(captured_image, outer_top_left, bottom_right):
    similar_area = captured_image[
        outer_top_left[1] : bottom_right[1], outer_top_left[0] : bottom_right[0]
    ]
    return similar_area


async def get_color(edge_difference, corner_difference, similar_area, template_crop):
    wrong_color, roi = await compare_color_and_save_mask(
        similar_area, template_crop, None, 90
    )
    return wrong_color, roi
    # if edge_difference < 5 and corner_difference < 10:
    #     return (244, 187, 88) if wrong_color else (0, 255, 0)
    # else:
    #     return (0, 0, 255) if wrong_color else (244, 187, 88)


async def detect_edges(image):
    try:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    except:
        gray = image
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    edges = cv.Canny(blurred, 50, 150)
    return edges


async def detect_corners(image):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    good_corners = cv.goodFeaturesToTrack(gray, 80, 0.01, 5)
    good_corners = np.intp(good_corners)
    corners = cv.cornerHarris(gray, 2, 3, 0.04)
    corners = cv.dilate(corners, None)
    return good_corners, corners


async def compare_features(image1, image2, feature_detector):
    """
    Compares the features of two images using a specified feature detector.

    Parameters:
    image1 (numpy.ndarray): The first image.
    image2 (numpy.ndarray): The second image.
    feature_detector (function): The feature detector function to use.

    Returns:
    tuple: A tuple containing the difference in feature counts and the modified image.

    """
    if feature_detector == detect_edges:
        # Create images to visualize the edges and corners
        features1 = await feature_detector(image1)
        features2 = await feature_detector(image2)
        image = image2.copy()
        image[features2 > 0.01 * features2.max()] = [0, 0, 0]
    else:
        features1, corners1 = await feature_detector(image1)
        features2, corners2 = await feature_detector(image2)
        # Create images to visualize the edges and corners
        image = image2.copy()
        image[corners2 > 0.01 * corners2.max()] = [0, 0, 0]
    # Here you can add your logic to compare the features
    # For simplicity, just comparing the count of features
    if len(features1) == 0:
        difference = 555
    else:
        total_f1 = len(features1)
        difference = abs(total_f1 - len(features2))

    return difference, image


async def find_best_ocr_result(ocr_results):
    """
    Finds the best OCR result from a list of OCR results.

    Args:
        ocr_results (list): A list of OCR results.

    Returns:
        str: The best OCR result.

    """
    best_result = None
    best_score = float("-inf")

    for result in ocr_results:
        idx = content_text.find(result)

        if idx > 0:
            best_result = result
            print(f"{best_result}:{best_score}")
            return best_result
        words = spell.split_words(result)
        misspelled = spell.unknown(words)
        correct_words = len(words) - len(misspelled)
        # Score can be calculated as the number of correct words
        if correct_words > best_score:
            best_score = correct_words
            best_result = result
    if -1 > best_score:
        best_result = spell.correction(result)
        print(best_result)

    print(f"{best_result}:{best_score}")
    return best_result


global image
global source_image
global final_result_image
global final_result
global final_data
global spell
global content_text
global contents
global count
count = 0

image = None  # Assign a default value to image
source_image = None
final_result_image = None
final_result = []
final_data = []
spell = None
image = None  # Assign a default value to image
content_text = None
contents = None
#subprocess.run("python3 ~/test_joint.py")
#take_picture("captured_image.jpg")

# capture_frame(False)
# source_image = cv.imread(SOURCE_PATH)
# image = cv.imread(IMAGE_PATH)
# final_result_image = image.copy()
# final_result = []
# final_data = []
# spell = add_special_words_to_dictionary()
# contents = []
# with open("ocr.txt") as file:
#     content_text = file.read()
#     for i in content_text.strip():
#         if i is not None:
#             spell.word_frequency.add(i)


async def process_visual():

    checking_areas = await read_out_locations_need_to_be_checked(COORDINATE_FILE_PATH)
    # tasks = [aoi(area) for area in filter(lambda x: x[0] == "s", checking_areas)]

    # ocr_array = asyncio.gather(*tasks)
    main_tasks = [calculate_async(area) for area in checking_areas]
    finish = await asyncio.gather(*main_tasks)
    # finish = await asyncio.gather(result)
    with open("ocr_result.txt", "w") as File:
        for item in finish:
            if item is not None:
                File.write(str(item) + "\n")
    return 'Done'

# asyncio.run(process_visual())
# cv.imwrite("Results/result.jpg", final_result_image)

async def async_checking():
    global image,source_image
    global final_result_image
    await capture_frame(False)
    source_image = cv.imread(SOURCE_PATH)
    image = cv.imread(IMAGE_PATH)
    final_result_image = image.copy()
    final_result = []
    final_data = []
    spell = add_special_words_to_dictionary()
    contents = []
    with open("ocr.txt") as file:
        content_text = file.read()
        for i in content_text.strip():
            if i is not None:
                spell.word_frequency.add(i)    
    # asyncio.run(process_visual())
    await process_visual()
    cv.imwrite("Results/result.jpg", final_result_image)
    return ''
