import shutil
import subprocess
import threading
import time

import cv2
import numpy as np

from grinder_scheduler.models import VideoStreamState


class FFmpegMediaStreamer:
    def __init__(self, stream_url, fps=8, width=1280, enabled=True):
        self._lock = threading.Lock()
        self._stream_url = stream_url
        self._fps = max(1, int(fps))
        self._target_width = max(320, int(width))
        self._enabled = enabled and bool(stream_url)
        self._ffmpeg = shutil.which("ffmpeg")
        self._process = None
        self._last_frame_time = 0.0
        self._state = VideoStreamState(stream_url=stream_url, codec="h264")

    def push_frames(self, left, right):
        if not self._enabled or self._ffmpeg is None or left is None:
            return
        now = time.time()
        if now - self._last_frame_time < 1.0 / float(self._fps):
            return
        self._last_frame_time = now
        frame = left if right is None else np.hstack((left, right))
        scale = self._target_width / float(frame.shape[1])
        height = max(2, int(round(frame.shape[0] * scale)))
        frame = cv2.resize(frame, (self._target_width, height), interpolation=cv2.INTER_AREA)
        with self._lock:
            self._ensure_process(frame.shape[1], frame.shape[0])
            if self._process is None:
                return
            try:
                self._process.stdin.write(frame.tobytes())
                self._process.stdin.flush()
                self._state.width = frame.shape[1]
                self._state.height = frame.shape[0]
                self._state.online = True
                self._state.last_update_utc = int(now)
            except Exception:
                self._stop_locked()

    def get_state(self):
        with self._lock:
            return VideoStreamState(**self._state.__dict__)

    def close(self):
        with self._lock:
            self._stop_locked()

    def _ensure_process(self, width, height):
        if self._process is not None and self._process.poll() is None:
            return
        if self._ffmpeg is None:
            return
        command = [
            self._ffmpeg,
            "-loglevel",
            "error",
            "-re",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgr24",
            "-s",
            "{}x{}".format(width, height),
            "-r",
            str(self._fps),
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "zerolatency",
            "-pix_fmt",
            "yuv420p",
        ]
        if self._stream_url.startswith("rtmp"):
            command.extend(["-f", "flv", self._stream_url])
        else:
            command.extend(["-f", "rtsp", "-rtsp_transport", "tcp", self._stream_url])
        self._process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _stop_locked(self):
        if self._process is None:
            self._state.online = False
            return
        try:
            if self._process.stdin:
                self._process.stdin.close()
        except Exception:
            pass
        try:
            self._process.terminate()
        except Exception:
            pass
        self._process = None
        self._state.online = False
