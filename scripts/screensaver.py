#!/usr/bin/python3
import os
import subprocess
import random
import signal
import sys
import time
from setproctitle import setproctitle
from wayfire import WayfireSocket

PROCESS_NAME = "screensaver.py"
setproctitle(PROCESS_NAME)
VID_DIR = os.path.expanduser("~/.local/share/screensaver/")
EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".webm")

sock = WayfireSocket()
processes = []

def cleanup(sig, frame):
    # Determine signal name for logging
    sig_name = signal.Signals(sig).name
    print(f"\nCaught {sig_name}. Killing screensavers...")
    for p in processes:
        try:
            p.terminate()
        except:
            pass
    sys.exit(0)

for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT):
    signal.signal(sig, cleanup)

def get_video():
    videos = [os.path.join(VID_DIR, f) for f in os.listdir(VID_DIR) 
              if f.lower().endswith(EXTENSIONS)]
    return random.choice(videos) if videos else None

def start_screensaver():
    outputs = sock.list_outputs()
    
    for output in outputs:
        video = get_video()
        if not video:
            continue
        
        out_name = output['name']
        unique_title = f"ss_{out_name}"
        print(f"Started ss for {out_name}...")

        cmd = [
            "mpv",
            "--no-stop-screensaver",
            "--fs",
            f"--fs-screen-name={out_name}",
            f"--title={unique_title}",
            "--loop-file=inf",
            video
        ]
        
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        processes.append(p)
        
    #time.sleep(1)
    
if __name__ == "__main__":
    if not os.path.exists(VID_DIR):
        print(f"Directory not found: {VID_DIR}")
        sys.exit(1)
        
    start_screensaver()
    
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            cleanup(signal.SIGINT, None)
