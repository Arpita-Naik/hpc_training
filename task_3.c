/*Master Collects Values
Each process computes:
value = rank * rank
Workers send value to rank 0 using MPI_Send.
Rank 0 receives all and prints total.
Then:
👉 Replace with MPI_Reduce*/

#include<stdio.h>
#include<mpi.h>

int main(int argc,char**argv)
{
    int rank,nprocs;
    int value,total=0;

    MPI_Init(&argc,&argv);
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);

    value=rank*rank;
    /*if(rank!=0)
    {
        MPI_Send(&value,1,MPI_INT,0,0,MPI_COMM_WORLD);
    }
    else{
        for(int i=1;i<nprocs;i++)
        {
            MPI_Recv(&value,1,MPI_INT,i,0,MPI_COMM_WORLD,0);
            total+=value;
        }
        printf("Total Sum:%d\n",total);
    }*/

    MPI_Reduce(&value,&total,1,MPI_INT,MPI_SUM,0,MPI_COMM_WORLD);
    if(rank==0)
    {
        printf("Total Sum=%d\n",total);
    }
    MPI_Finalize();
    return 0;
}


/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpicc task_3.c -o task_3
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpirun -np 4 ./task_3
Total Sum=14
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$*/