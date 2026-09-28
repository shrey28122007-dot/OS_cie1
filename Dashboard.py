"""dashboard.py - Checkpoint 3: live system dashboard.
Usage:  streamlit run dashboard.py
Every value is read from the machine on each refresh; nothing is hardcoded.
"""
import json, subprocess, platform, time, sys, pathlib
import psutil, pandas as pd, streamlit as st

HERE = pathlib.Path(__file__).parent
LOC = HERE / "outputs" / "locality.json"

st.set_page_config(page_title="System Detective", layout="wide")
st.title("System Detective - live dashboard")
refresh = st.sidebar.checkbox("Auto-refresh", True)
interval = st.sidebar.slider("Refresh interval (s)", 2, 30, 5)

def read_lscpu():
    try:
        out = subprocess.run(["lscpu"], capture_output=True, text=True).stdout
    except FileNotFoundError:
        return {}
    d = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d

# ---- CPU / ISA ----
st.header("1. CPU / ISA")
cpu = read_lscpu()
c1, c2, c3, c4 = st.columns(4)
c1.metric("ISA (platform.machine)", platform.machine())
c2.metric("Model", cpu.get("Model name", "n/a"))
c3.metric("Logical CPUs", psutil.cpu_count(logical=True))
c4.metric("CPU use now", f"{psutil.cpu_percent(interval=0.5)} %")
cache_keys = ["L1d cache", "L1i cache", "L2 cache", "L3 cache"]
st.write({k: cpu.get(k, "n/a") for k in cache_keys})

# ---- Memory ----
st.header("2. Memory")
vm = psutil.virtual_memory()
m1, m2, m3 = st.columns(3)
m1.metric("Total", f"{vm.total / 2**30:.2f} GiB")
m2.metric("Used", f"{vm.used / 2**30:.2f} GiB")
m3.metric("Available", f"{vm.available / 2**30:.2f} GiB")
st.progress(vm.percent / 100, text=f"{vm.percent}% used")

# ---- Top 5 processes ----
st.header("3. Top 5 processes by CPU")
procs = list(psutil.process_iter())
for p in procs:
    try: p.cpu_percent(None)          # prime the counters
    except (psutil.NoSuchProcess, psutil.AccessDenied): pass
time.sleep(0.5)
rows = []
for p in procs:
    try:
        rows.append({"PID": p.pid, "Name": p.name(), "State": p.status(),
                     "CPU %": p.cpu_percent(None), "Mem %": round(p.memory_percent(), 2)})
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
top5 = pd.DataFrame(rows).sort_values("CPU %", ascending=False).head(5)
st.dataframe(top5, hide_index=True, use_container_width=True)
st.caption("psutil states: running=R, sleeping=S, disk-sleep=D, zombie=Z, stopped=T")

# ---- Locality ----
st.header("4. Locality experiment")
if st.button("Run locality experiment now"):
    with st.spinner("Running locality.py ..."):
        subprocess.run([sys.executable, str(HERE / "locality.py")], check=True)
    st.rerun()
if LOC.exists():
    data = json.loads(LOC.read_text())
    st.caption(f"Measured {data['timestamp']} on {data['machine']}, N={data['N']}")
    for label in ("numpy", "c"):
        block = data.get(label)
        if not block:
            continue
        df = pd.DataFrame(block["runs"])
        df.index = range(1, len(df) + 1)
        df["col/row"] = (df["col"] / df["row"]).round(2)
        st.subheader(label.upper())
        st.dataframe(df, use_container_width=True)
        st.bar_chart(df[["row", "col"]])
        st.write(f"Mean row: {df['row'].mean():.4f}s | Mean col: {df['col'].mean():.4f}s")
else:
    st.info("No results yet. Click the button or run: python3 locality.py")

if refresh:
    time.sleep(interval)
    st.rerun()