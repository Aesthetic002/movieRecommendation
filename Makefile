# Makefile for C recommendation engine
CC = gcc
CFLAGS = -Wall -O2
TARGET = recommend_engine
INTERFACE_TARGET = c_interface

SRCS = file_io.c graph.c hash_table.c movie.c recommendation.c user.c
OBJS = $(SRCS:.c=.o)

# Main interactive program
$(TARGET): main.o $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) main.o $(OBJS) -lm

# Django interface program
$(INTERFACE_TARGET): c_interface.o $(OBJS)
	$(CC) $(CFLAGS) -o $(INTERFACE_TARGET) c_interface.o $(OBJS) -lm

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

c_interface.o: c_interface.c
	$(CC) $(CFLAGS) -c c_interface.c

%.o: %.c %.h
	$(CC) $(CFLAGS) -c $<

all: $(TARGET) $(INTERFACE_TARGET)

clean:
	rm -f *.o $(TARGET) $(INTERFACE_TARGET)

.PHONY: all clean
