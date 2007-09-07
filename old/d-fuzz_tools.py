#!/usr/bin/python

#import sys, os, random

#Playdir='/home/cellar/Cellar_playlist/'
#IndexFile='/home/cellar/stream/d-fuzz_1_index.txt'
#RandomIndexListFile='/home/cellar/stream/d-fuzz_1_random_index_list.txt'
#PlaylistLengthOrigFile='/home/cellar/stream/d-fuzz_1_playlist_length.txt'

def randrange(start, stop):
	values = range(start, stop)
	random.shuffle(values)
	while values:
		yield values.pop()
	raise StopIteration

if not os.path.exists(IndexFile):
	fi=open(IndexFile,'w')
	fi.write("%d\n" % 0)
	fi.close()
if not os.path.exists(RandomIndexListFile):
        fil=open(RandomIndexListFile,'w')
	fil.write("%d\n" % 0)
	fil.close()
if not os.path.exists(PlaylistLengthOrigFile):
        fill=open(PlaylistLengthOrigFile,'w')
	fill.write("%d\n" % 0)
	fill.close()
	
playlist = os.listdir(Playdir)
nf = len(playlist)
#print nf

fill=open(PlaylistLengthOrigFile,'rw')

nforig=int(fill.readline())

if not nf == nforig:
	fil=open(RandomIndexListFile,'w')
	ril=randrange(0,nf)
	#print ril
	k=1
	for i in ril:
		fil.write("%d\n" % (i))
#	fil.close()

fi=open(IndexFile,'rw')
fil=open(RandomIndexListFile,'rw')

#print nforig
if nforig < nf:
	nforig = nf

f_index=int(fi.readline())

#tmpil = fil.readlines()
f_index_list = range(nforig)
j = 0
for i in fil.readlines():
	f_index_list[j] = int(i)
	j+=1
	#print f_index_list[j]

fi.close()
fil.close()
fill.close()

if f_index == nf or f_index > nf:
	f_index = 0

#print f_index_list[f_index]
#print f_index
print Playdir + playlist[f_index_list[f_index]]

f_index+=1

fi = open(IndexFile,'w')
fi.write("%d" % (f_index))
fi.close()

fill=open(PlaylistLengthOrigFile,'w')
fill.write("%d" % (nf))
fill.close()


