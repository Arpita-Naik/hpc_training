cmake_minimum_required(VERSION 3.10)
project(STREAM C)

set(CMAKE_C_STANDARD 99)

# Define macros from command line
add_definitions(
  -DSTREAM_ARRAY_SIZE=${STREAM_ARRAY_SIZE}
  -DNTIMES=${NTIMES}
)

add_executable(stream_c.exe stream.c)

target_compile_options(stream_c.exe PRIVATE -O3 -fopenmp)
target_link_libraries(stream_c.exe PRIVATE -fopenmp)
