#!/bin/bash
#SBATCH --job-name=HPL_AOCC
#SBATCH --output=hpl_aocc_%j.out
#SBATCH --error=hpl_aocc_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --time=00:50:00

module purge
module use ~/modules
module load aocc/5.1.0
module load aocl/5.2.0

export PATH=/home/arpita/openmpi-5.0.9/bin:$PATH
export LD_LIBRARY_PATH=/home/arpita/openmpi-5.0.9/lib:$LD_LIBRARY_PATH

source /home/arpita/aocl/5.2.0/aocc/amd-libs.cfg

export OMP_PROC_BIND=true
export OMP_PLACES=cores

cd ~/hpl-aocc/hpl-2.3/bin/AOCC

TOTAL_CORES=$(nproc)

echo "Starting HPL runs..."

for OMP in 1 2 4 8
do
MPI=$((TOTAL_CORES / OMP))
export OMP_NUM_THREADS=$OMP

echo "Running MPI=$MPI OMP=$OMP"

if [ $MPI -eq 8 ]; then
    P=2; Q=4
elif [ $MPI -eq 4 ]; then
    P=2; Q=2
elif [ $MPI -eq 2 ]; then
    P=1; Q=2
else
    P=1; Q=1
fi

sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Ps/$P Ps/" HPL.dat
sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Qs/$Q Qs/" HPL.dat

mpirun --bind-to none -np $MPI ./xhpl > output_aocc_${OMP}.txt


done

echo "All HPL runs completed!"
