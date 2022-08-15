from env import MicroEnv
import cv2, numpy as np
import requests

class CDN:
    @staticmethod
    def upload_file(file, detail: str, media_type: str, level: int = 0) -> str:
        res = requests.post(
            f'http://{MicroEnv.CDN}/internal/cdn/upload',
            files={
                'file': ('/myfile', file, media_type),
            },
            data={
                'detail': detail[:200],
                'level': level
            }
        )

        if res.status_code == 200:
            return res.content.decode('utf-8')
        else:
            raise Exception(res.status_code)

    @staticmethod
    def upload_image(
        image: bytes,
        detail: str,
        level: int = 0,
        quality: int = 80,
        min_size: tuple[int, int] | None = (416, 416),
        max_size: tuple[int, int] | None = (5000, 5000)
    ) -> str | None:
        try:
            img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            h, w, _ = img.shape
            if min_size and (w < min_size[0] or h < min_size[1]) or max_size and (w > max_size[0] or h > max_size[1]):
                del img
                raise
            del image
            img = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])[1].tobytes()
        except:
            return None

        return CDN.upload_file(img, detail, 'image/jpeg', level)