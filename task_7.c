/*Parallel Matrix-Vector Multiplication
Task
Given:
Matrix (4×4) → only on rank 0
Vector (size 4) → broadcast to all
Steps:
Scatter matrix rows
Broadcast vector
Each process computes:
y_i = row_i × vector
Gather results into final vector y*/

#include <stdio.h>
#include <mpi.h>

#define N 4

int main(int argc, char **argv)
{
    int rank, nprocs;
    int matrix[N][N];
    int vector[N];
    int row[N];
    int y[N];
    int local_result = 0;

    MPI_Init(&argc, &argv);

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nprocs);

    if(nprocs != N)
    {
        if(rank == 0)
            printf("Run with %d processes only.\n", N);

        MPI_Finalize();
        return 0;
    }

    if(rank == 0)
    {
        int value = 1;
        printf("Matrix:\n");
        for(int i = 0; i < N; i++)
        {
            for(int j = 0; j < N; j++)
            {
                matrix[i][j] = value++;
                printf("%3d ", matrix[i][j]);
            }
            printf("\n");
        }

        printf("\nVector:\n");
        for(int i = 0; i < N; i++)
        {
            vector[i] = 1;
            printf("%d ", vector[i]);
        }
        printf("\n\n");
    }

    MPI_Scatter(matrix, N, MPI_INT,
                row, N, MPI_INT,
                0, MPI_COMM_WORLD);

    MPI_Bcast(vector, N, MPI_INT, 0, MPI_COMM_WORLD);

    printf("Process %d received row: ", rank);
    for(int i = 0; i < N; i++)
        printf("%d ", row[i]);
    printf("\n");

    for(int i = 0; i < N; i++)
        local_result += row[i] * vector[i];

    printf("Process %d computed y[%d] = %d\n",
           rank, rank, local_result);

    MPI_Gather(&local_result, 1, MPI_INT,
               y, 1, MPI_INT,
               0, MPI_COMM_WORLD);

    if(rank == 0)
    {
        printf("\nFinal Result Vector y:\n");
        for(int i = 0; i < N; i++)
            printf("%d ", y[i]);
        printf("\n");
    }

    MPI_Finalize();
    return 0;
}


/*arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpicc task_7.c -o task_7
arpita@DESKTOP-9FJDKRQ:/mnt/c/Users/infobell/Desktop/C$ mpirun -np 4  ./task_7
Matrix:
  1   2   3   4
  5   6   7   8
  9  10  11  12
 13  14  15  16

Vector:
1 1 1 1

Process 0 received row: 1 2 3 4
Process 0 computed y[0] = 10

Final Result Vector y:
10 26 42 58
Process 2 received row: 9 10 11 12
Process 2 computed y[2] = 42
Process 1 received row: 5 6 7 8
Process 1 computed y[1] = 26
Process 3 received row: 13 14 15 16
Process 3 computed y[3] = 58*/