import sys
import math
import copy

#print out current memory
def printmem(mem, framesperline):
	#initial line
	print("="*framesperline)

	#go through the memory array
	i = 0
	while i < len(mem):
		count = 0
		#print array out in lines of length framseperline
		for j in range(i, min(i+framesperline,len(mem))):
			print(mem[j], end="")
			count += 1
		print()
		i += count
	#end printing line
	print("="*framesperline)

#function to defragment memory
def defragment(mem, tmemmove):
	#keep track of cost and changes
	movecost = 0
	changed = []
	#go through memory
	for i in range(len(mem)):
		#if the memory is free
		if mem[i] == ".":
			#go through the rest of the memory
			for j in range(i+1, len(mem)):
				#if the frame isn't empty
				if mem[j] != ".":
					#keep track of what's changed and move the info
					if mem[j] not in changed:
						changed.append(mem[j])
					mem[i] = mem[j]
					mem[j] = "."
					movecost += tmemmove
					break

	#return the total cost and what moved
	return movecost, changed

#contigous memory first fit function
def firstfit(framesperline, memsize, tmemmove, p, sp):
	#initial variables
	time = 0
	processes = copy.deepcopy(p)
	sizeprocess = sp.copy()
	removeprocesses = {}
	#copy keps into remove processes
	for key in processes.keys():
		removeprocesses[key] = -1

	#set memory
	memory = ["."] * memsize
	defragprocess = '.'

	print("time {}ms: Simulator started (Contiguous -- First-Fit)".format(time))

	#while there are unfinished processes
	while len(removeprocesses):
		#find the processes that are finished and remove them
		toremove = [p for p in processes if len(processes[p]) == 0]
		for p in toremove:
			processes.pop(p)

		#for the remining processes
		for p in removeprocesses:
			#if it is time for the process to be removed from memory
			if removeprocesses[p] == time:
				#remove it from memory and print info
				for i in range(len(memory)):
					if memory[i] == p:
						memory[i] = "."
				print("time {}ms: Process {} removed:".format(time, p))
				printmem(memory, framesperline)

		#find processes that are finished and remove them from remaining processes
		finished = [p for p in removeprocesses if p not in processes and removeprocesses[p] < time]
		for p in finished:
			removeprocesses.pop(p)
		#if there are no more processes, break
		if (len(removeprocesses) == 0):
			break

		#go through each process
		for p in processes:

			#if it is arriving
			if processes[p][0][0] == time:
				#save the time it will leave
				removeprocesses[p] = time + processes[p][0][1]

				#how much size it needs
				sizeneeded = sizeprocess[p]

				#if defragmentation isn't needed
				if p != defragprocess:
					print("time {}ms: Process {} arrived (requires {} frames)".format(time, p, sizeneeded))
				else:
					defragprocess = '.'

				#if there isn't enough memory left in total, skip
				if memory.count(".") < sizeneeded:
					print("time {}ms: Cannot place process {} -- skipped!".format(time, p))
					removeprocesses[p] = -1
					processes[p].pop(0)
					continue

				#find the first spot with enough space to hold memory
				startpointer = 0
				freespace = 0
				#go through memory
				for i in range(len(memory)):
					#keep track of how much open space there is and when it starts
					if memory[i] != ".":
						freespace = 0
						continue
					if freespace == 0:
						startpointer = i
					freespace += 1
					#break on first block that's large enough
					if freespace == sizeneeded:
						break

				#if there isn't enough freespace in a block, defragment and print info
				if freespace < sizeneeded:
					print("time {}ms: Cannot place process {} -- starting defragmentation".format(time, p))
					timespent, changed = defragment(memory, tmemmove)
					time += timespent
					print("time {}ms: Defragmentation complete (moved {} frames: ".format(time, int(timespent/tmemmove)), end="")
					for i in range(len(changed)-1):
						print("{}, ".format(changed[i]), end="")

					print("{})".format(changed[-1]))

					#update times based on defragmentation
					for proc in processes:
						processes[proc] = [(x+timespent, y) for x, y in processes[proc]]
					for proc in removeprocesses:
						removeprocesses[proc] += timespent
					defragprocess = p
					break

				#go through the memory and add the process
				for i in range(startpointer, startpointer + sizeneeded):
					memory[i] = p
				print("time {}ms: Placed process {}:".format(time, p))
				printmem(memory, framesperline)
				processes[p].pop(0)

		#note if defragged
		if defragprocess != '.':
			defraged = '.'
			continue

		time += 1

	time -= 1
	print("time {}ms: Simulator ended (Contiguous -- First-Fit)".format(time))

