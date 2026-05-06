'''import os
import shutil
import subprocess
import time
from datetime import datetime

from core.config_loader import load_all_configs
from core.sbatch_generator import generate_sbatch_script
from hpc_apps.stream.post_run import extract_results, analyze_and_display_stream, store_results
from hpc_apps.stream.post_run import analyze_and_display_stream

BASE_DIR = os.path.expanduser("~/STREAM")


def case_banner(case, stage, color_code="\033[96m"):
    text = f"{case}  |  {stage}"
    width = len(text) + 10
    line = "*" * width

    print("\n" + color_code + line)
    print("*" + text.center(width - 2) + "*")
    print(line + "\033[0m\n")


def get_run_dir():
    base = os.path.expanduser("~/hpc_runs/stream")
    os.makedirs(base, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(base, f"case_setup_{ts}")

    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def setup(run_dir):
    os.makedirs(f"{run_dir}/bin", exist_ok=True)
    os.makedirs(f"{run_dir}/results", exist_ok=True)


def is_binary_present():
    return os.path.exists(f"{BASE_DIR}/stream")


def generate_build_sbatch(run_dir):
    cmd = """
echo "===== BUILD START ====="

cd ~

if [ ! -d "STREAM" ]; then
    git clone https://github.com/jeffhammond/STREAM.git
fi

cd ~/STREAM

if [ ! -f "stream" ]; then
    echo "Building STREAM..."
    gcc -O3 -fopenmp stream.c -o stream
else
    echo "✔ Binary exists → skipping build"
fi

cp ~/STREAM/stream {run_dir}/bin/

echo "===== BUILD END ====="
""".replace("{run_dir}", run_dir)

    script = generate_sbatch_script(
        "stream_build",
        f"{run_dir}/build.out",
        1,
        "00:02:00",
        cmd,
        "~"
    )

    path = f"{run_dir}/build.sbatch"
    with open(path, "w") as f:
        f.write(script)

    return path


def generate_run_sbatch(cfg, run_dir):
    threads = cfg["stream"]["runtime"]["threads"]

    cmd = f"""
echo "===== RUN START ====="
export OMP_NUM_THREADS={threads}
./stream
echo "===== RUN END ====="
"""

    script = generate_sbatch_script(
        "stream_run",
        f"{run_dir}/stream.out",
        1,
        cfg["stream"]["runtime"]["time"],
        cmd,
        f"{run_dir}/bin"
    )

    path = f"{run_dir}/run.sbatch"
    with open(path, "w") as f:
        f.write(script)

    return path

def submit(script):
    res = subprocess.run(["sbatch", script], capture_output=True, text=True)
    return res.stdout.strip().split()[-1]


def wait_for_job(job_id):
    while True:
        res = subprocess.run(
            ["squeue", "-j", job_id],
            capture_output=True,
            text=True
        )

        if job_id not in res.stdout:
            break

        time.sleep(1)


def collect_logs(run_dir):
    results_dir = os.path.join(run_dir, "results")

    if os.path.exists(f"{run_dir}/build.out"):
        shutil.copy(f"{run_dir}/build.out", f"{results_dir}/build.log")

    if os.path.exists(f"{run_dir}/stream.out"):
        shutil.copy(f"{run_dir}/stream.out", f"{results_dir}/run.log")

def print_build_config(cfg):
    b = cfg["build"]

    print("\n" + "="*50)
    print(" BUILD CONFIGURATION (YAML)")
    print("="*50)

    print("Modules   :", ", ".join(b["environment"]["modules"]))
    print("Node      :", b["execution"]["node"])
    print("Workdir   :", b["execution"]["workdir"])
    print("Compiler  :", b["compile"]["compiler"])
    print("BLAS      :", b["compile"]["blas"])

    if "metadata" in b:
        print("Scheduler :", b["metadata"].get("scheduler", "NA"))

    print("="*50 + "\n")

def print_stream_config(cfg):
    s = cfg["stream"]

    print("\n" + "="*50)
    print(" STREAM CONFIGURATION (YAML)")
    print("="*50)

    print("Benchmark :", s["benchmark"]["name"], f"(v{s['benchmark']['version']})")
    print("Threads   :", s["runtime"]["threads"])
    print("Array Size:", s["problem"]["array_size"])
    print("NTIMES    :", s["problem"]["ntimes"])
    print("Time      :", s["runtime"]["time"])

    print("="*50 + "\n")

def execute():
    cfg = load_all_configs("stream")
    print_build_config(cfg)
    print_stream_config(cfg)

    run_dir = get_run_dir()
    setup(run_dir)

    case = os.path.basename(run_dir)
    shortcut = os.path.join(os.getcwd(), case)

    if os.path.exists(shortcut):
        if os.path.islink(shortcut):
            os.remove(shortcut)

    os.symlink(run_dir, shortcut)

    print(f"Shortcut created: ./{case}\n")

    case_banner(case, "SETUP")
    print(f"{run_dir}\n")

    build_id = None

    if not is_binary_present():
        case_banner(case, "BUILD")

        build_script = generate_build_sbatch(run_dir)
        build_id = submit(build_script)

        print(f"Job Submitted: {build_id}\n")

        wait_for_job(build_id)
        print("✔ BUILD COMPLETED\n")

    else:
        case_banner(case, "BUILD")
        print("✔ Binary exists → Skipping build\n")
        shutil.copy(f"{BASE_DIR}/stream", f"{run_dir}/bin/")

    case_banner(case, "RUN")

    run_script = generate_run_sbatch(cfg, run_dir)
    run_id = submit(run_script)

    print(f"Job Submitted: {run_id}\n")

    wait_for_job(run_id)
    print("✔ RUN COMPLETED\n")

    collect_logs(run_dir)
    print("Logs stored in results/\n")

    results = extract_results(f"{run_dir}/stream.out")

    analyze_and_display_stream(results)

    store_results(
        run_dir,
        results,
        {
            "build_job_id": build_id,
            "run_job_id": run_id
        }
    )


if __name__ == "__main__":
    execute()'''


