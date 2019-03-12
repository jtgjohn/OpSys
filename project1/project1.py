import sys
import math
from heapq import heappush, heappop

alphabet = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'}

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

def SJF(p, tau0, alpha):
	processes = p.copy()
	print("time 0ms: Simulator started for SJF [Q empty]")

	process_taus = dict()
	for processkey in processes.keys():
		process_taus[processkey] = tau0
	timer = 0
	waittime = 0
	turnaroundtime = 0
	queue = []

	while len(processes):


		timer += 1
		return 1





def STR(p, tau0, alpha):
	processes = p.copy()
	print("time 0ms: Simulator started for SJF [Q empty]")

def RR(p, t_slice):
	processes = p.copy()
	print("time 0ms: Simulator started for SJF [Q empty]")





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

	for i in range(num_processes):
		processes[i] = [[],[]]
		upper = upper_bound + 1
		while upper > upper_bound:
			upper = int(-math.log(rand.drand())/y)
		arrival_times[i] = upper
		num_bursts = int(rand.drand() * 100) + 1
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

		print(sum(processes[i][0])/len(processes[i][0]))
		print(len(processes[i][0]))
	print(arrival_times)

	SJF(processes, 1/y, alpha)



