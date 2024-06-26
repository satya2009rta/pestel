####################
# compilers
####################
CC        = g++
CXXFLAGS 	= -Wall -Wextra -std=c++2a -O3 -DNDEBUG -Wno-unknown-pragmas 
CFLAGS 	= -O3 -DNDEBUG

####################
# project root
####################
PRJROOT		= .
LIBINC		= -I$(PRJROOT)/lib -isystem$(PRJROOT)
SRC			= $(PRJROOT)/src
BUILD		= $(PRJROOT)/build




.PHONY: folder pestel pg2gpg pg2randgpg clean

TARGET = folder pestel pg2gpg pg2randgpg 

build: $(TARGET)

folder:
	[ -d $(BUILD) ] || mkdir -p $(BUILD)

pestel:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/pestel.cpp -o $(BUILD)/pestel

pg2gpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/pg2gpg.cpp -o $(BUILD)/pg2gpg
pg2randgpg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/pg2randgpg.cpp -o $(BUILD)/pg2randgpg

hoa2pg:
	$(CC) $(CXXFLAGS) $(LIBINC) $(SRC)/hoa2pg.cpp -o $(BUILD)/hoa2pg


clean:
	rm -r -f  $(BUILD)/*