import subprocess
import os

# python subprocess to call on upload.py

def upload_firmware(board_name: str):
    print(f"[UPLOAD] Flashing firmware for {board_name}...")

    # Construct path to Rivanna3/upload.py
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../Rivanna3/upload_old.py")
    )

    # Clean up board name (PowerBoard → power)
    cli_board_arg = board_name.lower().replace("board", "")

    # Build command
    cmd = ["python3", script_path, cli_board_arg, "--hil"]

    try:
        subprocess.run(cmd, check=True)
        print("[UPLOAD] Success")
    except subprocess.CalledProcessError as e:
        print(f"[UPLOAD ERROR] Upload failed with code {e.returncode}")
        raise
