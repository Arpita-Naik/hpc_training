/*Broadcast an Array
Rank 0 creates an array:
int arr[8] = {1,2,3,4,5,6,7,8};
Broadcast to all processes.
Each process computes local sum of entire array.*/


#include<stdio.h>
#include<mpi.h>

int main(int argc,char **argv)
{
    int rank,nprocs;
    int arr[8];
    int local_sum=0;

    MPI_Init(&argc,&argv);

    MPI_Comm_rank(MPI_COMM_WORLD,&rank);
    MPI_Comm_size(MPI_COMM_WORLD,&nprocs);
    
    //rank 0 initilizes the array(temp)
    if(rank==0)
    {
        printf("Process 0 is initializing the array...\n");

        int temp[8]={1,2,3,4,5,6,7,8};
        for(int i=0;i<8;i++)
        {
            arr[i]=temp[i];
        }
    }
    MPI_Bcast(arr,8,MPI_INT,0,MPI_COMM_WORLD);
    for(int i=0;i<8;i++)
    {
        local_sum+=arr[i];
    }

    printf("Process %d local sum = %d\n",rank,local_sum);
    MPI_Finalize();
    return  0;

}

/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/c$ mpirun -np 3 ./mpi
Process 0 performed 334 iterations of the loop.
process 0 performed teh remaining 0 iteration of the loop
Process 2 performed 334 iterations of the loop.
Process 1 performed 334 iterations of the loop.*/