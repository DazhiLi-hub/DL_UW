#include <iostream>
#include "Timer.h"
#include <stdlib.h>   // atoi
#include "mpi.h"
#include "omp.h"

int default_size = 100;  // the default system size
int defaultCellWidth = 8;
double c = 1.0;      // wave speed
double dt = 0.1;     // time quantum
double dd = 2.0;     // change in system

int my_rank = 0;            // used by MPI
int mpi_size = 1;           // used by MPI
MPI_Status status;

using namespace std;

int main( int argc, char *argv[] ) {
  // verify arguments
  if ( argc != 4 && argc != 5 ) {
    cerr << "usage: Wave2D size max_time interval num_thread(optional)" << endl;
    return -1;
  }
  int size = atoi( argv[1] );
  int max_time = atoi( argv[2] );
  int interval  = atoi( argv[3] );
  int num_thread = 1;

  if (argc == 5) {
    num_thread = atoi( argv[4] );
  }

  if ( size < 100 || max_time < 3 || interval < 0 || num_thread < 1) {
    cerr << "usage: Wave2D size max_time interval" << endl;
    cerr << "       where size >= 100 && time >= 3 && interval >= 0 && #thread >=1" << endl;
    return -1;
  }

  // create a simulation space
  double z[3][size][size];
  for ( int p = 0; p < 3; p++ ) 
    for ( int i = 0; i < size; i++ )
      for ( int j = 0; j < size; j++ )
	      z[p][i][j] = 0.0; // no wave

  MPI_Init( &argc, &argv ); // start MPI
  MPI_Comm_rank( MPI_COMM_WORLD, &my_rank );
  MPI_Comm_size( MPI_COMM_WORLD, &mpi_size );

  omp_set_num_threads( num_thread );

  // Allocating strips for each node
  int strips[mpi_size], start_idx[mpi_size], end_idx[mpi_size];
  start_idx[0] = 0;
  int remainder = size % mpi_size, standard_strip = size / mpi_size;
  for (int i = 0; i < mpi_size; i++) {
    strips[i] = standard_strip;
  }
  if (remainder != 0) {
    for (int i = 0; i < remainder; i++) {
      strips[i] += 1;
    }
  }
  for (int i = 1; i < mpi_size; i++) {
    start_idx[i] = start_idx[i-1] + strips[i-1];
    end_idx[i-1] = start_idx[i] - 1;
  }
  //specialize first and last node
  start_idx[0] = 1;
  end_idx[mpi_size - 1] = size - 2;

  Timer time;
  time.start( );

  // master initializing t=0
  if (my_rank == 0) {
    // start a timer
    // time = 0;
    // initialize the simulation space: calculate z[0][][]
    int weight = size / default_size;
    for( int i = 0; i < size; i++ ) {
      for( int j = 0; j < size; j++ ) {
        if( i > 40 * weight && i < 60 * weight  &&
	      j > 40 * weight && j < 60 * weight ) {
	      z[0][i][j] = 20.0;
      } else {
	      z[0][i][j] = 0.0;
      }
      }
    }
    // send message to nodes
    if (mpi_size > 1) {
      for (int i = 1; i < mpi_size - 1; i++) {
        MPI_Send(z[0][end_idx[i-1]], size*(strips[i] + 2), MPI_DOUBLE, i, 0, MPI_COMM_WORLD);
      }
        MPI_Send(z[0][end_idx[mpi_size-2]], size*(strips[mpi_size-1] + 1),
         MPI_DOUBLE, mpi_size - 1, 0, MPI_COMM_WORLD);
    }
  } else {
    if (my_rank != mpi_size -1) {
      MPI_Recv(z[0][end_idx[my_rank-1]], size*(strips[my_rank] + 2),
       MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, &status);
    } else {
      MPI_Recv(z[0][end_idx[my_rank-1]], size*(strips[my_rank] + 1),
       MPI_DOUBLE, 0, 0, MPI_COMM_WORLD, &status);
    }
  }

  // time = 1
  // calculate z[1][][] 
  // cells not on edge
#pragma omp parallel for
  for (int i = start_idx[my_rank]; i <= end_idx[my_rank]; i++) {
    for (int j = 1; j < size-1; j++) {
      z[1][i][j] = z[0][i][j] + c*c/2*(dt/dd)*(dt/dd)*(z[0][i+1][j]+z[0][i-1][j]+z[0][i][j+1]+z[0][i][j-1]-4*z[0][i][j]);
    }
  }

  // simulate wave diffusion from time = 2
  for ( int t = 2; t < max_time; t++ ) {
    // message exchanging
    if (mpi_size > 1) {
      if (my_rank != mpi_size - 1) {
        MPI_Send(z[(t-1)%3][end_idx[my_rank]], size, MPI_DOUBLE, my_rank + 1, 0, MPI_COMM_WORLD);
      }
      if (my_rank != 0) {
        MPI_Recv(z[(t-1)%3][end_idx[my_rank - 1]], size, MPI_DOUBLE, my_rank - 1, 0, MPI_COMM_WORLD, &status);
        MPI_Send(z[(t-1)%3][start_idx[my_rank]], size, MPI_DOUBLE, my_rank - 1, 0, MPI_COMM_WORLD);
      }
      if (my_rank != mpi_size -1) {
        MPI_Recv(z[(t-1)%3][start_idx[my_rank+1]], size, MPI_DOUBLE, my_rank + 1, 0, MPI_COMM_WORLD, &status);
      }
    }
    // calculating
  #pragma omp parallel for
    for (int i = start_idx[my_rank]; i <= end_idx[my_rank]; i++) {
      for (int j = 1; j < size - 1; j++) {
        z[t%3][i][j] = 2*z[(t-1)%3][i][j] - z[(t-2)%3][i][j] + c*c*(dt/dd)*(dt/dd)*
        (z[(t-1)%3][i+1][j]+z[(t-1)%3][i-1][j]+z[(t-1)%3][i][j+1]+z[(t-1)%3][i][j-1]-4*z[(t-1)%3][i][j]);
      }
    }
    // printing out by interval
    if (interval !=0 && (t % interval == 0 || t == max_time - 1)) {
      // exchanging data first
      if (mpi_size > 1) {
        if (my_rank != 0) {
          MPI_Send(z[t%3][start_idx[my_rank]], size*strips[my_rank], MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
        } else {
          for (int i = 1; i < mpi_size; i++) {
            MPI_Recv(z[t%3][start_idx[i]], size*strips[i], MPI_DOUBLE, i, 0, MPI_COMM_WORLD, &status);
          }
        }
      }
      // printing
      if (my_rank == 0) {
        cout << t << endl;
        for (int i = 0; i < size; i++) {
          for (int j = 0; j < size; j++) {
            cout << z[t%3][i][j] << " ";
          }
          cout << endl;
        }
      }
    }
  } // end of simulation
    
  // finish the timer
  if (my_rank == 0) {
    cerr << "Elapsed time = " << time.lap( ) << endl;
  }
  MPI_Finalize( ); // shut down MPI
  return 0;
}
