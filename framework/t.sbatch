#!/bin/bash
#SBATCH --job-name=hpl_run
#SBATCH --output=hpl_output.txt
#SBATCH --error=hpl_error.txt
#SBATCH --ntasks=4
#SBATCH --time=00:20:00

echo "===== JOB START ====="
date

# -------------------------------

# 1. Fix environment (VERY IMPORTANT)

# -------------------------------

source /etc/profile

export PATH=/usr/bin:$PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH

# -------------------------------

# 2. Go to home and setup HPL

# -------------------------------

cd $HOME
rm -rf hpl-2.3

wget https://www.netlib.org/benchmark/hpl/hpl-2.3.tar.gz
tar -xzf hpl-2.3.tar.gz
cd hpl-2.3

# -------------------------------

# 3. Configure Makefile

# -------------------------------

cp setup/Make.Linux_PII_CBLAS Make.myarch

sed -i 's/^ARCH.*/ARCH = myarch/' Make.myarch
sed -i "s|^TOPdir.*|TOPdir = $HOME/hpl-2.3|" Make.myarch
sed -i 's|^CC.*|CC = mpicc -I$(TOPdir)/include|' Make.myarch
sed -i 's|^LINKER.*|LINKER = mpicc|' Make.myarch

# 🔥 FIXED OPENBLAS LINKING

sed -i 's|^LAlib.*|LAlib = /usr/lib/x86_64-linux-gnu/libopenblas.so|' Make.myarch

sed -i '/mpich/d' Make.myarch

echo "ARCHIVER = ar" >> Make.myarch
echo "ARFLAGS = r" >> Make.myarch

# -------------------------------

# 4. Build HPL

# -------------------------------

echo "===== BUILDING ====="
make arch=myarch

# -------------------------------

# 5. Run HPL

# -------------------------------

cd bin/myarch
cp ../../testing/ptest/HPL.dat .

chmod +x xhpl

echo "===== RUNNING ====="
mpirun -np 4 ./xhpl

echo "===== JOB END ====="
date
