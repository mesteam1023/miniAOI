import datetime
import threading
import asyncio
from async_checking import delete_files_in_directory,capture_frame,process_visual,read_out_locations_need_to_be_checked,calculate_async,print_numbers_async
import random
from async_checking import image, source_image
import cv2 as cv

IMAGE_PATH = "captured_image.jpg"
SOURCE_PATH = "Sources/source_image.jpg"
COORDINATE_FILE_PATH = "coordinate.txt"

# Step 2: Define the asynchronous function
async def print_numbers(area, image, source_image):
    checking_type,item,angle,thresh = area
    print("Start at: "+str(item) + str(datetime.datetime.now()))
    # image = image.copy()
    # source_image = source_image.copy()
    # Generate a random number between 1 and 5
    random_number = random.randint(1, 5)
    for i in range(1,3):
        print(f"{item} printing number: {i}")
        await asyncio.sleep(random_number)  # Simulate a non-blocking delay
    print("End at: "+str(item) + str(datetime.datetime.now()))

# Step 3: Create a main function to manage tasks
async def main():
    checking_areas = await read_out_locations_need_to_be_checked(COORDINATE_FILE_PATH)
    tasks = []
    num_tasks = 5
    i = 0
    # Create and start tasks in a loop
    # for area in checking_areas:
    #     task_name = f"Task main {i + 1}"
    #     task = asyncio.create_task(print_numbers_async(task_name, 3,area))
    #     tasks.append(task)
    #     i+=1

    source_image = cv.imread(SOURCE_PATH)
    image = cv.imread(IMAGE_PATH)
    temp_image = image.copy()
    temp_source_image = source_image.copy()
    temp=[]
    for area in checking_areas:
        temp.append([area,temp_image.copy(), temp_source_image.copy()])
    # main_tasks = [asyncio.create_task(calculate_async(area, temp_image, temp_source_image)) for area, temp_image, temp_source_image in temp]
    main_tasks = [asyncio.create_task(print_numbers(area, temp_image, temp_source_image)) for area, temp_image, temp_source_image in temp]
    # Wait for all tasks to complete
    await asyncio.gather(*main_tasks)
    

async def visual_test():
    checking_areas = await read_out_locations_need_to_be_checked(COORDINATE_FILE_PATH)
    source_image = cv.imread(SOURCE_PATH)
    image = cv.imread(IMAGE_PATH)
    temp_image = image.copy()
    temp_source_image = source_image.copy()
    await delete_files_in_directory("Results")
     # Create a list to hold references to thread objects
    tasks = []

    # Number of threads you want to create
    num_tasks = 5
    i = 0
    # Create and start threads in a loop
    for area in checking_areas:

        task_name = f"Task {i + 1}"
        print(task_name)
        task = asyncio.create_task(calculate_async(area, temp_image, temp_source_image))
        tasks.append(task)
        i+=1

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

    print("All threads have finished execution.")


if __name__ == '__main__':
    asyncio.run(main())