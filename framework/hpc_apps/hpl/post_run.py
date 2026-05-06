import os
import json


def extract_results(output_file):
    if not os.path.exists(output_file):
        return {"gflops": 0}

    gflops = 0.0

    with open(output_file, "r") as f:
        for line in f:
            if "WR" in line and "Gflops" not in line:
                parts = line.split()
                try:
                    gflops = float(parts[-1])
                except:
                    continue

    return {"gflops": gflops}


def show_summary_all(all_results):
    print("\n")
    print("╔══════════════════════════════════════╗")
    print("║         HPL PERFORMANCE             ║")
    print("╠══════╦══════════════════════════════╣")
    print("║ Iter ║ GFLOPS                       ║")
    print("╠══════╬══════════════════════════════╣")

    for i, r in enumerate(all_results, 1):
        print(f"║ {str(i).ljust(4)} ║ {str(round(r['gflops'],4)).ljust(28)} ║")

    print("╚══════════════════════════════════════╝\n")


def extract_perf(file):
    data = {"instructions": 0, "cycles": 0, "ipc": 0}

    if not os.path.exists(file):
        return data

    with open(file) as f:
        for line in f:
            if "cpu_core/instructions" in line:
                data["instructions"] = float(line.split()[0].replace(",", ""))
            elif "cpu_core/cycles" in line:
                data["cycles"] = float(line.split()[0].replace(",", ""))

    if data["cycles"] > 0:
        data["ipc"] = data["instructions"] / data["cycles"]

    return data


# -------------------------------
# BOTTLENECK DETECTION
# -------------------------------
def detect_bottleneck(ipc):
    if ipc < 0.6:
        return "Memory"
    elif ipc < 1.2:
        return "Balanced"
    else:
        return "Compute"


# -------------------------------
# WRITE SUMMARY FILE
# -------------------------------
def write_perf_summary(run_dir, i, gflops, ipc):
    bottleneck = detect_bottleneck(ipc)

    summary = f"GFLOPS: {gflops} | IPC: {round(ipc,2)} | Bottleneck: {bottleneck}"

    out_file = f"{run_dir}/profiling/perf_{i}.summary.txt"

    with open(out_file, "w") as f:
        f.write(summary + "\n")


# -------------------------------
# PERF HISTORY (SEPARATE FILE)
# -------------------------------
def append_perf_history(data, app="hpl"):

    FILE = f"performance/data/perf_{app}_history.json"

    os.makedirs("performance/data", exist_ok=True)

    if os.path.exists(FILE):
        with open(FILE) as f:
            history = json.load(f)
    else:
        history = []

    history.append(data)

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)


def append_hpl_history(gflops):
    FILE = "performance/data/hpl_history.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            history = json.load(f)
    else:
        history = []

    history.append({"gflops": gflops})

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)


def append_hpl_iterations(values):
    FILE = "performance/data/hpl_iterations.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            data = json.load(f)
    else:
        data = []

    data.append({"values": values})

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def append_hpl_avg(avg):
    FILE = "performance/data/hpl_avg.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            data = json.load(f)
    else:
        data = []

    data.append({"avg": avg})

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def store_results(run_dir, results, job_ids):
    results_dir = os.path.join(run_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    with open(f"{results_dir}/job_id.json", "w") as f:
        json.dump(job_ids, f, indent=4)

    with open(f"{results_dir}/summary.json", "w") as f:
        json.dump(results, f, indent=4)