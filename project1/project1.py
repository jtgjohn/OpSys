import sys


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









if __name__ == "__main__":
	print(len(sys.argv))
	print(sys.argv)

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
	if sys.argv[8] == "BEGINNING":
		rr_add = sys.argv[8]


	rand = Rand48(0)
	rand.srand(seed)
	print(rand.drand())
	print(rand.drand())



