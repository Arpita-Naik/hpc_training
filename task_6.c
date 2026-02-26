/*Parallel Matrix Row Distribution
Task
Rank 0 has a 4×4 matrix.
Distribute rows using MPI_Scatter.
Each process:
✔ Receives one row
✔ Computes sum of its row
✔ Use MPI_Reduce to compute total matrix sum*/

#include<stdio.h>
#include<mpi.h>
#define N 4
int main(int argc,char**argv)
{
    int rank,nprocs;
    int matrix[N][N];
    int row[N];
    int local_sum=0;
    int global_sum=0;
    MPI_Init(&argc,&argv);

    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);
    
    if(nprocs!=N)
    {
        if(rank==0)
          printf("Run with %d processes only.\n",N);
        MPI_Finalize();
        return 0;
    }

    if(rank==0)
    {
        int value=1;
        for(int i=0;i<N;i++)
        {
            for(int j=0;j<N;j++)
            {
                matrix[i][j]=value++;
                printf("%3d",matrix[i][j]);
            }
            printf("\n");
        }
    }
    MPI_Scatter(matrix,N,MPI_INT,row,N,MPI_INT,0,MPI_COMM_WORLD);

    for(int i=0;i<N;i++)
    {
        local_sum+=row[i];

    }
    printf("Process %d received row sum = %d\n", rank, local_sum);
    MPI_Reduce(&local_sum,&global_sum,1,MPI_INT,MPI_SUM,0,MPI_COMM_WORLD);

    if(rank==0)
    {
        printf("Total matrix sum = %d\n",global_sum);
        
    }

    MPI_Finalize();
    return 0;

}


/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpicc task_6.c -o task_6
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpirun -np 4  ./task_6
  1  2  3  4
  5  6  7  8
  9 10 11 12
 13 14 15 16
Process 0 received row sum = 10
Process 1 received row sum = 26
Process 2 received row sum = 42
Process 3 received row sum = 58
Total matrix sum = 136*/