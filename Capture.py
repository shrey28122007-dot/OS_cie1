"""capture.py - Checkpoint 1: run system commands and save their real output.
Usage:  python3 capture.py
Each command's output is saved to outputs/<name>.txt with a header
(command, timestamp, user, host) so it can be reproduced and screenshotted.
"""
import subprocess, datetime, getpass, socket, pathlib, shutil

OUT = pathlib.Path(__file__).parent / "outputs"
OUT.mkdir(exist_ok=True)

COMMANDS = {
    "01_lscpu":       ["lscpu"],
    "02_free":        ["free", "-h"],
    "03_meminfo":     ["head", "-n", "10", "/proc/meminfo"],
    "04_top":         ["top", "-b", "-n", "1"],
    "05_ps_threads":  ["ps", "-eLf"],
    "06_ps_states":   ["ps", "-eo", "pid,stat,comm", "--sort=-%cpu"],
    "07_strace":      ["strace", "-c", "ls", "/"],   # summary goes to stderr
    "08_vmstat":      ["vmstat", "1", "5"],
}

def main():
    for name, cmd in COMMANDS.items():
        header = (f"$ {' '.join(cmd)}\n"
                  f"# time: {datetime.datetime.now().isoformat(timespec='seconds')}\n"
                  f"# user: {getpass.getuser()}@{socket.gethostname()}\n\n")
        if shutil.which(cmd[0]) is None:
            body = f"[SKIPPED] '{cmd[0]}' not installed. Try: sudo apt install {cmd[0]}\n"
        else:
            r = subprocess.run(cmd, capture_output=True, text=True)
            body = r.stdout + (r.stderr if r.stderr else "")
        (OUT / f"{name}.txt").write_text(header + body)
        print(f"===== {name} =====")
        print("\n".join((header + body).splitlines()[:15]))
        print("...\n")
    print(f"Saved to {OUT}/  - take labelled screenshots of your terminal too.")

if __name__ == "__main__":
    main()