# Virtual RTC (Real-Time Communication) Application

**Virtual RTC** is a Python-based video conferencing tool that allows users to create and join virtual meetings with real-time audio and video streaming. It simulates the core functionalities of popular video conferencing platforms, focusing on simplicity, flexibility, and performance.

---

## 🚀 Features

- **Real-Time Video Streaming**: Capture and transmit video from webcams to other participants.
- **Real-Time Audio Streaming**: Capture and transmit audio from microphones with low latency.
- **Meeting Management**: Create and join meetings with unique IDs.
- **User-Friendly Interface**: Modern GUI built with `ttkbootstrap` for ease of use.
- **Dynamic Audio Mixing**: Mix audio streams from multiple participants.
- **Error Handling**: Graceful handling of network interruptions and corrupted data.
- **Customizable Themes**: Choose from multiple themes for the application interface.

---

## 🖥️ System Requirements

- **Operating System**: Windows 10 or higher (adaptable for Linux/MacOS).
- **Python Version**: Python 3.8 or higher
- **Hardware**:
  - Webcam and microphone
  - Stable internet connection (≥ 5 Mbps upload/download)

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/virtual-rtc.git
   cd virtual-rtc

2. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Run the server**:
    ```bash
    python server.py

4. **Run the client**:
    ```bash
    python client.py

## ▶️ Usage

1. **Start the Server**
    - Run server.py to start the video and audio servers.
    - The server listens for incoming connections on separate ports for video and audio.

    ```bash
    python server.py


2. **Create a Meeting**
    - Run client.py:

    ```bash
    python client.py
    ```
    - Click "Create a Meeting" and enter your name.

3. **Join a Meeting**
    - Open the client application.

    - Click "Join a Meeting", enter the meeting ID and password, and connect.

4. **In-Meeting Controls**
    - Toggle Audio/Video: Mute/unmute audio or start/stop video.

    - End Meeting: Click "End Meeting" to leave the session.

## 📁 File Structure

    virtual_RTC_application/
    │
    ├── server.py           Server-side implementation for audio and video streaming
    ├── client.py           Client-side implementation with GUI
    ├── img/                Image assets for the GUI
    │   ├── video-camera.png
    │   ├── audio.png
    │   ├── add.png
    │   ├── information.png
    │   └── ppico.ico
    ├── requirements.txt    List of dependencies
    └── README.md           Documentation

## 🧑‍💻 Technologies Used
- **Python**: Core programming language.

- **Socket Programming**: For real-time communication.

- **OpenCV**: For video capture, processing, and display.

- **PyAudio**: For audio capture and playback.

- **ttkbootstrap**: For modern UI elements.

- **Zlib + Base64**: For compression and encoding of media streams.

- **Threading**: For handling concurrent client connections.



## 🤝 Contributing
- Contributions are welcome!

- Fork the repository.

- Create a new branch for your feature or fix.

- Commit your changes.

- Submit a pull request with a detailed description.

## 📄 License
- This project is licensed under the MIT License.
- Feel free to use, modify, and distribute this software under the terms of the license.