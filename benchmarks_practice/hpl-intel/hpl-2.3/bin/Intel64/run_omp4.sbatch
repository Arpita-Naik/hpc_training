#!/bin/bash
#SBATCH --job-name=HPL_OMP4
#SBATCH --output=hpl_omp4_%j.out
#SBATCH --error=hpl_omp4_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=4
#SBATCH --time=00:30:00

module purge
module use /opt/intel/oneapi/2025.3/etc/modulefiles

unset OMPI_HOME
unset PMIX_HOME
unset OPAL_PREFIX

module load compiler/2025.3.2
module load mpi/2021.17
module load mkl/2025.3

export I_MPI_PIN=1
export OMP_PROC_BIND=true
export OMP_PLACES=cores
export OMP_NUM_THREADS=4

cd ~/hpl-intel/hpl-2.3/bin/Intel64

echo "Running OMP=4 MPI=2"

P=1; Q=2

sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Ps/$P            Ps/" HPL.dat
sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Qs/$Q            Qs/" HPL.dat

mpirun -np 2 ./xhpl > output_omp4.txt
