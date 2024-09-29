import cv2
import frames

class VideoObj:
    def __init__(self, stream_url):
        video_cap = cv2.VideoCapture(stream_url)
        self.video_capture = video_cap
        self.frame_rate = video_cap.get(cv2.CAP_PROP_FPS)
        self.frame_duration = 1 / self.frame_rate
        self.height = (int)(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = (int)(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.shape = [self.height, self.width, 3]

    def release(self):
        del self.video_capture

    def frames(self):
        read_success, image = self.video_capture.read()
        return frames.frames_to_float(image)
    
    def frames_neat(self):
        read_success, image = self.video_capture.read()
        return image
