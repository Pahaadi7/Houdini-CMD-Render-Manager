# Houdini Command Line Cache/Renderer

## Overview

The **Houdini Command Line Cache/Renderer** is a Python-based tool designed to streamline the rendering workflow for Houdini projects. With a user-friendly graphical interface, it allows users to select, scan, and render supported nodes directly from a Houdini `.hip` file using the Houdini Command-Line Tool (`hcmd.exe`).

## Features

- **Node Detection**: Automatically scans and lists supported nodes (`filecache::2.0`, `usdrender_rop`) from a Houdini project file.
- **Rendering Automation**: Start rendering directly from the UI for the selected node.
- **Progress Tracking**: Displays real-time progress updates and logs.
- **Error Handling**: Includes robust error management during rendering and node detection.
- **Process Cleanup**: Cancels rendering tasks and terminates associated processes when needed.

## Prerequisites

- **Houdini**: A valid installation of Houdini with access to the Houdini Command-Line Tool (`hcmd.exe`).
- **Python 3.x**: Ensure Python is installed on your system.
- **Dependencies**: The following Python libraries are required:
  - `tkinter`
  - `ttkthemes`
  - `subprocess`
  - `json`
  - `threading`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/houdini-command-line-renderer.git
   ```
2. Navigate to the project directory:
   ```bash
   cd houdini-command-line-renderer
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Generate a `requirements.txt` file with the required dependencies if needed.)*
   
requirements.txt=  
                  tkinter
                  ttkthemes
                  subprocess32
                  json5
                  threading

   

## Usage

1. Run the script:
   ```bash
   python flip_sim_tool_commandLine_withConsole_02.py
   ```
2. Use the graphical interface to:
   - Browse and select a `.hip` file.
   - Scan for supported nodes.
   - Start rendering by selecting a node from the list.

3. Check the progress bar and logs for updates during rendering.

### Cancel Rendering
If needed, you can cancel an ongoing render task using the **Cancel Render** button. This will also terminate associated processes (`husk.exe`).

## Supported Node Types

The application supports the following Houdini node types for rendering:
- `filecache::2.0`
- `usdrender_rop`

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
