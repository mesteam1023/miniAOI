import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt


async def template_check(source,image):
    # img = cv.cvtColor(image, cv.IMREAD_GRAYSCALE)
    img = cv.imread('Sources/partial_image.jpg', cv.IMREAD_GRAYSCALE)
    assert img is not None, "file could not be read, check with os.path.exists()"
    img2 = img.copy()
    # template = cv.cvtColor(source, cv.IMREAD_GRAYSCALE)
    template = cv.imread('Sources/partial_source_image.jpg', cv.IMREAD_GRAYSCALE)
    assert template is not None, "file could not be read, check with os.path.exists()"
    w, h = template.shape[::-1]
    
    # All the 6 methods for comparison in a list
    methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
    'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
    
    for meth in methods:
        img = img2.copy()
        method = eval(meth)
        # Apply template Matching
        res = cv.matchTemplate(img,template,method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        print(method)
        print(f'Max: {max_val}')
        print(f'Min: {min_val}')
        print(f'Max loc: {max_loc}')
        print(f'min loc: {min_loc}')
    
    
    res = cv.matchTemplate(img,template,5)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    print(f'Max: {max_val}')
    print(f'Min: {min_val}')
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
    result = max_val * 100
    return result