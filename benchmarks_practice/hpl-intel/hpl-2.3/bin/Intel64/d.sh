#!/bin/bash

TOTAL_CORES=8

for OMP in 1 2 4 8
do
    MPI=$((TOTAL_CORES / OMP))

    echo "Submitting: OMP=$OMP MPI=$MPI"

    sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=HPL_${OMP}
#SBATCH --output=hpl_${OMP}_%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=$MPI
#SBATCH --cpus-per-task=$OMP
#SBATCH --time=00:30:00

module purge
module use /opt/intel/oneapi/2025.3/etc/modulefiles
module load compiler/2025.3.2
module load mpi/2021.17
module load mkl/2025.3

export I_MPI_PIN=1
export OMP_PROC_BIND=true
export OMP_PLACES=cores
export OMP_NUM_THREADS=$OMP

cd ~/hpl-intel/hpl-2.3/bin/Intel64

if [ $MPI -eq 8 ]; then
    P=2; Q=4
elif [ $MPI -eq 4 ]; then
    P=2; Q=2
elif [ $MPI -eq 2 ]; then
    P=1; Q=2
else
    P=1; Q=1
fi

sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Ps/\$P            Ps/" HPL.dat
sed -i "s/^[[:space:]]*[0-9]\+[[:space:]]*Qs/\$Q            Qs/" HPL.dat

mpirun -np $MPI ./xhpl > output_${OMP}.txt

EOF

done