#contigous memory next fit function
def nextfit(framesperline, memsize, tmemmove, p, sp):
	#initialize first variables and memory
	time = 0
	processes = copy.deepcopy(p)
	sizeprocess = sp.copy()
	removeprocesses = {}
	#add all processes to another list
	for key in processes.keys():
		removeprocesses[key] = -1
	memory = ["."] * memsize
	defragprocess = '.'
	#holds location of last memory
	nextpointer = 0

	print("time {}ms: Simulator started (Contiguous -- Next-Fit)".format(time))

	#while there are processes that haven't ended
	while len(removeprocesses):
		#find processes that have ended and remove them
		toremove = [p for p in processes if len(processes[p]) == 0]
		for p in toremove:
			processes.pop(p)

		#go through all processes
		for p in removeprocesses:
			#if they are done running
			if removeprocesses[p] == time:
				#free the memory and print info
				for i in range(len(memory)):
					if memory[i] == p:
						memory[i] = "."
				print("time {}ms: Process {} removed:".format(time, p))
				printmem(memory, framesperline)

		#find processes that have finished and remove them
		finished = [p for p in removeprocesses if p not in processes and removeprocesses[p] < time]
		for p in finished:
			removeprocesses.pop(p)
		if (len(removeprocesses) == 0):
			break

		#go through all processes
		for p in processes:
			#if the process is arriving
			if processes[p][0][0] == time:
				#add the time for when the process will be removed and save the time needed
				removeprocesses[p] = time + processes[p][0][1]
				sizeneeded = sizeprocess[p]
				#if defragmentation isnt' necessary, print info
				if p != defragprocess:
					print("time {}ms: Process {} arrived (requires {} frames)".format(time, p, sizeneeded))
				else:
					defragprocess = '.'

				#if there isn't enough memory left, skip it
				if memory.count(".") < sizeneeded:
					print("time {}ms: Cannot place process {} -- skipped!".format(time, p))
					removeprocesses[p] = -1
					processes[p].pop(0)
					continue

				startpointer = 0
				freespace = 0

				#go through memory up to 2 times, starting at after the last added memory and find free space to hold
				#process
				for index in range(2*len(memory)):
					i = (index + nextpointer) % len(memory)
					if i == 0:
						freespace = 0
					
					if memory[i] != ".":
						freespace = 0
						continue
					if freespace == 0:
						startpointer = i

					freespace += 1
					if freespace == sizeneeded:
						break

				#if there isn't a block large enough, defragment and print info
				if freespace < sizeneeded:
					print("time {}ms: Cannot place process {} -- starting defragmentation".format(time, p))
					timespent, changed = defragment(memory, tmemmove)
					time += timespent
					print("time {}ms: Defragmentation complete (moved {} frames: ".format(time, int(timespent/tmemmove)), end="")
					for i in range(len(changed)-1):
						print("{}, ".format(changed[i]), end="")

					print("{})".format(changed[-1]))

					#update times and nextpointer after defragmentation
					for proc in processes:
						processes[proc] = [(x+timespent, y) for x, y in processes[proc]]
					for proc in removeprocesses:
						removeprocesses[proc] += timespent
					defragprocess = p
					nextpointer = memory.index(".")
					break

				#go through memory and add process memory
				for index in range(startpointer, startpointer + sizeneeded):
					i = index % len(memory)
					memory[i] = p
				nextpointer = (i+1)%len(memory)
				print("time {}ms: Placed process {}:".format(time, p))
				printmem(memory, framesperline)
				processes[p].pop(0)

		#note if defragmented
		if defragprocess != '.':
			defraged = '.'
			continue

		time += 1

	time -= 1
	print("time {}ms: Simulator ended (Contiguous -- Next-Fit)".format(time))

