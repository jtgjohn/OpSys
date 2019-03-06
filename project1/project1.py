import sys












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




