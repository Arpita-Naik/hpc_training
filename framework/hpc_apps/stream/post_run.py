import os
import json


def extract_results(output_file):
    if not os.path.exists(output_file):
        return {"Copy": 0, "Scale": 0, "Add": 0, "Triad": 0}

    results = {}

    with open(output_file) as f:
        for line in f:
            if "Copy:" in line:
                results["Copy"] = float(line.split()[1])
            elif "Scale:" in line:
                results["Scale"] = float(line.split()[1])
            elif "Add:" in line:
                results["Add"] = float(line.split()[1])
            elif "Triad:" in line:
                results["Triad"] = float(line.split()[1])

    results.setdefault("Copy", 0)
    results.setdefault("Scale", 0)
    results.setdefault("Add", 0)
    results.setdefault("Triad", 0)

    return results


def show_summary_all(all_results):

    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                STREAM PERFORMANCE (ALL ITERATIONS)                   ║")
    print("╠══════╦══════════╦══════════╦══════════╦══════════╣")
    print("║ Iter ║ Copy     ║ Scale    ║ Add      ║ Triad    ║")
    print("╠══════╬══════════╬══════════╬══════════╬══════════╣")

    for i, r in enumerate(all_results, 1):
        print(f"║ {str(i).ljust(4)} ║ "
              f"{str(r['Copy']).ljust(8)} ║ "
              f"{str(r['Scale']).ljust(8)} ║ "
              f"{str(r['Add']).ljust(8)} ║ "
              f"{str(r['Triad']).ljust(8)} ║")

    print("╚══════════════════════════════════════════════════════════════════════╝\n")


def append_stream_history(triad):
    FILE = "performance/data/stream_history.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            history = json.load(f)
    else:
        history = []

    history.append({"triad": triad})

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)

def append_iteration_run(values):

    FILE = "performance/data/stream_iterations.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            data = json.load(f)
    else:
        data = []

    data.append({"values": values})

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

        
def append_stream_avg(avg):
    FILE = "performance/data/stream_avg.json"

    if os.path.exists(FILE):
        with open(FILE) as f:
            data = json.load(f)
    else:
        data = []

    data.append({"avg": avg})

    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def extract_perf(file):
    data = {"cycles": 0, "instructions": 0, "ipc": 0}

    if not os.path.exists(file):
        return data

    with open(file) as f:
        for line in f:
            if "cycles" in line:
                data["cycles"] = float(line.split()[0].replace(",", ""))
            elif "instructions" in line:
                data["instructions"] = float(line.split()[0].replace(",", ""))

    if data["cycles"] > 0:
        data["ipc"] = data["instructions"] / data["cycles"]

    return data

def append_perf_history(data):
    FILE = "performance/data/perf_history.json"

    os.makedirs("performance/data", exist_ok=True)

    if os.path.exists(FILE):
        with open(FILE) as f:
            history = json.load(f)
    else:
        history = []

    history.append(data)

    with open(FILE, "w") as f:
        json.dump(history, f, indent=4)

def detect_bottleneck(ipc):
    if ipc < 0.6:
        return "Memory"
    elif ipc < 1.2:
        return "Balanced"
    else:
        return "Compute"


def write_perf_summary(run_dir, i, triad, ipc):
    bottleneck = detect_bottleneck(ipc)

    summary = f"Triad: {triad} | IPC: {round(ipc, 2)} | Bottleneck: {bottleneck}"

    out_file = f"{run_dir}/profiling/perf_{i}.summary.txt"
    with open(out_file, "w") as f:
        f.write(summary + "\n")

    #print(summary) 

def store_results(run_dir, results, job_ids):
    results_dir = os.path.join(run_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    with open(f"{results_dir}/job_id.json", "w") as f:
        json.dump(job_ids, f, indent=4)

    with open(f"{results_dir}/summary.json", "w") as f:
        json.dump(results, f, indent=4)