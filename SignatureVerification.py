import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as verifier

# Threshold value to match two signatures
THRESHOLD = 80


def match(path1, path2):
    # Load images
    src = cv2.imread(path1)
    test = cv2.imread(path2)

    # Convert images to grayscale
    src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)

    # Create binary thresholding
    _, src = cv2.threshold(src, 140, 255, cv2.THRESH_BINARY)
    _, test = cv2.threshold(test, 140, 255, cv2.THRESH_BINARY)

    # Erode the image
    src = cv2.erode(src, np.ones((5, 5)), iterations=1)
    test = cv2.erode(test, np.ones((5, 5)), iterations=2)

    # Blur image
    src = cv2.blur(src, (2, 2))
    test = cv2.blur(test, (5, 5))

    originalImages = []
    for r in range(0, src.shape[0], 300):
        for c in range(0, src.shape[1], 300):
            originalImages.append(src[r:r + 300, c:c + 300])

    # Resize images for comparison
    test = cv2.resize(test, (300, 300))

    verificationScore_1 = "{:.2f}".format(verifier(originalImages[0], test) * 100)
    verificationScore_2 = "{:.2f}".format(verifier(originalImages[1], test) * 100)
    verificationScore_3 = "{:.2f}".format(verifier(originalImages[2], test) * 100)

    return float(verificationScore_1), float(verificationScore_2), float(verificationScore_3), src, test


def browseImage(ent):
    filename = askopenfilename(filetypes=([
        ("image", ".jpeg"),
        ("image", ".png"),
        ("image", ".jpg"),
    ]))
    ent.delete(0, tk.END)
    ent.insert(tk.END, filename)


def capture_image_from_cam_into_temp(sign=1):
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cv2.namedWindow("test")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("test", frame)

        k = cv2.waitKey(1)
        if k % 256 == 27:
            # ESC pressed
            print("Escape hit, closing...")
            break
        elif k % 256 == 32:
            # SPACE pressed
            if not os.path.isdir('temp'):
                os.mkdir('temp', mode=0o777)  # img_name = "./temp/opencv_frame_{}.png".format(img_counter)
            if sign == 1:
                img_name = "./temp/test_img1.png"
            else:
                img_name = "./temp/test_img2.png"
            print('imwrite=', cv2.imwrite(filename=img_name, img=frame))
            print("{} written!".format(img_name))

    cam.release()
    cv2.destroyAllWindows()
    return True


def captureImage(ent, sign=1):
    if sign == 1:
        filename = os.getcwd() + '\\temp\\test_img1.png'
    else:
        filename = os.getcwd() + '\\temp\\test_img2.png'

    res = messagebox.askquestion(
        'Click Picture', 'Press Space Bar to click picture and ESC to exit')
    if res == 'yes':
        capture_image_from_cam_into_temp(sign=sign)
        ent.delete(0, tk.END)
        ent.insert(tk.END, filename)
    return True


def checkSimilarity(window, path1, path2):
    result = match(path1=path1, path2=path2)
    img1 = result[3]
    img2 = result[4]

    img1 = cv2.copyMakeBorder(img1, 25, 25, 50, 25, cv2.BORDER_CONSTANT, value=1)
    img2 = cv2.copyMakeBorder(img2, 25, 25, 50, 25, cv2.BORDER_CONSTANT, value=1)
    images = np.concatenate((img1, img2), axis=1)

    maxScore = max(result[0], result[1], result[2])

    if (result[0] <= THRESHOLD) & (result[1] <= THRESHOLD) & (result[2] <= THRESHOLD):
        # Display both images
        cv2.imshow("Compared Images", images)

        messagebox.showerror("Signature Verification Failed", "Verification score: " + str(maxScore) + f" %     ")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        pass
    else:
        # Display both images
        cv2.imshow("Compared Images", images)

        messagebox.showinfo("Signature Verification Successful", "Verification score: " + str(maxScore) + f" %     ")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return True


# Create main window
root = tk.Tk()
root.title("Signature Verification Using Digital Image Processing")
root.geometry("590x220")
root.configure(bg='#B1EEA8')

# Components for first image
img1_message = tk.Label(root, text="ORIGINAL SIGNATURE", font=10, bg='#B1EEA8')
img1_message.place(x=10, y=30)

image1_path_entry = tk.Entry(root, font=10)
image1_path_entry.place(x=10, y=120)

img1_browse_button = tk.Button(
    root, text="Browse", font=10, bg='cyan', command=lambda: browseImage(ent=image1_path_entry)
)
img1_browse_button.place(x=10, y=70)

# Components for second image
img2_message = tk.Label(root, text="SAMPLE SIGNATURE", font=10, bg='#B1EEA8')
img2_message.place(x=350, y=30)

image2_path_entry = tk.Entry(root, font=10)
image2_path_entry.place(x=350, y=120)

img2_capture_button = tk.Button(
    root, text="Capture", font=10, bg='cyan', command=lambda: captureImage(ent=image2_path_entry, sign=2)
)
img2_capture_button.place(x=350, y=70)

img2_browse_button = tk.Button(
    root, text="Browse", font=10, bg='cyan', command=lambda: browseImage(ent=image2_path_entry)
)
img2_browse_button.place(x=490, y=70)

# Compare button
compare_button = tk.Button(
    root, text="Compare Original Image vs Sample Image", font=10, bg='yellow',
    command=lambda: checkSimilarity(window=root, path1=image1_path_entry.get(), path2=image2_path_entry.get())
)
compare_button.place(x=100, y=160)

root.mainloop()
