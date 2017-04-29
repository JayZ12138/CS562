from uuid import uuid1
class Node():

	def __init__(self, parent_node=None, next_node=None, previous_node=None,
				 Pcs_node=None,Pce_node=None,blk=None):
		# Parent pointer
		self.parent_node = parent_node
		# Next pointer
		self.next_node = next_node
		# Previous Pointer
		self.previous_node = previous_node
		# First Child pointer
		self.Pcs_node = Pcs_node
		# Last Child pointer
		self.Pce_node = Pce_node
		# pointer to the block
		self.block = blk


class Linked_list():

	def __init__(self):
		# One double linked list
		sp_block = block(['SP', 0, '*'], c=1)
		self.SP = Node(blk=sp_block)
		self.last_node = self.SP
			
	# insert a new node
	def insert(self, node):
		assert isinstance(node, Node)
		node.previous_node = self.last_node
		self.last_node.next_node = node
		self.last_node = node


	# delete a node
	def delete(self, node):
		# n previous <-> n next
		node.previous_node.next_node = node.next_node
		# n parent -> n previous
		node.parent_node = node.previous_node
		# n's parent.last child -> n
		if(node.parent_node.Pce_node):
			#check if there is existed child of parent node
			node.previous_node = node.parent_node.Pce_node
			node.parent_node.Pce_node.next_node = node
			node.parent_node.Pce_node = node
		else:          
			node.parent_node.Pcs_node = node
			node.parent_node.Pce_node = node
			node.previous_node = None
			node.next_node = None


class block():

	def __init__(self, record, c=100, u=0.2):
		# record is a list of[oid, start_time, end_time]
		# add requisite here: there must be a record while creating 
		# new block
		# use a unique random id to represent the block
		self.id = uuid1()
		self.time_interval = [record[1], '*']
		self.capacity = c
		self.u = u
		self.record_list = [record]
		# Used memory
		self.usage = len(self.record_list)
		# an integer to show the number of alive entries
		self.alive_record = len(self.record_list)
		# a flag to show if the block is full or not
		self.isfull = False
		# another flag to show if the block is underflow or not
		# underflow also shows if the block is useful or not
		self.isunderflow = False
			
	def insert(self, record):
		self.record_list.append(record)
		self.usage += 1
		self.alive_record += 1
		if(self.usage == self.capacity):
			self.isfull = True

	def delete(self, oid, end_time):
		for record in self.record_list:
			if(oid == record[0]):
				record[2] = end_time
				self.alive_record -= 1
				if(self.isfull and self.alive_record<self.u*self.capacity):
					self.isunderflow = True
				return
		# if no record is founed
		print('cannot find the record')

	# for the copy procedure, we need to get all the entries first
	def alives_inblock(self):
		alive = []
		for record in self.record_list:
			if(record[2] == '*'):
				alive.append(record)
		return alive

	def delete_block(self, end_time):
		if(self.isunderflow):
			self.time_interval[1] = end_time
			for entry in self.record_list:
				if(entry[2] == '*'):
					entry[2] = end_time



