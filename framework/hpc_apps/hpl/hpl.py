'''import os
import shutil
import subprocess
import time
from datetime import datetime

from core.config_loader import load_all_configs
from core.sbatch_generator import generate_sbatch_script
from hpc_apps.hpl.config_generator import generate_hpl_dat
from hpc_apps.hpl.post_run import extract_results, compute_efficiency, show_summary, store_results
from hpc_apps.hpl.post_run import analyze_and_display
BASE_DIR = os.path.expanduser("~/hpl-2.3")

def case_banner(case, stage, color_code="\033[96m"):
    text = f"{case}  |  {stage}"
    width = len(text) + 10

    line = "*" * width

    print("\n" + color_code + line)
    print("*" + text.center(width - 2) + "*")
    print(line + "\033[0m\n")

def print_build_config(cfg):
    print("\n" + "="*50)
    print(" COMMON BUILD CONFIGURATION")
    print("="*50)

    b = cfg["build"]

    print("Modules   :", ", ".join(b["environment"]["modules"]))
    print("Node      :", b["execution"]["node"])
    print("Workdir   :", b["execution"]["workdir"])
    print("Compiler  :", b["compile"]["compiler"])
    print("BLAS      :", b["compile"]["blas"])

    print("="*50 + "\n")


def print_hpl_config(cfg):
    print("\n" + "="*50)
    print(" HPL CONFIGURATION")
    print("="*50)

    print(f"Ns, NB     : {cfg['problem']['Ns']}, {cfg['problem']['NB']}")
    print(f"P x Q      : {cfg['process_grid']['P']} x {cfg['process_grid']['Q']}")
    print(f"Tasks      : {cfg['runtime']['ntasks']}")
    print(f"Time       : {cfg['runtime']['time']}")
    print(f"Iterations : {cfg['execution']['iterations']}")

    print("="*50 + "\n")


def get_run_dir():
    base = os.path.expanduser("~/hpc_runs/hpl")
    os.makedirs(base, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = os.path.join(base, f"case_setup_{ts}")

    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def setup(run_dir):
    os.makedirs(f"{run_dir}/bin", exist_ok=True)
    os.makedirs(f"{run_dir}/lib", exist_ok=True)
    os.makedirs(f"{run_dir}/config", exist_ok=True)
    os.makedirs(f"{run_dir}/results", exist_ok=True)

def is_binary_present():
    return os.path.exists(f"{BASE_DIR}/bin/myarch/xhpl")


def generate_build_sbatch(run_dir):
    cmd = rf"""
echo "===== BUILD START ====="

cd ~

if [ ! -d "hpl-2.3" ]; then
    wget -nc https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz
    tar -xzf hpl-2.3.tar.gz
fi

cd {BASE_DIR}

if [ ! -f "bin/myarch/xhpl" ]; then
    echo " Building HPL..."

    cp setup/Make.Linux_PII_CBLAS Make.myarch

    sed -i 's/^ARCH.*/ARCH = myarch/' Make.myarch
    sed -i 's|^TOPdir.*|TOPdir = {BASE_DIR}|' Make.myarch
    sed -i 's/^CC.*/CC = mpicc -I$(TOPdir)\/include/' Make.myarch
    sed -i 's/^LINKER.*/LINKER = mpicc/' Make.myarch
    sed -i 's/^LAlib.*/LAlib = -lopenblas/' Make.myarch
    sed -i '/mpich/d' Make.myarch

    sed -i '/^ARCHIVER/d' Make.myarch
    sed -i '/^ARFLAGS/d' Make.myarch

    echo 'ARCHIVER = ar' >> Make.myarch
    echo 'ARFLAGS = r' >> Make.myarch

    make arch=myarch

    if [ ! -f "bin/myarch/xhpl" ]; then
        echo "BUILD FAILED"
        exit 1
    fi

else
    echo "✔ Binary exists → skipping build"
fi

cp {BASE_DIR}/bin/myarch/xhpl {run_dir}/bin/
cp {BASE_DIR}/lib/myarch/libhpl.a {run_dir}/lib/

echo "===== BUILD END ====="
"""

    script = generate_sbatch_script(
        "hpl_build",
        f"{run_dir}/build.out",
        1,
        "00:05:00",
        cmd,
        "~"
    )

    path = f"{run_dir}/build.sbatch"
    with open(path, "w") as f:
        f.write(script)

    return path


def generate_run_sbatch(cfg, run_dir):
    h = cfg

    ntasks = h["runtime"]["ntasks"]
    time_limit = h["runtime"]["time"]
    cmd_template = h["run"]["command"]
    run_command = cmd_template.format(ntasks=ntasks)

    cmd = f"""
echo "===== RUN START ====="
{run_command}
echo "===== RUN END ====="
"""

    script = generate_sbatch_script(
        job_name="hpl_run",
        output=f"{run_dir}/hpl.out",
        ntasks=ntasks,
        time=time_limit,
        command=cmd,
        workdir=f"{run_dir}/bin"
    )

    path = f"{run_dir}/run.sbatch"
    with open(path, "w") as f:
        f.write(script)

    return path


def submit(script, dependency=None):
    cmd = ["sbatch"]

    if dependency:
        cmd.append(f"--dependency=afterok:{dependency}")

    cmd.append(script)

    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print("Slurm submission failed")
        print(res.stderr)
        return None

    job_id = res.stdout.strip().split()[-1]

    return job_id

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

    build_out = os.path.join(run_dir, "build.out")
    run_out = os.path.join(run_dir, "hpl.out")

    if os.path.exists(build_out):
        shutil.copy(build_out, os.path.join(results_dir, "build.log"))

    if os.path.exists(run_out):
        shutil.copy(run_out, os.path.join(results_dir, "run.log"))

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

def print_hpl_config(cfg):
    h = cfg["hpl"]

    print("\n" + "="*50)
    print(" HPL CONFIGURATION (YAML)")
    print("="*50)

    print("Benchmark :", h["benchmark"]["name"], f"(v{h['benchmark']['version']})")
    print("Ns, NB    :", h["problem"]["Ns"], ",", h["problem"]["NB"])
    print("Grid      :", h["process_grid"]["P"], "x", h["process_grid"]["Q"])
    print("Tasks     :", h["runtime"]["ntasks"])
    print("Time      :", h["runtime"]["time"])
    print("Iterations:", h["execution"]["iterations"])

    if "metadata" in h:
        print("Scheduler :", h["metadata"].get("scheduler", "NA"))

    print("="*50 + "\n")

def execute():
    cfg = load_all_configs("hpl")

    print_build_config(cfg)
    #print_hpl_config(cfg["hpl"])
    print_hpl_config(cfg)
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

    config_path = f"{run_dir}/config/HPL.dat"
    generate_hpl_dat(cfg["hpl"], config_path)
    shutil.copy(config_path, f"{run_dir}/bin/HPL.dat")

    build_id = None  

    if not is_binary_present():

        case_banner(case, "BUILD")
        build_script = generate_build_sbatch(run_dir)
        build_id = submit(build_script)

        print(f"Job Submitted: {build_id}\n")

        wait_for_job(build_id)
        print("✔ BUILD COMPLETED\n")

        case_banner(case, "RUN")
        run_script = generate_run_sbatch(cfg["hpl"], run_dir)
        run_id = submit(run_script)

        print(f"Job Submitted: {run_id}\n")

    else:
        case_banner(case, "BUILD")
        print("✔ Binary exists → Skipping build\n")

        shutil.copy(f"{BASE_DIR}/bin/myarch/xhpl", f"{run_dir}/bin/")
        shutil.copy(f"{BASE_DIR}/lib/myarch/libhpl.a", f"{run_dir}/lib/")

        case_banner(case, "RUN")
        run_script = generate_run_sbatch(cfg["hpl"], run_dir)
        run_id = submit(run_script)

        print(f"Job Submitted: {run_id}\n")

    wait_for_job(run_id)
    print("✔ RUN COMPLETED\n")

    collect_logs(run_dir)
    print("Logs stored in results/\n")

    results = extract_results(f"{run_dir}/hpl.out")

    theoretical, efficiency = compute_efficiency(
        results["gflops"],
        {"cores": 2, "frequency": 2.5, "flops_per_cycle": 16}
    )

    analyze_and_display(results, theoretical, efficiency)
    store_results(
        run_dir,
        results,
        theoretical,
        efficiency,
        {
            "build_job_id": build_id,
            "run_job_id": run_id
        }
    )

if __name__ == "__main__":
    execute()'''


