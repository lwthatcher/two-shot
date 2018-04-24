import os
import argparse
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image
from interface import MultiModalInterface, EvaluateCutInterface


def get_image(_img, path):
    path = path or []
    img_path = os.path.join(*path, _img)
    print('Loading source image:', img_path)
    return np.asarray(Image.open(img_path))


def annotate(imgs, masks=None):
    interface = MultiModalInterface(imgs, masks)
    results = interface.run()
    # iterate over results
    results = zip(imgs, results)
    result_masks = []
    for img, (rect, mask) in results:
        has_rect, has_mask = rect is not None, 0 in np.unique(mask) or 1 in np.unique(mask)
        # do grab-cut
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        if has_rect and not has_mask:
            print('Initialization with Rectangle:')
            rect_mask = np.zeros(img.shape[:2], np.uint8)
            cv.grabCut(img, rect_mask, rect, bgdModel, fgdModel, args.iters, mode=cv.GC_INIT_WITH_RECT)
            rect_mask[mask == 0] = 0
            rect_mask[mask == 1] = 1
            print(np.unique(rect_mask), rect_mask.dtype)
            mask = rect_mask
        if has_mask:
            print('Initialization with Mask:')
            cv.grabCut(img, mask, rect, bgdModel, fgdModel, args.iters, mode=cv.GC_INIT_WITH_MASK)
        result_masks.append(mask)
    return result_masks


def masked_img(img, mask):
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    return img * mask2[:, :, np.newaxis]



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('images', nargs='*', default=['gymnastics.jpg'], help='the image to segment')
    parser.add_argument('-f', dest='folder', nargs='*', default=['img'], help='path list to the image folder path')
    parser.add_argument('--iters', '-i', type=int, default=5, help='the number of iterations to run grab-cut for')
    args = parser.parse_args()
    # load image
    imgs = [get_image(i, args.folder) for i in args.images]
    # open interface
    masks = annotate(imgs)
    # evaluate results
    img2 = masked_img(imgs[0], masks[0])
    eval_interface = EvaluateCutInterface(img2, masks[0])
    eval_result = eval_interface.run()
    print('Evaluation result', eval_result)
    # run a second time!
    masks = annotate(imgs, masks)
    # evaluate new results
    img2 = masked_img(imgs[0], masks[0])
    eval_interface = EvaluateCutInterface(img2, masks[0])
    eval_result = eval_interface.run()
    print('Evaluation result', eval_result)
