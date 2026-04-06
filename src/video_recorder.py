import pybullet as p
import time
from datetime import datetime

class OptimusVideoRecorder:
    def __init__(self, filename=None):
        self.filename = filename or f"optimus_duka_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4"
        self.recording = False
    
    def start(self, fps=60, width=1280, height=720):
        p.startStateLogging(p.STATE_LOGGING_VIDEO_MP4, self.filename)
        # أو لجودة أعلى:
        # p.startVideoRecording(self.filename, fps=fps, width=width, height=height)
        self.recording = True
        print(f"🎥 Recording started: {self.filename}")
    
    def stop(self):
        if self.recording:
            p.stopStateLogging()
            # p.stopVideoRecording()
            self.recording = False
            print("✅ Recording saved!")

# استخدام في Orchestrator
# recorder = OptimusVideoRecorder()
# recorder.start()
# ... run cycles ...
# recorder.stop()
