# System Detective (CIE-1)

## Setup (Windows PowerShell)
    py -3 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r Requirements.txt

The C locality benchmark requires GCC. MinGW GCC is sufficient on Windows;
WSL/Ubuntu users can install the Linux tools with:

    sudo apt update && sudo apt install -y strace sysstat htop gcc python3-venv procps
    python3 -m venv .venv && source .venv/bin/activate
    pip install -r Requirements.txt

## Run in order
    python Capture.py          # Checkpoint 1: saves outputs/*.txt
    python Locality.py         # Checkpoint 2: saves outputs/locality.json
    python -m streamlit run Dashboard.py  # Checkpoint 3: live dashboard

On Windows, the Linux-only commands in `Capture.py` are skipped automatically;
the dashboard still reports CPU, memory, process, and locality data.