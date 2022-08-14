
import cv2, numpy as np

def verify_image(image: bytes, min_size: tuple[int, int] | None = (416, 416), max_size: tuple[int, int] | None = None) -> bool:
    try:
        img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        h, w, c = img.shape

        if min_size and (w < min_size[0] or h < min_size[1]) or max_size and (w > max_size[0] or h > max_size[1]):
            raise
        del img
    except:
        return False
    return True