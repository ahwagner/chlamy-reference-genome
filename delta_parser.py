from __future__ import print_function #support python3 style print function, allowing me to change default terminal \n behavior
import sys, os, csv, re

if len(sys.argv) < 2:
	sys.exit("Usage: %s delta_file" % sys.argv[0])
if not os.path.exists(sys.argv[1]):
	sys.exit("Error: File '%s' not found" % sys.argv[1])

delta_file = sys.argv[1]
delta_regex = re.compile(r"^-?\d+$")

with open(delta_file) as d_f:
	lines = d_f.readlines()

	del lines[:2] #delete the first 2 lines in the lines list, which are just generic info
	#saves me writing a case in my if-elif-else block just to handle the first 2 lines of the file

	ref_name = "you shouldn't be able to read this"
	query_name = "you shouldn't be able to read this either"
	ref_array = []
	query_array = []
	ref_start = 0 #do I really need all these initialization lines?
	ref_end = 0   #probably not but I have bad habits from other languages
	q_start = 0   #I'm used to Java scopes
	q_end = 0
	q_rev = False

	for line in lines:

		#line.strip()

		if (line[0] == ">"): #the beginning of a seq, in the format >ref_name query_name ref_length query_length
			name_info = line.split()
			ref_name = name_info[0]
			query_name = name_info[1]
#			print("seq start- names")

		elif (line[0].isdigit() and line[0] == "0"): #marks end of an alignment block
			
			#to avoid writing multiple delta cases (see the else at the end of this if/elif/else block)
			#when a query is reversed, all calculations are performed as if it were forward;
			#here I map it back to reverse before dumping the data
			if(q_rev):

				q_len_DEBUG_REMOVE = len(query_array) - 1

				for index, temp_q in enumerate(query_array):

					if(index == q_len_DEBUG_REMOVE):
						print("-----------------FINAL TEMP TUPLE---------------")
						print(temp_q)

					mapped_tuple = ( q_start-temp_q[0] , q_start-temp_q[1] )

					if(index == q_len_DEBUG_REMOVE):
						print("----------------FINAL NEW TUPLE----------------")
						print(mapped_tuple)

					query_array[index] = mapped_tuple

			for ref_algn in ref_array:
				print(ref_algn, end=' ')
			print("") #make a line break

			#TODO only for debugging remove in production- if anyone else is reading this original dev is an idiot
			if(q_rev):
				print("OG q_end: " + str(q_end))

			for q_algn in query_array:
				print(q_algn, end=' ')
			print("") #another line break in anticipation of the next set of alignments

#			print("seq end")

		elif( delta_regex.search(line) is None): #beginning of alignment block, in the format
			
			a_info = line.split(" ")         #ref_start ref_end query_start query_end errors errors errors

			ref_start = int(a_info[0])
			ref_end = int(a_info[1])
			q_start = int(a_info[2])
			q_end = int(a_info[3])

			#for later use- check to see if the query alignment is reversed or not
			if(q_start > q_end):
				q_rev = True
			else:
				q_rev = False

			ref_array = []    #reset arrays; old info has been dumped in the above elif
			query_array = []

			ref_array.append((ref_start, ref_end)) #initialize arrays with new info

			if(q_rev):
				q_end = q_start - q_end
				query_array.append((0, q_end))
			else:
				query_array.append((q_start, q_end))
#			print("seq start- alignment info >" + line.rstrip() + "<")

			ref_tracker = ref_start

			if(q_rev):
				query_tracker = 0
			else:
				query_tracker = q_start

			curr_list_index = 0

		else: #this line contains delta info
#			print("delta line")
			delta = int(line)
			abs_delta = abs(delta)

			ref_tracker = int(ref_array[curr_list_index][0])
			query_tracker = int(query_array[curr_list_index][0])

			#old_ref_tuple = ref_array[curr_list_index]
			#old_q_tuple = query_array[curr_list_index]
			del ref_array[curr_list_index]
			del query_array[curr_list_index]
			curr_list_index += 1

			if (delta == -1): #move ref up by 1, no other changes (edge case)

				ref_array.append( (ref_tracker + 1, ref_end) )
				query_array.append( (query_tracker, q_end) )
				curr_list_index -= 1
			
			elif (delta == 1): #move query up by 1, no other changes (edge case)
				
				ref_array.append( (ref_tracker, ref_end) )
				query_array.append( (query_tracker + 1, q_end) )
				curr_list_index -= 1

			elif (delta < 0): #makes a gap in the ref

				ref_array.append( (ref_tracker, ref_tracker + (abs_delta - 2)) )
				ref_array.append( (ref_tracker + abs_delta, ref_end) )
				query_array.append( (query_tracker, query_tracker + (abs_delta - 2)) )
				query_array.append( (query_tracker + (abs_delta - 1), q_end) )

			else: #makes a gap in the query

				ref_array.append( (ref_tracker, ref_tracker + (abs_delta - 2)) )
				ref_array.append( (ref_tracker + (abs_delta - 1), ref_end) )
				query_array.append( (query_tracker, query_tracker + (abs_delta - 2)) )
				query_array.append( (query_tracker + abs_delta, q_end) )






