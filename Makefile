####################
# compilers
####################
CC        = g++
C	  		= gcc
CXXFLAGS 	= -Wall -Wextra -std=c++2a -O3 -DNDEBUG -Wno-unknown-pragmas
CFLAGS 	= -O3 -DNDEBUG


## OpenMP compiler and flags for linux
# MPCC 		= g++
# MPFLAGS	= -fopenmp


# OpenMP compiler and flags for mac
# MPCC		= /opt/homebrew/opt/llvm/bin/clang++
# MPFLAGS		= -I/opt/homebrew/opt/llvm/include -fopenmp -L/opt/homebrew/opt/llvm/lib


# # No OpenMP
MPCC 		= g++
MPFLAGS		=

####################
# project root
####################
PRJROOT		= .
LIBINC		= -I$(PRJROOT)/lib -isystem$(PRJROOT)
SRC			= $(PRJROOT)/src
BUILD		= $(PRJROOT)/build


#
# address of FileHandler (for linking)
#
#OBJ		= ../../src/FileHandler

.PHONY: folder compute compose pg2gpg pg2randgpg clean

TARGET = folder compute compose pg2gpg pg2randgpg 

all: $(TARGET)
build: $(TARGET)

folder:
	[ -d $(BUILD) ] || mkdir -p $(BUILD)

compute:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/compute.cpp -o $(BUILD)/compute
compose:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(MPFLAGS) $(SRC)/compose.cpp -o $(BUILD)/compose

pg2gpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/pg2gpg.cpp -o $(BUILD)/pg2gpg
pg2randgpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/pg2randgpg.cpp -o $(BUILD)/pg2randgpg


clean:
	rm -r -f  $(BUILD)/*