import os
import subprocess
import time
import shutil
from datetime import datetime
from hpc_apps.hpl.config_generator import generate_hpl_dat
from core.sbatch_generator import generate_sbatch_script
from hpc_apps.hpl.post_run import (
    extract_results,
    show_summary_all,
    append_hpl_history,
    append_hpl_iterations,
    append_hpl_avg,
    store_results,
    extract_perf,          
    append_perf_history,   
    write_perf_summary   
)

BASE_DIR = os.path.expanduser("~/hpl-2.3")


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
    os.makedirs(f"{run_dir}/results", exist_ok=True)
    os.makedirs(f"{run_dir}/profiling", exist_ok=True)
    os.makedirs(f"{run_dir}/bin", exist_ok=True)

def is_binary_present():
    return os.path.exists(f"{BASE_DIR}/bin/myarch/xhpl")


'''def generate_hpl_dat(parser):
    problem = parser.get_problem()
    grid = parser.get_process_grid()

    path = f"{BASE_DIR}/bin/myarch"
    if not os.path.exists(path) or not os.path.exists(f"{path}/xhpl"):
        #raise RuntimeError("HPL not built properly. Cannot generate HPL.dat")
    if not os.path.exists(f"{path}/xhpl"):
        print("HPL binary missing.")
        return

    
    content = f"""HPLinpack benchmark input file
Innovative Computing Laboratory, University of Tennessee
HPL.out      output file name (if any)
6            device out (6=stdout,7=stderr,file)
1            # of problems sizes (N)
{problem["Ns"]}         Ns
1            # of NBs
{problem["NB"]}         NBs
0            PMAP process mapping (0=Row-,1=Column-major)
1            # of process grids (P x Q)
{grid["P"]}            Ps
{grid["Q"]}            Qs
16.0         threshold
1            # of panel fact
0            PFACTs
1            # of recursive stopping criterium
2            NBMINs
1            # of panels in recursion
2            NDIVs
1            # of recursive panel fact.
0            RFACTs
1            # of broadcast
0            BCASTs
1            # of lookahead depth
0            DEPTHs
2            SWAP
64           swapping threshold
0            L1 in
0            U  in
1            Equilibration
8            memory alignment
"""

    with open(f"{path}/HPL.dat", "w") as f:
        f.write(content)'''