import os
import shutil
import subprocess
import time
from datetime import datetime

from core.sbatch_generator import generate_sbatch_script
from hpc_apps.stream.post_run import (
    extract_results,
    store_results,
    append_stream_history,
    append_stream_avg,
    append_iteration_run,
    extract_perf,
    append_perf_history,   
    show_summary_all
)
from performance.graphs import plot_local_iterations
from hpc_apps.stream.post_run import write_perf_summary
BASE_DIR = os.path.expanduser("~/STREAM")


def case_banner(case, stage):
    COLOR = "\033[96m"
    RESET = "\033[0m"
    WIDTH = 50
    text = f"{case} | {stage}"

    print("\n" + COLOR + "*" * (WIDTH + 2))
    print("*" + text.center(WIDTH) + "*")
    print("*" * (WIDTH + 2) + RESET + "\n")


def get_run_dir(parser):
    base_dir = parser.get_paths()["run_dir"]
    os.makedirs(base_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(base_dir, f"case_{ts}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def setup(run_dir):
    os.makedirs(f"{run_dir}/bin", exist_ok=True)
    os.makedirs(f"{run_dir}/results", exist_ok=True)
    os.makedirs(f"{run_dir}/profiling", exist_ok=True)

def is_binary_present():
    return os.path.exists(f"{BASE_DIR}/stream")


def generate_build_sbatch(parser, run_dir):
    cmd = f"""
cd ~

# clone if not exists
if [ ! -d "STREAM" ]; then
    git clone https://github.com/jeffhammond/STREAM.git
fi

cd ~/STREAM

# build if not exists
if [ ! -f "stream" ]; then
    echo "Building STREAM..."
    gcc -O3 -fopenmp stream.c -o stream
else
    echo "✔ Binary exists → skipping build"
fi

# copy binary
cp ~/STREAM/stream {run_dir}/bin/
"""

    return generate_sbatch_script(
        job_name="stream_build",
        output_file=f"{run_dir}/build.out",
        nodes=1,
        ntasks=1,
        time_limit="00:02:00",
        command=cmd,
        workdir="~"
    )

def generate_run_sbatch(parser, run_dir, i, profile=False):
    runtime = parser.get_runtime()

    if profile:
        cmd = f"""
cd {run_dir}/bin
export OMP_NUM_THREADS={runtime["threads"]}

echo "===== RUN {i} (PROFILE) ====="
perf stat -o {run_dir}/profiling/perf_{i}.out \
./stream > {run_dir}/run_{i}.out
"""
    else:
        cmd = f"""
cd {run_dir}/bin
export OMP_NUM_THREADS={runtime["threads"]}

echo "===== RUN {i} ====="
./stream > {run_dir}/run_{i}.out
"""

    return generate_sbatch_script(
        job_name=f"stream_run_{i}",
        output_file=f"{run_dir}/stream_{i}.out",
        nodes=1,
        ntasks=1,
        time_limit=runtime["time"],
        command=cmd,
        workdir="~"
    )

def submit(script_path):
    res = subprocess.run(["sbatch", script_path], capture_output=True, text=True)
    return res.stdout.strip().split()[-1]


def wait_for_job(job_id):
    while True:
        res = subprocess.run(["squeue", "-j", job_id], capture_output=True, text=True)
        if job_id not in res.stdout:
            break
        time.sleep(1)

def stream_log(file, job_id):
    while not os.path.exists(file):
        time.sleep(1)

    with open(file, "r") as f:
        f.seek(0, 2)

        while True:
            line = f.readline()

            if line:
                print(line, end="")
            else:
                res = subprocess.run(
                    ["squeue", "-j", job_id],
                    capture_output=True,
                    text=True
                )

                if job_id not in res.stdout:
                    break

                time.sleep(0.5)

def collect_logs(run_dir):
    results_dir = os.path.join(run_dir, "results")

    if os.path.exists(f"{run_dir}/build.out"):
        shutil.copy(f"{run_dir}/build.out", f"{results_dir}/build.log")

    for file in os.listdir(run_dir):
        if file.startswith("stream_") and file.endswith(".out"):
            shutil.copy(
                os.path.join(run_dir, file),
                os.path.join(results_dir, file.replace(".out", ".log"))
            )

    

def execute(parser, mode,profile=False):

    print("[STREAM] Execution started")

    run_dir = get_run_dir(parser)
    setup(run_dir)

    case = os.path.basename(run_dir)
    print(f"Run directory: {run_dir}")

    runtime = parser.get_runtime()
    iterations = runtime.get("iterations", 1)

    build_id = None

    if mode in ["build", "all"]:
        case_banner(case, "BUILD")

        if not is_binary_present():
            script_path = f"{run_dir}/build.sbatch"
            with open(script_path, "w") as f:
                f.write(generate_build_sbatch(parser, run_dir))

            build_id = submit(script_path)
            print(f"Job Submitted (BUILD): {build_id}")
            stream_log(f"{run_dir}/build.out", build_id)
            wait_for_job(build_id)
            print("✔ BUILD DONE")
        else:
            shutil.copy(f"{BASE_DIR}/stream", f"{run_dir}/bin/")
            print("✔ Binary exists → Skipped build")

    if mode in ["run", "all"]:
        case_banner(case, "RUN")

        all_results = []

        for i in range(iterations):
            print(f"\n--- Iteration {i+1}/{iterations} ---")

            script_path = f"{run_dir}/run_{i}.sbatch"
            with open(script_path, "w") as f:
                f.write(generate_run_sbatch(parser, run_dir,i,profile))

            run_id = submit(script_path)
            print(f"Job Submitted (RUN {i+1}): {run_id}")
            stream_log(f"{run_dir}/stream_{i}.out", run_id)
            wait_for_job(run_id)
            print(f"✔ RUN {i+1} DONE")

            results = extract_results(f"{run_dir}/run_{i}.out")

            append_stream_history(results["Triad"])
            if profile:
                perf_res = extract_perf(f"{run_dir}/profiling/perf_{i}.out")
                combined = {**results, **perf_res}
                append_perf_history({
                   "ipc": perf_res["ipc"],
                  "triad": results["Triad"]
                })
                write_perf_summary(run_dir,i,results["Triad"],perf_res["ipc"])
                all_results.append(combined)
            else:
                all_results.append(results)

        show_summary_all(all_results)

        triads = [r["Triad"] for r in all_results]
        append_iteration_run(triads)
        avg = sum(triads) / len(triads)
        append_stream_avg(avg)
        collect_logs(run_dir)
        print("Logs stored in results/")
        store_results(
            run_dir,
            {"iterations": all_results, "average": avg},
            {"build_job_id": build_id}
        )
        link_name = case  
        current_dir = os.getcwd()

        link_path = os.path.join(current_dir, link_name)
        if os.path.islink(link_path) or os.path.exists(link_path):
            os.remove(link_path)
        os.symlink(run_dir, link_path)

        print(f"\n Shortcut created: {link_name}")
        print(f"Now you can run: cd {link_name}\n")