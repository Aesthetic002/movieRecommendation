@echo off
REM Build script for Windows

echo Compiling C recommendation engine...

gcc -Wall -O2 -c file_io.c
gcc -Wall -O2 -c graph.c
gcc -Wall -O2 -c hash_table.c
gcc -Wall -O2 -c movie.c
gcc -Wall -O2 -c recommendation.c
gcc -Wall -O2 -c user.c
gcc -Wall -O2 -c c_interface.c

echo Linking...
gcc -Wall -O2 -o c_interface.exe file_io.o graph.o hash_table.o movie.o recommendation.o user.o c_interface.o -lm

echo Cleaning object files...
del *.o

echo Build complete! c_interface.exe created.
