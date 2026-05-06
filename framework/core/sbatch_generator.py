def generate_sbatch_script(
    job_name,
    output_file,
    nodes,
    ntasks,
    time_limit,   # ✅ changed
    command,
    workdir
):
    return f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --output={output_file}
#SBATCH --nodes={nodes}
#SBATCH --ntasks={ntasks}
#SBATCH --time={time_limit}
#SBATCH --partition=debug

echo "===== SLURM JOB START ====="

echo "Node: $(hostname)"
echo "Cores: $(nproc)"
echo "Working Dir: {workdir}"

cd {workdir}

echo "===== EXECUTION START ====="

{command}

echo "===== JOB END ====="
"""