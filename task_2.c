/*Each process sends its rank to the next process:
rank → (rank+1) % nprocs
Each process receives from previous rank and prints:
Rank X received Y */
#include<stdio.h>
#include<mpi.h>

int main(int argc,char **argv)
{
    int rank,nprocs;
    int send,rec;
    MPI_Status status;

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);

    send=rank;
    int next=(rank+1)%nprocs;
    int prev=(rank-1+nprocs)%nprocs;

    if(rank%2==0)
    {
        MPI_Send(&send,1,MPI_INT,next,0,MPI_COMM_WORLD);
        MPI_Recv(&rec,1,MPI_INT,prev,0,MPI_COMM_WORLD,0);
    }
    else{
        MPI_Recv(&rec,1,MPI_INT,prev,0,MPI_COMM_WORLD,0);
        MPI_Send(&send,1,MPI_INT,next,0,MPI_COMM_WORLD);
    }
    printf("Rank %d received %d\n",rank,rec);

    MPI_Finalize();
    return 0;
}

/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpirun -np 2 ./task_2
Rank 1 received 0
Rank 0 received 1
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpirun -np 3 ./task_2
Rank 0 received 2
Rank 1 received 0
Rank 2 received 1
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpirun -np 4 ./task_2
Rank 2 received 1
Rank 1 received 0
Rank 3 received 2
Rank 0 received 3
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$*/