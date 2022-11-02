import cv2
import numpy as np

img1 = cv2.imread('o1.jpg')
img1 = cv2.resize(img1, (300, 300))

img2 = cv2.imread('o2.jpg')
img2 = cv2.resize(img2, (300, 300))

img3 = cv2.imread('o3.jpg')
img3 = cv2.resize(img3, (300, 300))

original = np.concatenate((img1, img2, img3), axis=1)
cv2.imwrite("Original Signature Samples.jpg", original)
