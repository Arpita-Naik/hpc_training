#!/bin/bash
#SBATCH --job-name=AOCC_OMP8
#SBATCH --output=aocc_omp8_%j.out
#SBATCH --error=aocc_omp8_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=00:30:00

module purge
module use ~/modules
module load aocc/5.1.0
module load aocl/5.2.0

export PATH=/home/arpita/openmpi-5.0.9/bin:$PATH
export LD_LIBRARY_PATH=/home/arpita/openmpi-5.0.9/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/home/arpita/aocc-compiler-5.1.0/lib:$LD_LIBRARY_PATH

export OMPI_MCA_plm=isolated
export OMPI_MCA_ess=singleton
export OMPI_MCA_rmaps_base_oversubscribe=1
export OMPI_MCA_hwloc_base_binding_policy=none

source /home/arpita/aocl/5.2.0/aocc/amd-libs.cfg

export OMP_NUM_THREADS=8
export OMP_PROC_BIND=true
export OMP_PLACES=cores

cd ~/hpl-aocc/hpl-2.3/bin/AOCC

P=1; Q=1

sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Ps/$P Ps/" HPL.dat
sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Qs/$Q Qs/" HPL.dat

mpirun --oversubscribe --bind-to none -np 1 ./xhpl > Output_aocc_8.txt
