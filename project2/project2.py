import sys
import math
import copy


def printmem(mem, framesperline):
	print("="*framesperline)
	i = 0
	while i < len(mem):
		count = 0
		for j in range(i, min(i+framesperline,len(mem))):
			print(mem[j], end="")
			count += 1
		print()
		i += count
	print("="*framesperline)

def defragment(mem, tmemmove):
	movecost = 0
	changed = []
	for i in range(len(mem)):
		if mem[i] == ".":
			for j in range(i+1, len(mem)):
				if mem[j] != ".":
					if mem[j] not in changed:
						changed.append(mem[j])
					mem[i] = mem[j]
					mem[j] = "."
					movecost += tmemmove
					break

	return movecost, changed



def firstfit(framesperline, memsize, tmemmove, p, sp):
	time = 0
	processes = copy.deepcopy(p)
	sizeprocess = sp.copy()
	removeprocesses = {}
	for key in processes.keys():
		removeprocesses[key] = -1
	memory = ["."] * memsize
	defragprocess = '.'

	print("time {}ms: Simulator started (Contiguous -- First-Fit)".format(time))


	while len(removeprocesses):
		toremove = [p for p in processes if len(processes[p]) == 0]
		for p in toremove:
			processes.pop(p)

		for p in removeprocesses:
			if removeprocesses[p] == time:
				for i in range(len(memory)):
					if memory[i] == p:
						memory[i] = "."
				print("time {}ms: Process {} removed:".format(time, p))
				printmem(memory, framesperline)

		finished = [p for p in removeprocesses if p not in processes and removeprocesses[p] < time]
		for p in finished:
			removeprocesses.pop(p)
		if (len(removeprocesses) == 0):
			break

		for p in processes:

			if processes[p][0][0] == time:
				removeprocesses[p] = time + processes[p][0][1]
				sizeneeded = sizeprocess[p]
				if p != defragprocess:
					print("time {}ms: Process {} arrived (requires {} frames)".format(time, p, sizeneeded))
				else:
					defragprocess = '.'
				if memory.count(".") < sizeneeded:
					print("time {}ms: Cannot place process {} -- skipped!".format(time, p))
					removeprocesses[p] = -1
					processes[p].pop(0)
					continue
				startpointer = 0
				freespace = 0
				for i in range(len(memory)):
					if memory[i] != ".":
						freespace = 0
						continue
					if freespace == 0:
						startpointer = i
					freespace += 1
					if freespace == sizeneeded:
						break

				if freespace < sizeneeded:
					print("time {}ms: Cannot place process {} -- starting defragmentation".format(time, p))
					timespent, changed = defragment(memory, tmemmove)
					time += timespent
					print("time {}ms: Defragmentation complete (moved {} frames: ".format(time, int(timespent/tmemmove)), end="")
					for i in range(len(changed)-1):
						print("{}, ".format(changed[i]), end="")

					print("{})".format(changed[-1]))

					for proc in processes:
						processes[proc] = [(x+timespent, y) for x, y in processes[proc]]
					for proc in removeprocesses:
						removeprocesses[proc] += timespent
					defragprocess = p
					break

				for i in range(startpointer, startpointer + sizeneeded):
					memory[i] = p
				print("time {}ms: Placed process {}:".format(time, p))
				printmem(memory, framesperline)
				processes[p].pop(0)

		if defragprocess != '.':
			defraged = '.'
			continue



		time += 1

	time -= 1
	print("time {}ms: Simulator ended (Contiguous -- First-Fit)".format(time))






if __name__ == "__main__":
	if len(sys.argv) != 5:
		sys.stderr.write("ERROR: Incorrect number of command line arguments\n");
		sys.exit(1)

	if not (sys.argv[1].isdigit() and sys.argv[2].isdigit() and sys.argv[4].isdigit()):
		sys.stderr.write("ERROR: Usage project2.py <frames per line> <memory size> <input file> <tmemmove>\n")
		sys.exit(1)

	framesperline = int(sys.argv[1])

	memsize = int(sys.argv[2])

	infile = sys.argv[3]

	tmemmove = int(sys.argv[4])

	processes = {}
	sizeprocess = {}

	try:
		file = open(infile, "r")

		for line in file:
			if line.strip() == "" or line.strip()[0] == "#":
				continue
			line = line.strip().split()
			p = line[0]
			processes[p] = []
			sizeprocess[p] = int(line[1])
			line = line[2:]
			for l in line:
				times = l.split("/")
				processes[p].append((int(times[0]),int(times[1])))
	except IOError as err:
		sys.stderr.write("ERROR: {}\n".format(err))
		sys.exit(1)
	file.close()
	firstfit(framesperline, memsize, tmemmove, processes, sizeprocess)



