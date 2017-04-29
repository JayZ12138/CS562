from snapshot import Snapshot

def main():
	fname = 'snapshot_test.txt'
	with open(fname, 'r') as f:
		line = f.readline().split()
		Sindex = Snapshot([line[1], int(line[0]), '*'])
		for l in f:
			line = l.split()
			op = line[2]
			if(op == 'b'):
				Sindex.insert([line[1], int(line[0]), '*'])
			elif(op == 'd'):
				Sindex.delete(line[1], int(line[0]))
	# print(Sindex.blocks.SP.next_node.block.id)
	# print(Sindex.blocks.SP.next_node.Pce_node.block.record_list)
	# print(Sindex.AT)
	# print(Sindex.alives_entries)
	# print(Sindex.tsquery(5))
	s = Sindex.tsquery(5)|Sindex.tsquery(6)|Sindex.tsquery(7)
	s = sorted(list(s))
	y = sorted(list(Sindex.trquery(5,7)))
	print(s)
	print(y)
	print(s==y)
if __name__=='__main__':
	main()