class Snapshot():

	# record format is [oid, start_time, end_time]
	def __init__(self, r): # start by inserting an record
		self.blocks = Linked_list()
		# insert a new block and set it as acceptor
		new_block = block(record=r)
		self.blocks.insert(Node(blk=new_block))
		self.acceptor = self.blocks.last_node.block
		# entry in AT array is in format (t, pointer_to_node_in_linkedlist)
		self.AT = [(r[1], self.blocks.last_node)]
		# record all alive entries, formart is {oid, pointer_to_node_in_linkedlist}
		self.alives_entries = {r[0]:self.blocks.last_node}

	def insert(self, r):
		if(self.acceptor.isfull):
			# create new block with the new record
			new_block = block(record=r)
			self.blocks.insert(Node(blk=new_block))
			# set the acceptor block to the newly inserted block
			self.acceptor = self.blocks.last_node.block 
			# append the (time, block) to the AT array
			self.AT.append((r[1], self.blocks.last_node))
			# self.acceptor.insert(r)
		else:
			self.acceptor.insert(r)
		self.alives_entries[r[0]] = self.blocks.last_node

	def delete(self, oid, end_time):
		# use hash to find the node first and then delete
		node = self.alives_entries.pop(oid) # pop the entry in hash map
		node.block.delete(oid, end_time)
		if(node.block.isunderflow):
			# copy the alive entires to the new block
			# new node creation is automatic in the insert process, as only full
			# block will be in underflow condition and insert process will create
			# new acceptor block if block is full
			self.copy(node.block.alives_inblock(), end_time)
			# change the end_time of the alive entries in block to current time
			node.block.delete_block(end_time)
			# delete the node in the doubly linked list
			self.blocks.delete(node)

	def copy(self, records, time):
		for record in records:
			new_record = [record[0], time, '*']
			# no need to create new node
			self.insert(new_record)

	# timeslice query interface, get the records alive in some time instant
	def tsquery(self, time):
		cur_node = None
		# get the acceptor block at the required time by the AT array
		# want the largest t <= time
		for i in range(len(self.AT)):
			if(self.AT[i][0]<=time and self.AT[i+1][0]>time):
				cur_node = self.AT[i][1]
				break
		# if didn't find, consider two situations:
		else:
			if(self.AT[0][0]>time):
				return []
			else:
				cur_node = self.AT[-1][1]
		# start visitation. The visitation pattern is this node-->up node, left node,
		# children in parallel and left arrow keeps checking left and down
		# up keeps checking up, left, no need to check right
		# Use a list to record the checked nodes
		checked = []
		result = Snapshot.check_node(cur_node, time, checked)
		# Now, go up, left, down,.. from the current node.
		if(cur_node.parent_node):
			result += Snapshot.gocheck_up(cur_node.parent_node, time, checked)
		if(cur_node.previous_node):
			result += Snapshot.gocheck_left(cur_node.previous_node, time, checked)
		# There should be no need to check the right sibling
		# if(cur_node.next_node):
		# 	result += Snapshot.gocheck_right(cur_node.next_node, time, checked)	
		if(cur_node.Pce_node):
			result += Snapshot.gocheck_down(cur_node.Pce_node, time, checked)			
		# Remove duplicates and return result as a set
		result = set(result)
		return result

	@classmethod
	def check_node(cls, node, t, checked=None):
		result = []
		t_s, t_e = node.block.time_interval
		if(t_e != '*' and (t_s>t or t_e <t)):
			return result
		for re in node.block.record_list:
			if(re[2] == '*'):
				if(re[1]<=t):
					result.append(re[0])
			else:
				if(re[1]<=t and re[2]>=t):
					result.append(re[0])
		# record the checked node, so won't be double checked
		checked.append(node.block.id)
		return result

	@classmethod
	def gocheck_up(cls, node, t, checked):
		result = []
		result += cls.check_node(node, t, checked)
		# if there is parent node, keep going up and checking
		if(node.parent_node and node.parent_node.block.id not in checked):
			# No need to check interval, as upper node is what we always need
			result += cls.gocheck_up(node.parent_node, t, checked)
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_s, t_e = node.previous_node.block.time_interval
			if(t_s<=t and t_e>=t):
				result += cls.gocheck_left(node.previous_node, t, checked)
		return result

	@classmethod
	def gocheck_down(cls, node, t, checked):
		result = []
		result += cls.check_node(node, t, checked)
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_s, t_e = node.previous_node.block.time_interval
			if(t_s<=t and t_e>=t):
				result += cls.gocheck_left(node.previous_node, t, checked)
		if(node.Pce_node and node.Pce_node.block.id not in checked):
			t_s, t_e = node.Pce_node.block.time_interval
			if(t_s<=t and t_e>=t):
				result += cls.gocheck_down(node.Pce_node, t, checked)
		return result

	@classmethod
	def gocheck_left(cls, node, t, checked):
		result = []
		result += cls.check_node(node, t, checked)
		# check the left sibling node:
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_s, t_e = node.previous_node.block.time_interval
			if(t_s<=t and t_e>=t):
				result += cls.gocheck_left(node.previous_node, t, checked)
		if(node.Pce_node and node.Pce_node.block.id not in checked):
			t_s, t_e = node.Pce_node.block.time_interval
			if(t_s<=t and t_e>=t):
				result += cls.gocheck_down(node.Pce_node, t, checked)
		return result

	# There is always no need to check right. As while checking the children
	# The checking process is always start from right most, in the process of 
	# up checking, it is fundamentally no suitable records in the right sibling
	# @classmethod
	# def gocheck_right(cls, node, t, checked):
	# 	result = []
	# 	result += cls.check_node(node, t, checked)
	# 	# check the left sibling node:
	# 	if(node.next_node and node.next_node.block.id not in checked):
	# 		t_s, t_e = node.next_node.time_interval
	# 		if(t_s<=t and t_e>=t):
	# 			result += cls.gocheck_right(node.next_node, t, checked)
	# 	if(node.Pce_node and node.Pce_node.block.id not in checked):
	# 		t_s, t_e = node.Pce_node.time_interval
	# 		if(t_s<=t and t_e>=t):
	# 			result += cls.gocheck_down(node.Pce_node, t, checked)
	# 	return result

	# range query interface, get the records between time period
	# t_min must <= t_max
	def trquery(self, t_min, t_max):
		# checking process starts from the t_max to t_min, ease the process
		# get the acceptor block of t_max from AT array
		max_node = None
		for i in range(len(self.AT)):
			if(self.AT[i][0]<=t_max and self.AT[i+1][0]>t_max):
				max_node = self.AT[i][1]
				break
		# if didn't find, consider two situations:
		else:
			if(self.AT[0][0]>t_max):
				return []
			else:
				max_node = self.AT[-1][1]

		# first check the acceptor block
		checked = []
		result = Snapshot.rcheck_node(max_node, t_min, t_max, checked)
		if(max_node.parent_node):
			result += Snapshot.rcheck_up(max_node, t_min, t_max, checked)
		if(max_node.previous_node):
			result += Snapshot.rcheck_left(max_node, t_min, t_max, checked)
		if(max_node.Pce_node):
			result += Snapshot.rcheck_down(max_node, t_min, t_max, checked)
		result = set(result)
		return result

	@classmethod
	def rcheck_node(cls, node, t1, t2, checked):
		t_interval = node.block.time_interval
		result = []
		if(cls.overlap(t1, t2, t_interval)):
			for re in node.block.record_list:
				if(cls.overlap(t1, t2,[re[1], re[2]])):
					result.append(re[0])
		checked.append(node.block.id)
		return result

	@classmethod
	def rcheck_up(cls, node, t1, t2, checked):
		result = []
		result += cls.rcheck_node(node, t1, t2, checked)
		# if there is parent node, keep going up and checking
		if(node.parent_node and node.parent_node.block.id not in checked):
			# No need to check interval, as upper node is what we always need
			result += cls.rcheck_up(node.parent_node, t1, t2, checked)
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_interval = node.previous_node.block.time_interval
			if(cls.overlap(t1, t2, t_interval)):
				result += cls.rcheck_left(node.previous_node, t1, t2, checked)
		return result

	classmethod
	def rcheck_left(cls, node, t1, t2, checked):
		result = []
		result += cls.rcheck_node(node, t1, t2, checked)
		# check the left sibling node:
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_interval = node.previous_node.block.time_interval
			if(cls.overlap(t1, t2, t_interval)):
				result += cls.rcheck_left(node.previous_node, t1, t2, checked)
		if(node.Pce_node and node.Pce_node.block.id not in checked):
			t_interval = node.Pce_node.block.time_interval
			if(cls.overlap(t1, t2, t_interval)):
				result += cls.rcheck_down(node.Pce_node, t1, t2, checked)
		return result


	@classmethod
	def rcheck_down(cls, node, t1, t2, checked):
		result = []
		result += cls.rcheck_node(node, t1, t2, checked)
		if(node.previous_node and node.previous_node.block.id not in checked):
			t_interval = node.previous_node.block.time_interval
			if(cls.overlap(t1, t2, t_interval)):
				result += cls.rcheck_left(node.previous_node, t1, t2, checked)
		if(node.Pce_node and node.Pce_node.block.id not in checked):
			t_interval = node.Pce_node.block.time_interval
			if(cls.overlap(t1, t2, t_interval)):
				result += cls.rcheck_down(node.Pce_node, t1, t2, checked)
		return result
	
	@classmethod
	def overlap(cls, t1, t2, t_interval):
		if(t_interval[1]=='*'):
			if(t_interval[0]<=t2):
				return True
			else:
				return False
		else:
			if(t1>=t_interval[0] and t1<=t_interval[1]):
				return True
			elif(t2>=t_interval[0] and t2<=t_interval[1]):
				return True
			elif(t1<=t_interval[0] and t2>=t_interval[1]):
				return True
			elif(t1>=t_interval[0] and t2<=t_interval[1]):
				return True
			return False

	# get the records with particular object id
	# def keyq(self, oid):
	# 	pass

	