import threading
import asyncio
from async_checking import delete_files_in_directory,capture_frame,process_visual,read_out_locations_need_to_be_checked,calculate_async

IMAGE_PATH = "captured_image.jpg"
SOURCE_PATH = "Sources/source_image.jpg"
COORDINATE_FILE_PATH = "coordinate.txt"

# Define the function to be run by each thread
def print_numbers(name, count):
    for i in range(count):
        print(f"{name} printing number: {i}")

def test():
    # Create a list to hold references to thread objects
    threads = []

    # Number of threads you want to create
    num_threads = 5

    # Create and start threads in a loop
    for i in range(num_threads):
        thread_name = f"Thread {i + 1}"
        thread = threading.Thread(target=print_numbers, args=(thread_name, 5))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All threads have finished execution.")

async def visual_test():
    checking_areas = await read_out_locations_need_to_be_checked(COORDINATE_FILE_PATH)
    global image,source_image
    global final_result_image
    await delete_files_in_directory("Results")
     # Create a list to hold references to thread objects
    threads = []

    # Number of threads you want to create
    num_threads = 5
    i = 0
    # Create and start threads in a loop
    for area in checking_areas:

        thread_name = f"Thread {i + 1}"
        thread = threading.Thread(target=calculate_async, args=(area))
        threads.append(thread)
        thread.start()
        i+=1

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("All threads have finished execution.")

def print_cordinate(cordinates):
    for item in cordinates:
        print(f'{item}')

if __name__ == '__main__':
    asyncio.run(visual_test())