def generate_build_sbatch(parser, run_dir):
    cmd = f"""
echo "===== HPL BUILD STAGE ====="

cd ~

# If not present → build
if [ ! -f "$HOME/hpl-2.3/bin/myarch/xhpl" ]; then
    echo "HPL not found → building..."
    
    cd ~
    rm -rf hpl-2.3
    tar -xzf hpl-2.3.tar.gz
    cd hpl-2.3

    cp setup/Make.Linux_PII_CBLAS Make.myarch

    sed -i 's|^ARCH.*|ARCH = myarch|' Make.myarch
    sed -i "s|^TOPdir.*|TOPdir = $HOME/hpl-2.3|" Make.myarch
    sed -i 's|^CC.*|CC = mpicc -I$(TOPdir)/include|' Make.myarch
    sed -i 's|^LINKER.*|LINKER = mpicc|' Make.myarch

    sed -i '/libmpich/d' Make.myarch

    sed -i 's|^LAlib.*|LAlib = -lopenblas|' Make.myarch

    echo "ARCHIVER = ar" >> Make.myarch
    echo "ARFLAGS = r" >> Make.myarch

    make arch=myarch

    if [ ! -f "$HOME/hpl-2.3/bin/myarch/xhpl" ]; then
        echo " BUILD FAILED"
        exit 1
    else
        echo "✔ BUILD SUCCESS"
    fi

else
    echo "✔ HPL already exists → skipping build"
fi
"""

    return generate_sbatch_script(
        job_name="hpl_build",
        output_file=f"{run_dir}/build.out",
        nodes=1,
        ntasks=1,
        time_limit="00:10:00",
        command=cmd,
        workdir="~"
    )

def generate_run_sbatch(parser, run_dir, profile=False):
    runtime = parser.get_runtime()
    execution = parser.get_app_config().get("execution", {})
    iterations = execution.get("iterations", 1)

    if profile:
        cmd = f"""
cd {run_dir}/bin

for i in $(seq 0 {iterations-1})
do
    echo "===== RUN $i (PROFILE) ====="

    perf stat -o {run_dir}/profiling/perf_$i.out \\
    mpiexec --oversubscribe -np {runtime.get("ntasks", 4)} ./xhpl > {run_dir}/run_$i.out
done
"""
    else:
        cmd = f"""
cd {run_dir}/bin

for i in $(seq 0 {iterations-1})
do
    echo "===== RUN $i ====="

    mpiexec --oversubscribe -np {runtime.get("ntasks", 4)} ./xhpl > {run_dir}/run_$i.out
done
"""

    return generate_sbatch_script(
        job_name="hpl_run_all",
        output_file=f"{run_dir}/run_all.out",
        nodes=1,
        ntasks=runtime.get("ntasks", 4),
        time_limit=runtime["time"],
        command=cmd,
        workdir="~"
    )

