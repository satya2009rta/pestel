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
LIBINC		= -I$(PRJROOT)/lib
SRC			= $(PRJROOT)/src
BASH		= $(PRJROOT)/bash-scripts
BUILD		= $(PRJROOT)/build

# hoa files
HOA			= -isystem$(PRJROOT)
HOA2PG	 	= $(PRJROOT)/hoa2pg
HOA2PGHDR 	= $(HOA2PG)/hoalexer.h $(HOA2PG)/hoaparser.h $(HOA2PG)/simplehoa.h
HOA2PGSRC 	= $(HOA2PG)/hoalexer.c $(HOA2PG)/hoaparser.c $(HOA2PG)/simplehoa.c $(HOA2PG)/hoa2pg.c


#
# address of FileHandler (for linking)
#
#OBJ		= ../../src/FileHandler

.PHONY: folder compute compose hoa2pg solveParity solveGenParity pg2gpg pg2randgpg compare compareIncr solvePUF clean

TARGET = folder compute compose hoa2pg solveParity solveGenParity pg2gpg pg2randgpg compare compareIncr solvePUF conflictsPUF

all: $(TARGET)
build: $(TARGET)

folder:
	[ -d $(BUILD) ] || mkdir -p $(BUILD)

compute:
	$(CC) $(CXXFLAGS) $(LIBINC) $(HOA) $(SRC)/compute.cpp -o $(BUILD)/compute
compose:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(HOA) $(MPFLAGS) $(SRC)/compose.cpp -o $(BUILD)/compose

hoa2pg:$(HOA2PGSRC) $(HOA2PGHDR) 
	$(C) $(CFLAGS) $(HOA2PGSRC) -o $(BUILD)/hoa2pg


solveParity:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(HOA) $(MPFLAGS) $(SRC)/solveParity.cpp -o $(BUILD)/solveParity
solveGenParity:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(HOA) $(MPFLAGS) $(SRC)/solveGenParity.cpp -o $(BUILD)/solveGenParity


pg2gpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(HOA) $(SRC)/pg2gpg.cpp -o $(BUILD)/pg2gpg
pg2randgpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(HOA) $(SRC)/pg2randgpg.cpp -o $(BUILD)/pg2randgpg



compare:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(HOA) $(MPFLAGS) $(SRC)/compare.cpp -o $(BUILD)/compare
compareIncr:
	$(MPCC) $(CXXFLAGS) $(LIBINC) $(HOA) $(MPFLAGS) $(SRC)/compareIncr.cpp -o $(BUILD)/compareIncr


solvePUF:
	$(CC) $(CXXFLAGS) $(LIBINC) $(HOA) $(SRC)/solvePUF.cpp -o $(BUILD)/solvePUF
conflictsPUF:
	$(CC) $(CXXFLAGS) $(LIBINC) $(HOA) $(SRC)/conflictsPUF.cpp -o $(BUILD)/conflictsPUF


clean:
	rm -r -f  $(BUILD)/*