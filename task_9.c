/*As discussed during session. Practice excercise 1000 p0 = main process 
receiving nloops and calculating 
total_nloops and perform remaining left over 
iterations p1,p2,p3 = take care of 333 by each (iteration task) and send nloops to p0*/


#include <stdio.h>
#include <mpi.h>

#define TOTAL 1000

int main(int argc, char **argv)
{
    int i, rank, nprocs;
    int count, start, stop;
    int nloops, total_nloops;
    MPI_Status status;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    if(nprocs != 4)
    {
        if(rank == 0)
            printf("Run with 4 processes only.\n");

        MPI_Finalize();
        return 0;
    }

    // Only worker processes divide work
    if(rank != 0)
    {
        count = TOTAL / (nprocs - 1);   // 1000 / 3 = 333

        start = (rank - 1) * count;
        stop  = start + count;

        nloops = 0;

        for(i = start; i < stop; i++)
            ++nloops;

        printf("Process %d performed %d iterations.\n",
               rank, nloops);

        MPI_Send(&nloops, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    }
    else
    {
        total_nloops = 0;

        for(i = 1; i < nprocs; i++)
        {
            MPI_Recv(&nloops, 1, MPI_INT, i, 0,
                     MPI_COMM_WORLD, &status);

            total_nloops += nloops;
        }

        nloops = 0;

        for(i = total_nloops; i < TOTAL; i++)
            ++nloops;

        printf("Process 0 performed the remaining %d iterations.\n",
               nloops);
    }

    MPI_Finalize();
    return 0;
}

/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpicc task_9.c -o task_9
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpirun -np 4  ./task_9
Process 2 performed 333 iterations.
Process 1 performed 333 iterations.
Process 3 performed 333 iterations.
Process 0 performed the remaining 1 iterations.*/