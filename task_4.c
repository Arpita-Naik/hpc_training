/*Parallel Average
Steps:
Rank 0 reads N numbers
Broadcast N
Scatter data
Each process computes local sum
Reduce to global sum
Rank 0 computes average lets go with this*/



#include<stdio.h>
#include<mpi.h>
#define MAX 100
int main(int argc,char**argv)
{
    int n,rank,nprocs,local_sum=0,global_sum=0,i,data[MAX];
    MPI_Init(&argc,&argv);

    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);

    if(rank==0)
    {
        printf("Enter the no of elements : ");
        scanf("%d",&n);

        printf("Enter %d numbers:\n",n);
        for(int i=0;i<n;i++)
        {
            scanf("%d",&data[i]);
        }
    }

    MPI_Bcast(&n,1,MPI_INT,0,MPI_COMM_WORLD);

    int local_n=n/nprocs;
    int local[local_n];

    MPI_Scatter(data,local_n,MPI_INT,local,local_n,MPI_INT,0,MPI_COMM_WORLD);

    for(i=0;i<local_n;i++)
       local_sum+=local[i];
    
    printf("Process %d local sum : %d\n",rank,local_sum);

    MPI_Reduce(&local_sum,&global_sum,1,MPI_INT,MPI_SUM,0,MPI_COMM_WORLD);

    if(rank==0)
    {
        double avg=(double)global_sum/n;
        printf("Global Sum : %d\n",global_sum);
        printf("Average = %.2f\n",avg);
    }

    MPI_Finalize();
    return 0;
}