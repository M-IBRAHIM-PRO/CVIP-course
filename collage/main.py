import os
import cv2
import numpy as np

def pick_images(folder_path, n_images, target_size, border_size):
    files = os.listdir(folder_path)
    image_files = [file for file in files if file.lower().endswith((".jpeg", ".jpg", ".png", ".gif", ".bmp", ".tiff"))]
    image_files = image_files[:n_images]

    resized_images = []
    for image_file in image_files:
        file_path = os.path.join(folder_path, image_file)
        image = cv2.imread(file_path)
        resized_image = cv2.resize(image, target_size)
        resized_image = cv2.copyMakeBorder(resized_image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[255, 255, 255])
        resized_images.append(resized_image)

    return np.array(resized_images)

def create_collage(images, rows):
    collage_rows = np.array_split(images, rows)
    
    if rows > 1:
        collage = np.vstack([np.hstack(row) for row in collage_rows])
    else:
        collage = np.hstack(collage_rows[0])

    return collage

def main():
    folder_path = "assignment_01\\images"
    print('Place the images in the images folder')

    rows = int(input("Enter the number of rows for the collage: "))
    columns = int(input("Enter the number of columns for the collage: "))
    width = int(input("Enter the width for resizing: "))
    height = int(input("Enter the height for resizing: "))
    target_size = (width, height)

    border_size = int(input("Enter the size of the white border: "))
    n_images = rows * columns

    images = pick_images(folder_path, n_images, target_size, border_size)
    collage = create_collage(images, rows)

    cv2.imshow("Image Collage", collage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
