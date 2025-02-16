import cv2
threshold = 50 # Adjust threshold as needed
def check_image_quality(image_path):
    # Reading image
    image = cv2.imread(image_path)
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate image gradient using the Scharr operator
    grad_x = cv2.Scharr(gray, cv2.CV_64F, 1, 0)
    grad_y = cv2.Scharr(gray, cv2.CV_64F, 0, 1)
    gradient = cv2.addWeighted(grad_x, 0.5, grad_y, 0.5, 0)

    # Compute the standard deviation of the gradient
    gradient_std = cv2.meanStdDev(gradient)[1][0]

    # Check if the image has enough quality
    print(f"Gradient is: {gradient_std}")
    if gradient_std < threshold:
        print("Image quality is not sufficient.")
        return False
    else:
        print("Image quality is sufficient.")
        return True

image_path = "./image1_5.png"
# threshold = 130  # Adjust threshold as needed
quality = check_image_quality(image_path)
if(quality):
    print("Proceed with OCR extraction")
else:
    print("Stop further processing")
