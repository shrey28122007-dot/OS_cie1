"""locality.py - Checkpoint 2: row-major vs column-major timing.
Usage:  python3 locality.py
Runs a NumPy version and (if gcc exists) the C version, RUNS times each,
and writes every individual run to outputs/locality.json.
"""
import numpy as np, time, json, platform, subprocess, shutil, datetime, pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
N, RUNS = 4096, 5

def run_numpy():
    a = np.ones((N, N), dtype=np.int32)          # C order: rows are contiguous
    a.sum()                                      # warm-up, pages touched
    runs = []
    for _ in range(RUNS):
        t = time.perf_counter()
        s = 0
        for i in range(N):
            s += int(a[i, :].sum())              # contiguous slice
        row = time.perf_counter() - t
        t = time.perf_counter()
        s = 0
        for j in range(N):
            s += int(a[:, j].sum())              # stride of N*4 bytes
        col = time.perf_counter() - t
        runs.append({"row": row, "col": col})
    return {"size_mb": a.nbytes / 1e6, "runs": runs}

def run_c():
    if shutil.which("gcc") is None:
        print("c: skipped (gcc not found)")
        return None
    exe = HERE / ("locality_c.exe" if platform.system() == "Windows" else "locality_c")
    try:
        subprocess.run(
            ["gcc", "-O0", str(HERE / "locality.c"), "-o", str(exe)],
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print(f"c: skipped (gcc could not compile locality.c: {detail})")
        return None
    r = subprocess.run([str(exe), str(N), str(RUNS)], capture_output=True, text=True, check=True)
    runs = []
    for line in r.stdout.splitlines():
        row, col, *_ = line.split()
        runs.append({"row": float(row), "col": float(col)})
    return {"size_mb": N * N * 4 / 1e6, "runs": runs, "flags": "-O0"}

def main():
    result = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "machine": platform.machine(),
        "N": N,
        "numpy": run_numpy(),
        "c": run_c(),
    }
    (OUT / "locality.json").write_text(json.dumps(result, indent=2))
    for label in ("numpy", "c"):
        block = result[label]
        if not block:
            print(f"{label}: skipped (gcc not found)")
            continue
        print(f"--- {label} (N={N}) ---")
        for i, r in enumerate(block["runs"], 1):
            print(f"run {i}: row={r['row']:.4f}s  col={r['col']:.4f}s  ratio={r['col']/r['row']:.2f}x")

if __name__ == "__main__":
    main()