#contigous memory best fit function
def bestfit(framesperline, memsize, tmemmove, p, sp):
	#initialize variables
	time = 0
	processes = copy.deepcopy(p)
	sizeprocess = sp.copy()
	removeprocesses = {}
	#copy processes
	for key in processes.keys():
		removeprocesses[key] = -1
	memory = ["."] * memsize
	defragprocess = '.'

	print("time {}ms: Simulator started (Contiguous -- Best-Fit)".format(time))

	#while there are unfinished processes
	while len(removeprocesses):
		#if a processes is finished, remove it
		toremove = [p for p in processes if len(processes[p]) == 0]
		for p in toremove:
			processes.pop(p)

		#if a process is done running
		for p in removeprocesses:
			if removeprocesses[p] == time:
				#remove memory saved for processes
				for i in range(len(memory)):
					if memory[i] == p:
						memory[i] = "."
				print("time {}ms: Process {} removed:".format(time, p))
				printmem(memory, framesperline)

		#if a process is finished, remove it
		finished = [p for p in removeprocesses if p not in processes and removeprocesses[p] < time]
		for p in finished:
			removeprocesses.pop(p)
		if (len(removeprocesses) == 0):
			break

		#go through processes
		for p in processes:
			#if a process is arriving
			if processes[p][0][0] == time:
				#save when it will leave and how much memory it needs
				removeprocesses[p] = time + processes[p][0][1]
				sizeneeded = sizeprocess[p]
				#note if defragmentation happened and print info
				if p != defragprocess:
					print("time {}ms: Process {} arrived (requires {} frames)".format(time, p, sizeneeded))
				else:
					defragprocess = '.'

				#if there isn't enough space left, skip it
				if memory.count(".") < sizeneeded:
					print("time {}ms: Cannot place process {} -- skipped!".format(time, p))
					removeprocesses[p] = -1
					processes[p].pop(0)
					continue

				#vars to find the best amount and space and it's location in memory
				bestspace = float("inf")
				bestpointer = -1
				startpointer = 0
				freespace = 0

				#go through memory
				for i in range(len(memory)):
					#find size of open space and compare to smallest open space large enough to hold memory so far
					if memory[i] != ".":
						if freespace >= sizeneeded and freespace < bestspace:
							bestspace = freespace
							bestpointer = startpointer
						freespace = 0
						continue
					#count freespace
					if freespace == 0:
						startpointer = i
					freespace += 1

				#Corner case for empty memory
				if freespace >= sizeneeded and freespace < bestspace and freespace != 0:
					bestspace = freespace
					bestpointer = startpointer

				#if there isn't a large enough memory block, defragment and print info
				if bestpointer == -1:
					print("time {}ms: Cannot place process {} -- starting defragmentation".format(time, p))
					timespent, changed = defragment(memory, tmemmove)
					time += timespent
					print("time {}ms: Defragmentation complete (moved {} frames: ".format(time, int(timespent/tmemmove)), end="")
					for i in range(len(changed)-1):
						print("{}, ".format(changed[i]), end="")

					print("{})".format(changed[-1]))

					#update times for defragmentation
					for proc in processes:
						processes[proc] = [(x+timespent, y) for x, y in processes[proc]]
					for proc in removeprocesses:
						removeprocesses[proc] += timespent
					defragprocess = p
					break

				#add process to memory and best location
				for i in range(bestpointer, bestpointer + sizeneeded):
					memory[i] = p
				print("time {}ms: Placed process {}:".format(time, p))
				printmem(memory, framesperline)
				processes[p].pop(0)

		#note if defragmented
		if defragprocess != '.':
			defraged = '.'
			continue

		time += 1

	time -= 1
	print("time {}ms: Simulator ended (Contiguous -- Best-Fit)".format(time))

