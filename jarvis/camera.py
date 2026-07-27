from __future__ import annotations

import threading


_camera_thread: threading.Thread | None = None


def open_camera() -> str:
    """Open the default webcam with OpenCV in a background thread."""
    global _camera_thread
    if _camera_thread and _camera_thread.is_alive():
        return "Camera is already open, sir."

    _camera_thread = threading.Thread(target=_camera_loop, daemon=True)
    _camera_thread.start()
    return "I opened the camera, sir. Press Q or Escape in the camera window to close it."


def _camera_loop() -> None:
    try:
        import cv2
    except Exception:
        print("OpenCV is not installed. Run: pip install opencv-python")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open the camera.")
        return

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Could not read from the camera.")
                break

            cv2.imshow("JARVIS Camera", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
