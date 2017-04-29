import unittest
# import sys
from snapshot import Node, Linked_list, block, Snapshot

class SnapshotTest(unittest.TestCase):

	def setUp(self):
		pass

	def test_node_init(self):
		node = Node()
		self.assertIsInstance(node, Node)

	def test_linked_list_init(self):
		l = Linked_list()
		self.assertIsInstance(l, Linked_list)

	def test_linked_insert(self):
		node = Node(blk = 'haha')
		l = Linked_list()
		l.insert(node)
		self.assertEqual(l.last_node, node)
		self.assertEqual(l.last_node.block, 'haha')

	def test_linked_delete(self):
		node = Node(blk='hmm')
		l = Linked_list()
		l.insert(node)
		node1 = Node(blk='haha')
		l.insert(node1)
		l.delete(node)
		self.assertEqual(l.SP.next_node, l.last_node)
		self.assertEqual(l.SP.next_node.block, 'haha')
		self.assertEqual(l.SP.Pce_node, l.SP.Pcs_node)
		self.assertEqual(l.SP.Pce_node.block, 'hmm')
		self.assertEqual(node.parent_node, l.SP)

	def test_block_init(self):
		#initialize with record [id, start_time, end_time]
		record = ['idhere', 1, '*']
		b = block(record)
		self.assertIsInstance(b, block)

	def test_block_insert(self):
		record = ['idhere', 1, '*']
		b = block(record)
		record = ['another id', 2, '*']
		b.insert(record)
		self.assertEqual(b.usage, 2)
		self.assertEqual(b.alive_record, 2)
		self.assertFalse(b.isfull)

	def test_block_delete(self):
		record = ['idhere', 1, '*']
		b = block(record)
		record = ['another id', 2, '*']
		b.insert(record)
		b.delete('idhere', 5)
		self.assertEqual(b.record_list[0][2],  5)
		self.assertEqual(b.usage, 2)
		self.assertEqual(b.alive_record, 1)
		self.assertFalse(b.isunderflow)
		self.assertFalse(b.isfull)

	def test_block_delete_block(self):
		record = ['idhere', 1, '*']
		b = block(record)
		record = ['another id', 2, '*']
		b.insert(record)
		b.isunderflow=True
		b.delete_block(10)
		self.assertEqual(b.time_interval, [1,10])
		self.assertEqual(b.record_list[0][2], 10)
		self.assertEqual(b.record_list[1][2], 10)

	def test_snapshot_init(self):
		record = ['idhere', 1, '*']
		s = Snapshot(record)
		self.assertIsInstance(s, Snapshot)
		self.assertIsInstance(s.blocks, Linked_list)
		self.assertIsInstance(s.blocks.last_node.block, block)
		self.assertIsInstance(s.acceptor, block)

	def test_snapshot_insert(self):
		record = ['idhere', 1, '*']
		s = Snapshot(record)
		record = ['another id', 2, '*']
		s.insert(record)
		self.assertEqual(s.acceptor.record_list[1], record)
		self.assertEqual(s.blocks.last_node, s.alives_entries[record[0]])

	def test_snapshot_delete(self):
		record = ['idhere', 1, '*']
		s = Snapshot(record, cap=2, ut=0.6)
		record = ['another id', 2, '*']
		s.insert(record)
		s.delete('another id', 5)
		self.assertEqual(s.blocks.last_node.previous_node.Pce_node.block.record_list[1][2],5)
		self.assertEqual(s.blocks.last_node.previous_node.Pce_node.block.time_interval,[1,5])
		self.assertTrue(s.blocks.last_node.previous_node.Pce_node.block.isfull)
		self.assertTrue(s.blocks.last_node.previous_node.Pce_node.block.isunderflow)
		self.assertEqual(s.blocks.last_node.block.usage, 1)
		self.assertFalse('another id' in s.alives_entries)
		
	def test_snapshot_query(self):
		record = ['idhere', 1, '*']
		s = Snapshot(record, cap=2, ut=0.6)
		record = ['another id', 2, '*']
		s.insert(record)
		record = ['onemore id', 2, '*']
		s.insert(record)
		self.assertEqual(s.tsquery(3),{'SP','idhere', 'another id', 'onemore id'})
		self.assertEqual(s.tsquery(1), {'SP', 'idhere'})
		s.delete('another id', 5)
		self.assertEqual(s.tsquery(6), {'idhere', 'onemore id', 'SP'})
		self.assertEqual(s.trquery(1,3), s.trquery(1,2))
		self.assertEqual(s.trquery(1,3), s.tsquery(1)|s.tsquery(2))

if __name__=='__main__':
	unittest.main()
