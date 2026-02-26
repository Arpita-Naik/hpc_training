/*Parallel Maximum of Matrix
Task
Each process finds local max of its row.
Use:
MPI_Reduce(..., MPI_MAX, ...)
Rank 0 prints global maximum.*/



#include<stdio.h>
#include<mpi.h>

#define N 4

int main(int argc,char**argv)
{
    int rank,nprocs;
    int matrix[N][N];
    int row[N];
    int local_max,global_max;

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
        printf("Matrix: \n");
        for(int i=0;i<N;i++)
        {
            for(int j=0;j<N;j++)
            {
                matrix[i][j]=value++;
                printf("%3d",matrix[i][j]);
            }
            printf("\n");
        }
        printf("\n");
    }
    MPI_Scatter(matrix,N,MPI_INT,row,N,MPI_INT,0,MPI_COMM_WORLD);
    local_max=row[0];

    for(int i=1;i<N;i++)
    {
        if(row[i]>local_max)
           local_max=row[i];
    }
    printf("process %d local max = %d\n",rank,local_max);

    MPI_Reduce(&local_max,&global_max,1,MPI_INT,MPI_MAX,0,MPI_COMM_WORLD);
    if(rank==0)
    {
        printf("Global MAX : %d\n",global_max);
    }
    MPI_Finalize();
    return 0;
}