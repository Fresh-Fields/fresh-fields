import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import threading


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or event.src_path.endswith(".mjs"):
            return
        print(f"File {event.src_path} has been modified. Running the command...")
        # Replace the command below with the command you want to run
        subprocess.run(["npm run build"], cwd="./vite", shell=True)
        time.sleep(1)


def watch():
    print("Watching ./vite for changes!")
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path="./vite", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


def start():
    thread = threading.Thread(target=watch, daemon=True)
    thread.start()