def submit(script_path):
    res = subprocess.run(["sbatch", script_path], capture_output=True, text=True)
    job_id = res.stdout.strip().split()[-1]
    print(f"Job Submitted: {job_id}")
    return job_id


def wait_for_job(job_id):
    while True:
        res = subprocess.run(["squeue", "-j", job_id], capture_output=True, text=True)
        if job_id not in res.stdout:
            break
        time.sleep(1)

def copy_hpl_artifacts(run_dir):
    src_bin = os.path.join(BASE_DIR, "bin", "myarch")
    src_lib = os.path.join(BASE_DIR, "lib", "myarch")

    dst_bin = os.path.join(run_dir, "bin")
    dst_lib = os.path.join(run_dir, "lib")

    if os.path.exists(src_bin):
        shutil.copytree(src_bin, dst_bin, dirs_exist_ok=True)

    if os.path.exists(src_lib):
        shutil.copytree(src_lib, dst_lib, dirs_exist_ok=True)

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

                # job finished → stop streaming
                if job_id not in res.stdout:
                    break

                time.sleep(0.5)

def collect_logs(run_dir):
    results_dir = os.path.join(run_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    build_out = os.path.join(run_dir, "build.out")

    if os.path.exists(build_out):
        shutil.copy(build_out, os.path.join(results_dir, "build.log"))

    for file in os.listdir(run_dir):
        if file.startswith("run_") and file.endswith(".out"):
            shutil.copy(
                os.path.join(run_dir, file),
                os.path.join(results_dir, file.replace(".out", ".log"))
            )

def execute(parser, mode,profile=False):

    print("[HPL] Execution started")

    run_dir = get_run_dir(parser)
    setup(run_dir)

    case = os.path.basename(run_dir)
    print(f"Run directory: {run_dir}")

    runtime = parser.get_runtime()
    execution = parser.get_app_config().get("execution", {})
    iterations = execution.get("iterations", 1)

    build_id = None

    if mode in ["build", "all"]:
        case_banner(case, "BUILD")

        if is_binary_present():
            print("✔ Binary exists → Skipping BUILD")
        else:
            script_path = f"{run_dir}/build.sbatch"
            with open(script_path, "w") as f:
                f.write(generate_build_sbatch(parser, run_dir))

            build_id = submit(script_path)
            wait_for_job(build_id)
            print("✔ BUILD DONE")
        if not is_binary_present():
            print("Build failed. Stopping.")
            return
        copy_hpl_artifacts(run_dir)

    if mode in ["run", "all"]:
        case_banner(case, "RUN")
        generate_hpl_dat(parser, f"{run_dir}/bin/HPL.dat")
        all_results = []
        script_path = f"{run_dir}/run.sbatch"
        with open(script_path, "w") as f:
            f.write(generate_run_sbatch(parser, run_dir, profile))

        print("Submitting single job for all iterations...")
        run_id = submit(script_path)
        wait_for_job(run_id)

        for i in range(iterations):
            print(f"--- Iteration {i+1}/{iterations} ---")
            results = extract_results(f"{run_dir}/run_{i}.out")

            append_hpl_history(results["gflops"])
            
            if profile:
                perf_res = extract_perf(f"{run_dir}/profiling/perf_{i}.out")
                append_perf_history({"ipc": perf_res["ipc"],"gflops": results["gflops"]}, app="hpl")
                write_perf_summary(run_dir,i,results["gflops"],perf_res["ipc"])
            all_results.append(results)

        gflops_values = [r["gflops"] for r in all_results]

        append_hpl_iterations(gflops_values)

        avg = sum(gflops_values) / len(gflops_values)
        append_hpl_avg(avg)

        show_summary_all(all_results)

        store_results(run_dir, all_results, {"build_job_id": build_id})

        collect_logs(run_dir)

        link_name = case
        current_dir = os.getcwd()
        link_path = os.path.join(current_dir, link_name)

        if os.path.islink(link_path) or os.path.exists(link_path):
            os.remove(link_path)

        os.symlink(run_dir, link_path)

        print(f"\nShortcut created: {link_name}")
        print(f"Now you can run: cd {link_name}\n")
        print("✔ ALL RUNS COMPLETED")