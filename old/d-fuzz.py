#!/usr/bin/python

import sys, os, string

if len(sys.argv) == 1:
	print """
 dfuzz : easy and light streaming tool

 Copyright (c) 2006 Guillaume Pellerin <yomguy@altern.org>
 distributed under the terms of the GNU Public License v2
 
 depends : ezstream (patched), icecast2, python,
 
 Usage : dfuzz $1 $2 $3 $4 $5
 	  where $1 : station name
	  	$2 : type (mp3 or ogg)
		$3 : number of sub-channels
		$4 : working directory
		$5 : audio directory 
		$6 : icecast2 server name
		$7 : icecast2 port
	"""
	sys.exit('')

radio_name = sys.argv[1]
nb_ch = int(sys.argv[3])
type = sys.argv[2]
work_dir = sys.argv[4]
audio_dir = sys.argv[5]
server = sys.argv[6]
port = sys.argv[7]
radio_description_file = work_dir+os.sep+radio_name+'.xml'
dfuzz_dir = '/usr/local/share/d-fuzz'
ez_tools_file = dfuzz_dir+os.sep+'d-fuzz_tools.py'

f_descr = open(radio_description_file,'r')
l_descr = f_descr.readlines()
f_descr.close()

f_ez_tools = open(ez_tools_file,'r')
l_tools = f_ez_tools.readlines()
f_ez_tools.close()

for i in range(1,nb_ch+1):
	ch_name_i = radio_name+'_'+type+'_'+str(i)
	ch_ice_name_i = radio_name+'_'+str(i)
	ch_pre_i = work_dir+os.sep+ch_name_i
	fi_xml = open(ch_pre_i+'.xml','w')
	fi_xml.write('<ezstream>\n')
	fi_xml.write('<url>http://'+server+':'+port+'/'+ch_ice_name_i+'.'+type+'</url>\n')
	fi_xml.write('<format>'+string.upper(type)+'</format>\n')
        fi_xml.write('<filetype>script</filetype>\n')
        fi_xml.write('<filename>'+ch_pre_i+'.py</filename>\n')
	for line in l_descr:
		fi_xml.write(line)
	fi_xml.write('</ezstream>')
	fi_xml.close()
	fi_py = open(ch_pre_i+'.py','w')
	fi_py.write('#!/usr/bin/python\n\n')
	fi_py.write('import sys, os, random\n\n')
	fi_py.write('Playdir="'+audio_dir+os.sep+'"\n')
	fi_py.write('IndexFile="'+ch_pre_i+'_index.txt"\n')
	fi_py.write('RandomIndexListFile="'+ch_pre_i+'_random_index_list.txt"\n')
	fi_py.write('PlaylistLengthOrigFile="'+ch_pre_i+'_playlist_length.txt"\n\n')
	for line in l_tools:
		fi_py.write(line)
	fi_py.close()
	os.chmod(work_dir+os.sep+ch_name_i+'.py',0755)
	os.system('d-fuzz_loop '+ch_pre_i+' &')
	sys.exit(ch_pre_i+' started !')
	


