import argparse
import webbrowser
import threading
import time

from .main import app


def open_browser(url):
    def open_browser_thread():
        time.sleep(0.2)
        try:
            webbrowser.open(url)
        except webbrowser.Error:
            print("Open browser failed")

    t = threading.Thread(target=open_browser_thread)
    t.daemon = True
    t.start()


def parse_args():
    parser = argparse.ArgumentParser(description="Example program")

    parser.add_argument("--host", help="Host to connect to", default="127.0.0.1")
    parser.add_argument("--port", type=int, help="Port to use", default=8022)
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser")

    return parser.parse_args()


def main():

    import uvicorn

    args = parse_args()
    if not args.no_browser:
        open_browser(f"http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
