/*Parallel Vector Addition
Task
Rank 0 creates two vectors:
A = {1,2,3,4,5,6,7,8}B = {8,7,6,5,4,3,2,1}
Steps:
Scatter A and B
Each process computes local sum
Gather results (or print locally)
C[i] = A[i] + B[i] */

#include<stdio.h>
#include<mpi.h>

#define N 8

int main(int argc,char**argv)
{
    int rank,nprocs;
    int A[N],B[N],C[N];

    MPI_Init(&argc,&argv);

    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);

    int local = N/nprocs;

    int local_A[local];
    int local_B[local];
    int local_C[local];

    if(rank==0)
    {
        int temp[N]={1,2,3,4,5,6,7,8};
        int temp1[N]={8,7,6,5,4,3,2,1};

        for(int i=0;i<N;i++)
        {
            A[i]=temp[i];
            B[i]=temp1[i];
        }

        printf("Vector A: ");
        for(int i=0;i<N;i++)
            printf("%d ",A[i]);

        printf("\nVector B: ");
        for(int i=0;i<N;i++)
            printf("%d ",B[i]);

        printf("\n");
    }

    MPI_Scatter(A,local,MPI_INT,local_A,local,MPI_INT,0,MPI_COMM_WORLD);
    MPI_Scatter(B,local,MPI_INT,local_B,local,MPI_INT,0,MPI_COMM_WORLD);

    // Print what each process received
    printf("Process %d received:\n", rank);

    printf("  A part: ");
    for(int i = 0; i < local; i++)
        printf("%d ", local_A[i]);

    printf("\n  B part: ");
    for(int i = 0; i < local; i++)
        printf("%d ", local_B[i]);

    printf("\n");

    for(int i=0;i<local;i++)
    {
        local_C[i]=local_A[i]+local_B[i];
    }

    MPI_Gather(local_C,local,MPI_INT,C,local,MPI_INT,0,MPI_COMM_WORLD);

    if(rank==0)
    {
        printf("Result Vector C: ");
        for(int i=0;i<N;i++)
            printf("%d ",C[i]);

        printf("\n");
    }

    MPI_Finalize();
    return 0;
}

/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpirun -np 2  ./task_5
Vector A: 1 2 3 4 5 6 7 8
Vector B: 8 7 6 5 4 3 2 1
Process 0 received:
  A part: 1 2 3 4
  B part: 8 7 6 5
Process 1 received:
  A part: 5 6 7 8
  B part: 4 3 2 1
Result Vector C: 9 9 9 9 9 9 9 9*/