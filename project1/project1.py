import sys
import math
from heapq import heappush, heappop
import copy

#dictionary to match process numbers to letters
alphabet = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'}

############################################################################
# Taken From StackOverflow
# https://stackoverflow.com/questions/7287014/is-there-any-drand48-equivalent-in-python-or-a-wrapper-to-it

#class to get a random number given a seed
class Rand48(object):
    def __init__(self, seed):
        self.n = seed
    def seed(self, seed):
        self.n = seed
    def srand(self, seed):
        self.n = (seed << 16) + 0x330e
    def next(self):
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n
    def drand(self):
        return self.next() / 2**48
    def lrand(self):
        return self.next() >> 17
    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n 

############################################################################

#First come, First serve just runs round robin with an infinite time slice and states the algorithm is called FCFS
def FCFS(processes, arrival_times,t_cs):
	return RR(processes, float("inf"), "FCFS",t_cs,arrival_times)

#shortest job first
def SJF(p, tau0, alpha, t_cs, at):

	#copy arrival times and processes, then print the info for them
	arrival_times = at.copy()
	processes = copy.deepcopy(p)
	for i in processes:
		if len(processes[i][0]) > 1:
			print("Process {} [NEW] (arrival time {} ms) {} CPU bursts".format(alphabet[i], arrival_times[i], len(processes[i][0])))
		else:
			print("Process {} [NEW] (arrival time {} ms) {} CPU burst".format(alphabet[i], arrival_times[i], len(processes[i][0])))
	
	#start the simulator
	print("time 0ms: Simulator started for SJF [Q <empty>]")

	#variables to keep track of time, what's running, context switch, and turnaround times
	running_process = None
	process_taus = dict()
	for processkey in processes.keys():
		process_taus[processkey] = tau0
	timer = 0
	waittime = 0
	turnaroundtime = 0
	queue = []
	remaining_cs= 0
	num_cs = 0
	start_cs = False
	end_cs = False

	#go through the processes until they finish
	while len(processes) or end_cs:

		#if a process is running, and not during a context switch, decriment its runtime
		#if it is the last cpu burst for the process, remove it from dict of processes
		if running_process and not start_cs and not end_cs:
			processes[running_process][0][0] -= 1
			turnaroundtime += 1
			#if the process finished a cpu burst
			if processes[running_process][0][0] == 0:
				end_cs = True
				remaining_cs = int(t_cs/2)
				processes[running_process][0].pop(0)

				#say that the process completed a cpu birst
				if timer < 1000:
					if len(processes[running_process][0]) == 1:
						print("time {}ms: Process {} completed a CPU burst; {} burst to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(sorted(queue))))
					else:
						print("time {}ms: Process {} completed a CPU burst; {} bursts to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(sorted(queue))))
					print("time {}ms: Recalculated tau = {}ms for process {} {}".format(timer, process_taus[running_process], alphabet[running_process], Qstr(sorted(queue))))

				#if that was the last cpu burst, remove it from the processes list and say it
				if len(processes[running_process][0]) == 0:
					processes.pop(running_process)
					print("time {}ms: Process {} terminated {}".format(timer, alphabet[running_process], Qstr(sorted(queue))))
				#else move the process to io
				elif timer < 1000:
					print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms {}".format(timer, alphabet[running_process], int(t_cs/2) + timer + processes[running_process][1][0], Qstr(sorted(queue))))

		#only decriment context switch time if it didnt finish in this loop iteration
		elif (start_cs or end_cs) and remaining_cs > 0:
			remaining_cs -= 1
			turnaroundtime += 1

		#if a context switch into the queue is occuring and finishes, it starts using the cpu
		if start_cs and remaining_cs == 0:
			num_cs += 1
			if timer < 1000:
				print("time {}ms: Process {} started using the CPU for {}ms burst {}".format(timer, alphabet[running_process], processes[running_process][0][0], Qstr(sorted(queue))))
			start_cs = False

		#if a process finishes switching out of the queue, run its io burst
		elif end_cs and remaining_cs == 0:
			end_cs = False
			#run the io burst
			if running_process in processes.keys():
				arrival_times[running_process] = timer + processes[running_process][1].pop(0)
			running_process = None

		#add the length of processes waiting as the wait time
		waittime += len(queue)

		#check for newly arriving processes, either from finished io or new arrival
		for i in processes.keys():
			#if the process isn't running and it just arrived
			if i != running_process and arrival_times[i] == timer:
				#push it to the queue and print out it's info
				heappush(queue, (process_taus[i], i))
				if timer < 1000:
					if at[i] == arrival_times[i]: #first arrival
						print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(timer, alphabet[i], process_taus[i], Qstr(sorted(queue))))
					else: #finished io burst
						print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue {}".format(timer, alphabet[i], process_taus[i], Qstr(sorted(queue))))
				#update tau for next time based on this cpu burst length
				process_taus[i] = math.ceil((alpha * processes[i][0][0]) + ((1 - alpha) * process_taus[i]))
				

		# start running a new process if none is running or being switched out
		if not running_process and not end_cs: #no process currently using CPU
			if len(queue) > 0: #queue is not empty
				running_process = heappop(queue)[1]
				remaining_cs = int(t_cs/2)
				start_cs = True
	

		timer += 1

	#reset timer back one for the last increment
	timer -= 1

	#end the simulation
	print("time {}ms: Simulator ended for SJF {}".format(timer, Qstr(sorted(queue))))

	#make last calculations on time and number of bursts
	num_bursts = 0
	cpubursttime = 0
	turnaroundtime += waittime
	for process in p.values():
		cpubursttime += sum(process[0])
		num_bursts += len(process[0])

	avg_turnaroundtime = turnaroundtime/num_bursts
	avg_cpubursttime = cpubursttime/num_bursts
	avg_waittime = waittime/num_bursts

	#print stats
	finalstats = "Algorithm SJF\n"
	finalstats += "-- average CPU burst time: {0:.3f} ms\n".format(avg_cpubursttime)
	finalstats += "-- average wait time: {0:.3f} ms\n".format(avg_waittime)
	finalstats += "-- average turnaround time: {0:.3f} ms\n".format(avg_turnaroundtime)
	finalstats += "-- total number of context switches: {}\n".format(num_cs)
	finalstats += "-- total number of preemptions: 0\n"
	print()
	return finalstats

#shortest remaining time algo
def SRT(p, tau0, alpha, t_cs, at):

	#copy arrival times and processes, then print the info for them
	arrival_times = at.copy()
	processes = copy.deepcopy(p)

	#keep track of the preemptions
	preempted = dict()
	process_taus = dict()
	last_cpu_burst = dict()

	for i in processes:
		if len(processes[i][0]) > 1:
			print("Process {} [NEW] (arrival time {} ms) {} CPU bursts".format(alphabet[i], arrival_times[i], len(processes[i][0])))
		else:
			print("Process {} [NEW] (arrival time {} ms) {} CPU burst".format(alphabet[i], arrival_times[i], len(processes[i][0])))
		
		#initialize preemptions and taus
		preempted[i] = False
		process_taus[i] = tau0

	#start the simulation
	print("time 0ms: Simulator started for SRT [Q <empty>]")

	#variables to keep track of time, what's running, context switches, turnaround times, and preemptions
	running_process = None
	
	timer = 0
	waittime = 0
	turnaroundtime = 0
	queue = []
	remaining_cs= 0
	num_cs = 0
	num_preemptions = 0
	start_cs = False
	end_cs = False
	process_preempted = False

	#go through the processes until they finish
	while len(processes) or end_cs:

		#if a process is running, and not during a context switch, decriment its runtime
		#if it is the last cpu burst for the process, remove it from dict of processes
		if running_process and not start_cs and not end_cs:
			processes[running_process][0][0] -= 1
			turnaroundtime += 1
			#if the process finished a cpu burst
			if processes[running_process][0][0] == 0:
				end_cs = True
				remaining_cs = int(t_cs/2)
				processes[running_process][0].pop(0)
				#update tau for next time based on last cpu burst length
				process_taus[running_process] = math.ceil((alpha * last_cpu_burst[running_process]) + ((1 - alpha) * process_taus[running_process]))
				#if the process terminated
				if len(processes[running_process][0]) == 0:
					processes.pop(running_process)
					print("time {}ms: Process {} terminated {}".format(timer, alphabet[running_process], Qstr(sorted(queue))))
				else:
					if timer < 1000:
						#if there is only 1 more burst to go
						if len(processes[running_process][0]) > 1:
							print("time {}ms: Process {} completed a CPU burst; {} bursts to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(sorted(queue))))
						#if there are multiple bursts to go
						else:
							print("time {}ms: Process {} completed a CPU burst; {} burst to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(sorted(queue))))
						print("time {}ms: Recalculated tau = {}ms for process {} {}".format(timer, process_taus[running_process], alphabet[running_process], Qstr(sorted(queue))))

						#switch to io
						if running_process in processes:
							print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms {}".format(timer, alphabet[running_process], int(t_cs/2) + timer + processes[running_process][1][0], Qstr(sorted(queue))))
					preempted[running_process] = False


		#only decriment context switch time if it didnt finish in this loop iteration
		elif (start_cs or end_cs) and remaining_cs > 0:
			remaining_cs -= 1
			turnaroundtime += 1

		#if a context switch into the queue is occuring and finishes, it starts using the cpu
		if start_cs and remaining_cs == 0:
			num_cs += 1
			if timer < 1000:
				#if the process was preempted, change the wording on how it starts using the cpu
				if preempted[running_process]:
					print("time {}ms: Process {} started using the CPU with {}ms remaining {}".format(timer, alphabet[running_process], processes[running_process][0][0], Qstr(sorted(queue))))
				else:
					print("time {}ms: Process {} started using the CPU for {}ms burst {}".format(timer, alphabet[running_process], processes[running_process][0][0], Qstr(sorted(queue))))
		
			start_cs = False

			#check for a preemption
			if len(queue):
				#remove and add the first in the queue
				first_in_queue = heappop(queue)
				heappush(queue, first_in_queue)
				#if there's a preemption, state it and set a variable to remember it
				if process_taus[first_in_queue[1]] < process_taus[running_process] - (last_cpu_burst[running_process] - processes[running_process][0][0]):
					if timer < 1000:
						print("time {}ms: Process {} (tau {}ms) will preempt {} {}".format(timer, alphabet[first_in_queue[1]], process_taus[first_in_queue[1]], alphabet[running_process], Qstr(sorted(queue))))

					end_cs = True
					process_preempted = True
					remaining_cs = t_cs/2



		#if a process finishes switching out of the queue, run its io burst
		elif end_cs and remaining_cs == 0 and not process_preempted:
			end_cs = False
			#if the running prosess is in the recieved processes, set the next arrival time after io burst
			if running_process in processes.keys():
				arrival_times[running_process] = timer + processes[running_process][1].pop(0)
			running_process = None
		waittime += len(queue)

		#check for newly arriving processes, either from finished io or new arrival
		for i in processes.keys():
			#if the process isn't running and it just arrived
			if i != running_process and arrival_times[i] == timer:
				heappush(queue, (process_taus[i], i))

				#preemption occurs
				if running_process != None and process_taus[i] < process_taus[running_process] - (last_cpu_burst[running_process] - processes[running_process][0][0]) and not start_cs and not end_cs:
					if timer < 1000:
						if at[i] == arrival_times[i]: #first arrival
							print("time {}ms: Process {} (tau {}ms) arrived and will preempt {} {}".format(timer, alphabet[i], process_taus[i], alphabet[running_process], Qstr(sorted(queue))))
						else: #finished io burst
							print("time {}ms: Process {} (tau {}ms) completed I/O and will preempt {} {}".format(timer, alphabet[i], process_taus[i], alphabet[running_process], Qstr(sorted(queue))))
					#preempted process already did some cpu
					if last_cpu_burst[running_process] > processes[running_process][0][0]:
						preempted[running_process] = True
					
					end_cs = True
					process_preempted = True
					remaining_cs = int(t_cs/2)
				#else it arrives and there's no preemption
				else:
					if timer < 1000:
						if at[i] == arrival_times[i]: #first arrival
							print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue {}".format(timer, alphabet[i], process_taus[i], Qstr(sorted(queue))))
						else: #finished io burst
							print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue {}".format(timer, alphabet[i], process_taus[i], Qstr(sorted(queue))))
					last_cpu_burst[i] = processes[i][0][0]
				last_cpu_burst[i] = processes[i][0][0]

		#reset variables
		if end_cs and process_preempted and remaining_cs == 0:
			num_preemptions += 1
			end_cs = False
			heappush(queue, (process_taus[running_process] - (last_cpu_burst[running_process] - processes[running_process][0][0]), running_process))
			running_process =  heappop(queue)[1]
			start_cs = True
			remaining_cs = int(t_cs/2)
			process_preempted = False

		# start running a new process if none is running or being switched out
		if not running_process and not end_cs: #no process currently using CPU
			if len(queue) > 0: #queue is not empty
				running_process = heappop(queue)[1]
				remaining_cs = int(t_cs/2)
				start_cs = True
	

		timer += 1

	#reset timer back one for the last increment
	timer -= 1

	#print that the simulation is over
	print("time {}ms: Simulator ended for SRT {}".format(timer, Qstr(sorted(queue))))
	#do some final calculations for timing and bursts
	num_bursts = 0
	cpubursttime = 0
	turnaroundtime += waittime
	for process in p.values():
		cpubursttime += sum(process[0])
		num_bursts += len(process[0])

	avg_turnaroundtime = turnaroundtime/num_bursts
	avg_cpubursttime = cpubursttime/num_bursts
	avg_waittime = waittime/num_bursts

	#print final stats
	finalstats = "Algorithm SRT\n"
	finalstats += "-- average CPU burst time: {0:.3f} ms\n".format(avg_cpubursttime)
	finalstats += "-- average wait time: {0:.3f} ms\n".format(avg_waittime)
	finalstats += "-- average turnaround time: {0:.3f} ms\n".format(avg_turnaroundtime)
	finalstats += "-- total number of context switches: {}\n".format(num_cs)
	finalstats += "-- total number of preemptions: {}\n".format(num_preemptions)
	print()
	return finalstats

#round robin algo
def RR(p, t_slice, alg_name,t_cs,at):

	#copy arrival time and processes and print them
	arrival_times = at.copy()
	processes = copy.deepcopy(p)
	for i in processes:
		if len(processes[i][0]) > 1:
			print("Process {} [NEW] (arrival time {} ms) {} CPU bursts".format(alphabet[i], arrival_times[i], len(processes[i][0])))
		else:
			print("Process {} [NEW] (arrival time {} ms) {} CPU burst".format(alphabet[i], arrival_times[i], len(processes[i][0])))
	print("time 0ms: Simulator started for {} [Q <empty>]".format(alg_name))

	#initialize variables for context switches, preemptions, time, and bursts
	isPreemp = False
	preeCount = 0
	running_process = None
	preemptionTimer = 0
	timer = 0
	waittime = 0
	turnaroundtime = 0
	queue = []
	remaining_cs= 0
	num_cs = 0
	start_cs = False
	end_cs = False

	twasPre = set()

	#go through the running processes
	while len(processes) or end_cs:

		#if a process is running, and not during a context switch, decriment its runtime
		#if it is the last cpu burst for the process, remove it from dict of processes
		if running_process and not start_cs and not end_cs:
			processes[running_process][0][0] -= 1
			turnaroundtime += 1
			#if the cpu burst ended
			if processes[running_process][0][0] == 0:
				#set variables and pop the cpu burst
				preemptionTimer = 0
				end_cs = True
				remaining_cs = int(t_cs/2)
				processes[running_process][0].pop(0)
				if timer < 1000 and len(processes[running_process][0]) != 0:
					#print the info depending on if it has 1 or more cpu bursts to go
					if len(processes[running_process][0]) == 1:
						print("time {}ms: Process {} completed a CPU burst; {} burst to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(queue)))
					else:
						print("time {}ms: Process {} completed a CPU burst; {} bursts to go {}".format(timer, alphabet[running_process], len(processes[running_process][0]), Qstr(queue)))
				#if there aren't any more cpu bursts
				if len(processes[running_process][0]) == 0:
					#the process terminates
					processes.pop(running_process)
					print("time {}ms: Process {} terminated {}".format(timer, alphabet[running_process], Qstr(queue)))
				#else it will move to io
				elif timer < 1000:
					print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms {}".format(timer, alphabet[running_process], int(t_cs/2) + timer + processes[running_process][1][0], Qstr(queue)))

		#only decriment context switch time if it didnt finish in this loop iteration
		elif (start_cs or end_cs) and remaining_cs > 0:
			remaining_cs -= 1
			turnaroundtime += 1

		#Preemptions
		#if the time slice has expired
		if(preemptionTimer == t_slice) and (running_process):
			#if there are other processes
			if len(queue) > 0:	
				#save that the running process was preempted
				twasPre.add(running_process)
				preeCount += 1
				timeLeft = processes[running_process][0][0]
				#let the user know the process was preempted
				if timer < 1000:
					print("time {}ms: Time slice expired; process {} preempted with {}ms to go {}".format(timer,alphabet[running_process],timeLeft,Qstr(queue)))
				
				end_cs = True
				remaining_cs = t_cs/2
				isPreemp = True
			#if there are no other processes, you don't need to preempt
			elif(timer < 1000):
				print("time {}ms: Time slice expired; no preemption because ready queue is empty {}".format(timer, Qstr(queue)))


		#if a context switch into the queue is occuring and finishes, it starts using the cpu
		if start_cs and remaining_cs == 0:
			num_cs += 1
			if timer < 1000:
				if running_process in twasPre:
					print("time {}ms: Process {} started using the CPU with {}ms remaining {}".format(timer, alphabet[running_process], processes[running_process][0][0], Qstr(queue)))
					twasPre.remove(running_process)
				else:
					print("time {}ms: Process {} started using the CPU for {}ms burst {}".format(timer, alphabet[running_process], processes[running_process][0][0], Qstr(queue)))
			start_cs = False
			preemptionTimer = 0

		#if a process finishes switching out of the queue, run its io burst
		elif end_cs and remaining_cs == 0:
			end_cs = False
			preemptionTimer = 0
			if running_process in processes.keys():
				#if there is a preemption
				if(isPreemp):
					isPreemp = False
					toAdd = (alphabet[running_process], running_process)
					queue.append(toAdd)

					waittime -= 1
				else:
					arrival_times[running_process] = timer + processes[running_process][1].pop(0)
			running_process = None

		#check for newly arriving processes, either from finished io or new arrival
		for i in processes.keys():
			if i != running_process and arrival_times[i] == timer:
				toAdd = (alphabet[i], i)
				#if the queue is set to end, add the process to the end
				if (rr_add == "END"):
					queue.append(toAdd)
				#else add it to the beginning of the queue
				else:
					queue.insert(0,toAdd)
				if timer < 1000:
					if at[i] == arrival_times[i]: #first arrival
						print("time {}ms: Process {} arrived; added to ready queue {}".format(timer, alphabet[i], Qstr(queue)))
					else: #finished io burst
						print("time {}ms: Process {} completed I/O; added to ready queue {}".format(timer, alphabet[i], Qstr(queue)))
				waittime -= 1 #to account for newly arrived processes that havent waited yet
		waittime += len(queue)

		# start running a new process if none is running or being switched out
		if not running_process and not end_cs: #no process currently using CPU
			if len(queue) > 0: #queue is not empty
				running_process = queue.pop(0)[1]
				remaining_cs = int(t_cs/2)
				start_cs = True
				preemptionTimer = 0
		preemptionTimer += 1
		timer += 1

	#reset timer back one for the last increment
	timer -= 1

	#print that the simulation ended
	print("time {}ms: Simulator ended for {} {}".format(timer,alg_name, Qstr(queue)))

	#finish calculations for time and bursts
	num_bursts = 0
	cpubursttime = 0
	turnaroundtime += waittime
	for process in p.values():
		cpubursttime += sum(process[0])
		num_bursts += len(process[0])

	avg_turnaroundtime = turnaroundtime/num_bursts
	avg_cpubursttime = cpubursttime/num_bursts
	avg_waittime = waittime/num_bursts

	#print final stats
	finalstats = "Algorithm {}\n".format(alg_name)
	finalstats += "-- average CPU burst time: {0:.3f} ms\n".format(avg_cpubursttime)
	finalstats += "-- average wait time: {0:.3f} ms\n".format(avg_waittime)
	finalstats += "-- average turnaround time: {0:.3f} ms\n".format(avg_turnaroundtime)
	finalstats += "-- total number of context switches: {}\n".format(num_cs)
	finalstats += "-- total number of preemptions: {}\n".format(preeCount)
	if(alg_name != "RR"):
		print()
	return finalstats

#function depends on a queue being a list of tuples, with index 1 being the process id
#prints out a queue as a string
def Qstr(queue):
	contents = "[Q"
	if len(queue) == 0:
		contents += " <empty>"
	#go through each item in the string and get the letter of the process
	for item in queue:
		contents += " "
		contents += alphabet[item[1]]
	contents += "]"
	return contents

#main function
if __name__ == "__main__":

	#make sure we get the correct number of arguments
	if len(sys.argv) != 8 and len(sys.argv) != 9:
		sys.stderr.write("ERROR: Incorrect number of command line arguments\n")
		sys.exit(1)

	#save the arguments into the appropriate variables
	seed = int(sys.argv[1])

	y = float(sys.argv[2])

	upper_bound = int(sys.argv[3])

	num_processes = int(sys.argv[4])

	t_cs = int(sys.argv[5])

	alpha = float(sys.argv[6])

	t_slice = int(sys.argv[7])

	#set rr_add to END unless otherwise specified
	rr_add = "END"
	if len(sys.argv) == 9 and sys.argv[8] == "BEGINNING":
		rr_add = sys.argv[8]

	#get the random seed
	rand = Rand48(0)
	rand.srand(seed)

	# processes is a dictionary of:
	# 	Key: process number 1-25
	#		Value: List holding two lists:
	#			list[0] is a ordered list of cpu burst duration times
	#			list[1] is a list of io burst times
	processes = dict()
	arrival_times = dict()

	#go through the number of processes
	for i in range(1, num_processes + 1):
		processes[i] = [[],[]]
		upper = upper_bound + 1
		while upper > upper_bound:
			upper = int(-math.log(rand.drand())/y)
		#get the arrival times and the number of bursts
		arrival_times[i] = upper
		num_bursts = int(rand.drand() * 100) + 1
		#for each burst, get the time necessary for the burst
		for j in range(num_bursts):
			upper = upper_bound + 1
			while upper > upper_bound:
				upper = math.ceil(-math.log(rand.drand())/y)
			processes[i][0].append(upper)
			if j != num_bursts-1:
				upper = upper_bound + 1
				while upper > upper_bound:
					upper = math.ceil(-math.log(rand.drand())/y)
				processes[i][1].append(upper)

	#open file to print to
	file = open("simout.txt", "w")

	#write the output from running the 4 algos to the file
	file.write(SJF(processes, math.ceil(1/y), alpha, t_cs, arrival_times))
	file.write(SRT(processes, math.ceil(1/y), alpha, t_cs, arrival_times))
	file.write(FCFS(processes,arrival_times,t_cs))
	file.write(RR(processes,t_slice,"RR",t_cs,arrival_times))

	#close the file
	file.close()
