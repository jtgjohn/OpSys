import sys
import math
from heapq import heappush, heappop
import copy

alphabet = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F', 7: 'G', 8: 'H', 9: 'I', 10: 'J', 11: 'K', 12: 'L', 13: 'M', 14: 'N', 15: 'O', 16: 'P', 17: 'Q', 18: 'R', 19: 'S', 20: 'T', 21: 'U', 22: 'V', 23: 'W', 24: 'X', 25: 'Y', 26: 'Z'}

############################################################################
# Taken From StackOverflow
# https://stackoverflow.com/questions/7287014/is-there-any-drand48-equivalent-in-python-or-a-wrapper-to-it

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


def FCFS(processes):
	print("time 0ms: Simulator started for FCFS [Q empty]")
	RR(processes, float("inf"))

def SJF(p, tau0, alpha, t_cs, at):
	arrival_times = at.copy()
	processes = {}
	print(p)

	for i in p.keys():
		processes[i] = [[],[]]
		processes[i][0] = p[i][0].copy()
		processes[i][1] = p[i][1].copy()

	print("time 0ms: Simulator started for SJF [Q empty]")

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


	while len(processes) or end_cs:
		#check for newly arriving processes, either from finished io or new arrival
		for i in processes.keys():
			if i != running_process and arrival_times[i] == timer:
				
				#update tau for next time based on this cpu burst length
				process_taus[i] = (alpha * processes[i][0][0]) + ((1 - alpha) * process_taus[i])
				if at[i] == arrival_times[i]: #first arrival
					print("time {}ms: Process {} arrived {}".format(timer, alphabet[i], Qstr(queue)))
				else: #finished io burst
					print("time {}ms: Process {} finished performing I/O {}".format(timer, alphabet[i], Qstr(queue)))
				heappush(queue, (process_taus[i], i))
				waittime -= 1 #to account for newly arrived processes that havent waited yet
		waittime += len(queue)

		#if a process is running, and not during a context switch, decriment its runtime
		#if it is the last cpu burst for the process, remove it from dict of processes
		if running_process and not start_cs and not end_cs:
			processes[running_process][0][0] -= 1
			turnaroundtime += 1
			if processes[running_process][0][0] == 0:
				end_cs = True
				remaining_cs = int(t_cs/2)
				processes[running_process][0].pop(0)
				print("time {}ms: Process {} finishes using the CPU {}".format(timer, alphabet[running_process], Qstr(queue)))
				if len(processes[running_process][0]) == 0:
					processes.pop(running_process)
					print("time {}ms: Process {} terminates by finishing its last CPU burst {}".format(timer, alphabet[running_process], Qstr(queue)))



		#only decriment context switch time if it didnt finish in this loop iteration
		elif (start_cs or end_cs) and remaining_cs > 0:
			remaining_cs -= 1
			turnaroundtime += 1



		#if a context switch into the queue is occuring and finishes, it starts using the cpu
		if start_cs and remaining_cs == 0:
			num_cs += 1
			print("time {}ms: Process {} starts using the CPU {}".format(timer, alphabet[running_process], Qstr(queue)))
			start_cs = False



		#if a process finishes switching out of the queue, run its io burst
		elif end_cs and remaining_cs == 0:
			end_cs = False
			if running_process in processes.keys():
				arrival_times[running_process] = timer + 1 + processes[running_process][1].pop(0)
			running_process = None

		# start running a new process if none is running or being switched out
		if not running_process and not end_cs: #no process currently using CPU
			if len(queue) > 0: #queue is not empty
				running_process = heappop(queue)[1]
				remaining_cs = int(t_cs/2)
				start_cs = True
	


		


		timer += 1
	print("time {}ms: Simulator ended for SFJ {}".format(timer, Qstr(queue)))
	num_bursts = 0
	cpubursttime = 0
	turnaroundtime += waittime
	for process in p.values():
		cpubursttime += sum(process[0])
		num_bursts += len(process[0])

	avg_turnaroundtime = turnaroundtime/num_bursts
	avg_cpubursttime = cpubursttime/num_bursts
	avg_waittime = waittime/num_bursts

	finalstats = "Algorithm SJF\n"
	finalstats += "--average CPU burst time: {0:.3f} ms\n".format(avg_cpubursttime)
	finalstats += "--average wait time: {0:.3f} ms\n".format(avg_waittime)
	finalstats += "--average turnaround time: {0:.3f} ms\n".format(avg_turnaroundtime)
	finalstats += "-- total number of context switches: {}\n".format(num_cs)
	finalstats += "--total number of preemptions: 0\n"

	return finalstats





def STR(p, tau0, alpha):
	processes = p.copy()
	print("time 0ms: Simulator started for SJF [Q empty]")

def RR(p, t_slice):
	processes = p.copy()
	print("time 0ms: Simulator started for SJF [Q empty]")


def Qstr(queue):
	contents = "[Q"
	if len(queue) == 0:
		contents += " empty"
	for item in sorted(queue):
		contents += " "
		contents += alphabet[item[1]]
	contents += "]"
	return contents



if __name__ == "__main__":

	if len(sys.argv) != 8 and len(sys.argv) != 9:
		sys.stderr.write("ERROR: Incorrect number of command line arguments\n")
		sys.exit(1)

	seed = int(sys.argv[1])

	y = float(sys.argv[2])

	upper_bound = int(sys.argv[3])

	num_processes = int(sys.argv[4])

	t_cs = int(sys.argv[5])

	alpha = float(sys.argv[6])

	t_slice = int(sys.argv[7])

	rr_add = "END"
	if len(sys.argv) == 9 and sys.argv[8] == "BEGINNING":
		rr_add = sys.argv[8]


	rand = Rand48(0)
	rand.srand(seed)

	# processes is a dictionary of:
	# 	Key: process number 1-25
	#		Value: List holding two lists:
	#			list[0] is a ordered list of cpu burst duration times
	#			list[1] is a list of io burst times
	processes = dict()
	arrival_times = dict()

	for i in range(1, num_processes + 1):
		processes[i] = [[],[]]
		upper = upper_bound + 1
		while upper > upper_bound:
			upper = int(-math.log(rand.drand())/y)
		arrival_times[i] = upper
		num_bursts = int(rand.drand() * 100) + 1
		#print("Process {} (arrival time {} ms) {} CPU bursts".format(alphabet[i], upper, num_bursts))
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
			#print("--> CPU burst {} ms --> I/O burst {} ms".format(processes[i][0][-1], upper))

	# 	print(sum(processes[i][0])/len(processes[i][0]))
	# 	print(len(processes[i][0]))
	# print(arrival_times)
	# print(processes)

	file = open("simout.txt", "w")


	file.write(SJF(processes, 1/y, alpha, t_cs, arrival_times))


	# test = {1: [[18],[]], 2: [[3],[]], 3: [[4], []]}
	# atest = {1: 0, 2: 0, 3:0}
	# file.write(SJF(test, 5, 0.5, 2, atest))



