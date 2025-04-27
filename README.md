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

---

##  App Conversion Guide

This guide explains how to convert the **Virtual RTC Application** into a standalone executable application using **PyInstaller**. By following this guide, you can package the Python-based application into a distributable format that can run on systems without requiring Python or dependencies to be pre-installed.

### 📦 Prerequisites

Before converting the application, ensure the following are installed on your system:

1. Python: Version 3.8 or higher.
2. Pip: Python's package manager.
3. PyInstaller: Install it using the following command:

```bash
pip install pyinstaller
```

### 🔧 Steps to Convert the Application

1. Install Dependencies:
Ensure all required dependencies are installed. Use the requirements.txt file to install them:

```bash
pip install -r requirements.txt
```
2. Navigate to the Project Directory:
Open a terminal or command prompt and navigate to the directory containing the application files:
```bash
cd c:\Users\Desktop\git\virtual_RTC_application
```

3. Create the Executable for the Client:
Run the following command to package the client.py file into an executable:
```bash
pyinstaller --onefile --windowed --icon=img/ppico.ico --name="LinkHub" client.py
```

- ```--onefile:``` Packages everything into a single executable file.
- ```--windowed:``` Ensures the application runs without a console window (useful for GUI applications).
- ```--icon=img/ppico.ico```: Specifies the path to the icon file. Here, it assumes the ppico.ico file is inside the img folder relative to the project directory.
- ```--name="LinkHub"```: Sets the name of the output executable to LinkHub.
- ```client.py```: The main Python file to be converted into an executable.

**⚠️Note**: Before converting the fle to application make sure that the enter the **SERVER IP** address in **Client.py** file then only application could connection the server. 
---

## Demo

<img src="img/Screenshot 2025-04-17 141513.png" alt="app icon" width=400 heigth=200>

<img src="img/Screenshot 2025-04-17 141839.png" alt="main GUI" width=400 heigth=200>

<img src="img/Screenshot 2025-04-03 072204.png" alt="create meeting GUI" width=400 heigth=200>

<img src="img/Screenshot 2025-04-17 142423.png" alt="connect meeting GUI" width=400 heigth=200>

<img src="img/Screenshot 2025-04-03 072638.png" alt="meeting img1" width=400 heigth=200>

<img src="img/Screenshot 2025-04-20 134102.png" alt="meeting img2" width=400 heigth=200>

---
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

---

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

---

## 🧑‍💻 Technologies Used
- **Python**: Core programming language.

- **Socket Programming**: For real-time communication.

- **OpenCV**: For video capture, processing, and display.

- **PyAudio**: For audio capture and playback.

- **ttkbootstrap**: For modern UI elements.

- **Zlib + Base64**: For compression and encoding of media streams.

- **Threading**: For handling concurrent client connections.

---

## 🤝 Contributing
- Contributions are welcome!

- Fork the repository.

- Create a new branch for your feature or fix.

- Commit your changes.

- Submit a pull request with a detailed description.

---

## 📄 License
- This project is licensed under the MIT License.
- Feel free to use, modify, and distribute this software under the terms of the license.