#noncontigous memory function
def noncontiguous(framesperline, memsize, p, sp):
	#initialize variables
	time = 0
	processes = copy.deepcopy(p)
	sizeprocess = sp.copy()
	removeprocesses = {}
	#copy processes
	for key in processes.keys():
		removeprocesses[key] = -1
	#initialize memory
	memory = ["."] * memsize

	#pageTable is a dictionary with processes as the key and the value being a list of tuples containing the starting
	#and ending index in memory of the process
	#example
	#pageTable["A"] = [(0, 5), (8, 10)]
	#means that A is set between 0 and 5 and 8 and 10 inclusive
	pageTable = {}

	print("time {}ms: Simulator started (Non-Contiguous)".format(time))

	#while there are unfinished processes
	while len(removeprocesses):
		#if a processes has finished, remove it
		toremove = [p for p in processes if len(processes[p]) == 0]
		for p in toremove:
			processes.pop(p)

		#go through the processes
		for p in removeprocesses:
			#if a process is done running
			if removeprocesses[p] == time:
				#use the page table to remove the memory for the process at all locations, then print info about it
				for i in range(len(pageTable[p])):
					for j in range(pageTable[p][i][0], pageTable[p][i][1] + 1):
						memory[j] = "."
				print("time {}ms: Process {} removed:".format(time, p))
				pageTable.pop(p)
				printmem(memory, framesperline)

		#if a process is finished, remove it
		finished = [p for p in removeprocesses if p not in processes and removeprocesses[p] < time]
		for p in finished:
			removeprocesses.pop(p)
		if (len(removeprocesses) == 0):
			break

		#take all the processes and order them alphabetically
		orderedProc = []
		for p in processes:
			orderedProc.append(p)

		orderedProc.sort()

		#go through proceses in alphabetical order
		for p in orderedProc:

			#if a process arrived
			if processes[p][0][0] == time:
				#save when it will leave and how much memory it needs
				removeprocesses[p] = time + processes[p][0][1]
				sizeneeded = sizeprocess[p]

				print("time {}ms: Process {} arrived (requires {} frames)".format(time, p, sizeneeded))

				#if there isn't enough space left, skip it
				if memory.count(".") < sizeneeded:
					print("time {}ms: Cannot place process {} -- skipped!".format(time, p))
					removeprocesses[p] = -1
					processes[p].pop(0)
					continue

				#initialixe the process in the page table
				pageTable[p] = []
				starter = -1
				toAdd = sizeneeded
				#go through the memory
				for i in range(len(memory)):
					#if the memory is open and the counter hasn't started, start adding to memory and set the start index
					if memory[i] == "." and starter == -1:
						starter = i
						memory[i] = p
						sizeneeded -= 1
					#if the start index is in use and the memory is free, keep adding the process memory
					elif memory[i] == "." and starter != -1:
						memory[i] = p
						sizeneeded -= 1
					#if there's no more free memory and the starter was set, add the start and end point to the page
					#table and reset the start index
					elif memory[i] != "." and starter != -1:
						pageTable[p].append((starter, i-1))
						starter = -1

					#once the process is added to memory, add the last section to the page table and break
					if sizeneeded == 0:
						pageTable[p].append((starter, i))
						starter = -1
						break

				#print memory info
				print("time {}ms: Placed process {}:".format(time, p))
				printmem(memory, framesperline)
				processes[p].pop(0)

		time += 1
	time -= 1
	print("time {}ms: Simulator ended (Non-Contiguous)".format(time))

#main function
if __name__ == "__main__":
	#make sure there are the right number of arguments
	if len(sys.argv) != 5:
		sys.stderr.write("ERROR: Incorrect number of command line arguments\n");
		sys.exit(1)

	#make sure arguments are correct type
	if not (sys.argv[1].isdigit() and sys.argv[2].isdigit() and sys.argv[4].isdigit()):
		sys.stderr.write("ERROR: Usage project2.py <frames per line> <memory size> <input file> <tmemmove>\n")
		sys.exit(1)

	#save arguments in variables
	framesperline = int(sys.argv[1])

	memsize = int(sys.argv[2])

	infile = sys.argv[3]

	tmemmove = int(sys.argv[4])

	#processes is a dictionary
	#	The key is the process
	# The value is a list of tuples
	#		The 2-tuple values are arrival time and process duration
	#	Example:
	#		processes["A"] = [(100, 50)]
	#		means process A needs memory for only one burst starting at time 
	#		100 and lasting 50ms (so will exit at time 150)
	processes = {}

	#sizeprocess is a dictionary 
	# Key -> process name
	# Value -> how many frames of memory the process requires
	sizeprocess = {}

	#try to open the file
	try:
		file = open(infile, "r")

		#for each line in the file
		for line in file:
			#remove white space
			if line.strip() == "" or line.strip()[0] == "#":
				continue
			line = line.strip().split()
			p = line[0]
			processes[p] = []

			#save the memory needed for the process
			sizeprocess[p] = int(line[1])
			line = line[2:]

			#save the info in the line to processes
			for l in line:
				times = l.split("/")
				processes[p].append((int(times[0]),int(times[1])))
	#else print the error with opening the file
	except IOError as err:
		sys.stderr.write("ERROR: {}\n".format(err))
		sys.exit(1)
	file.close()

	#Function calls for each of the four algorithms
	firstfit(framesperline, memsize, tmemmove, processes, sizeprocess)
	print()
	nextfit(framesperline, memsize, tmemmove, processes, sizeprocess)
	print()
	bestfit(framesperline, memsize, tmemmove, processes, sizeprocess)
	print()
	noncontiguous(framesperline, memsize, processes, sizeprocess)



