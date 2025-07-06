import subprocess

def run_in_background():
    return subprocess.Popen(["python", "live_run.py"])

def stop_live_process():
    import os
    os.system("taskkill /f /im python.exe")  # Windows-specific
    return True

