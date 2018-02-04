from snapshot import Snapshot
from tqdm import tqdm
import sys
import time

CAPACITY=2000
UTILIZE=0.2

def main():
	fname = 'snapshot_test.txt'
	print('Start reading and indexing file...')
	start = time.time()
	with open(fname, 'r') as f:
		pbar = tqdm(total=2377471)
		line = f.readline().split()
		Sindex = Snapshot([line[1], int(line[0]), '*'], cap=CAPACITY, ut=UTILIZE)
		for l in f:
			line = l.split()
			op = line[2]
			if(op == 'b'):
				Sindex.insert([line[1], int(line[0]), '*'], cap=CAPACITY, ut=UTILIZE)
			elif(op == 'd'):
				Sindex.delete(line[1], int(line[0]))
			pbar.update(1)
	duration = time.time() - start
	print('')
	print('Index done in: {0:.2f}s '.format(duration))
	print('')
	print('Enter the query type (ts or tr) and time')
	print('timeslice query format: ts time_instance')
	print('timerrange query format: tr min_time max_time')
	print('Enter anything else to quit')
	print('')
	for line in sys.stdin:
		qtype, *t = line.split()
		if(qtype == 'ts'):
			start = time.time()
			result = Sindex.tsquery(int(t[0]))
			duration = time.time() - start
		elif(qtype == 'tr'):
			start = time.time()
			result = Sindex.trquery(int(t[0]), int(t[1]))
			duration = time.time() - start
		else:
			quit()
		print('result: ',result)
		print('')
		print('Get time result in {0:.5f}s'.format(duration))

	# s = Sindex.tsquery(5)|Sindex.tsquery(6)|Sindex.tsquery(7)
	# s = sorted(list(s))
	# y = sorted(list(Sindex.trquery(5,7)))
	# print(s)
	# print(y)
	# print(s==y)
if __name__=='__main__':
	main()