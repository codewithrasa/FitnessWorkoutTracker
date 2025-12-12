# data_structures,py

# Binary Search Tree (stores exercises alphabetically by name)
class BSTNode:
    def __init__(self, exercise):
        self.exercise = exercise      # store exercise object
        self.left = None              
        self.right = None             

class ExerciseBST:
    def __init__(self):
        self.root = None              

    def insert(self, exercise):
        
        if not self.root:
            self.root = BSTNode(exercise)
            return True
        return self._insert(self.root, exercise)

    def _insert(self, node, exercise):
        # Avoid duplicates based on name
        if exercise.name.lower() == node.exercise.name.lower():
            return False

        # Go left alphabetically
        if exercise.name.lower() < node.exercise.name.lower():
            if node.left:
                return self._insert(node.left, exercise)
            node.left = BSTNode(exercise)
            return True
        else:
            # Go right alphabetically
            if node.right:
                return self._insert(node.right, exercise)
            node.right = BSTNode(exercise)
            return True

    def in_order(self):
        # Return all exercises sorted by name
        items = []
        self._in_order(self.root, items)
        return items

    def _in_order(self, node, items):
        # Classic in-order traversal
        if node:
            self._in_order(node.left, items)
            items.append(node.exercise)
            self._in_order(node.right, items)

    def find_by_name(self, name):
        # Search for an exercise by name
        return self._find(self.root, name.lower()) if name else None

    def _find(self, node, name):
        if not node:
            return None
        if name == node.exercise.name.lower():
            return node.exercise
        if name < node.exercise.name.lower():
            return self._find(node.left, name)
        return self._find(node.right, name)

    def delete(self, name):
        # Delete a node and return the removed exercise
        self.root, deleted = self._delete(self.root, name.lower())
        return deleted

    def _delete(self, node, name):
        # Standard BST delete logic
        if not node:
            return node, None

        # Traverse to find node
        if name < node.exercise.name.lower():
            node.left, deleted = self._delete(node.left, name)
            return node, deleted

        if name > node.exercise.name.lower():
            node.right, deleted = self._delete(node.right, name)
            return node, deleted

        # Found the node
        deleted = node.exercise

        # Case 1: no left child
        if not node.left:
            return node.right, deleted

        # Case 2: no right child
        if not node.right:
            return node.left, deleted

        # Case 3: two children → replace with inorder successor
        succ_parent = node
        succ = node.right
        while succ.left:
            succ_parent = succ
            succ = succ.left

        node.exercise = succ.exercise

        # Remove successor
        if succ_parent.left == succ:
            succ_parent.left = succ.right
        else:
            succ_parent.right = succ.right

        return node, deleted


# Simple linked-list queue (for daily workout order)
class QueueNode:
    def __init__(self, exercise):
        self.exercise = exercise
        self.next = None

class ExerciseQueue:
    def __init__(self):
        self.front = self.rear = None
        self._size = 0                 # keep track of size manually

    def enqueue(self, exercise):
        # Add to end of queue
        node = QueueNode(exercise)
        if not self.rear:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self._size += 1

    def dequeue(self):
        # Remove from front
        if not self.front:
            return None
        ex = self.front.exercise
        self.front = self.front.next
        if not self.front:
            self.rear = None
        self._size -= 1
        return ex

    def peek(self):
        # Look at first item without removing it
        return self.front.exercise if self.front else None

    def is_empty(self):
        return self.front is None

    def size(self):
        return self._size

    def clear(self):
        # Reset queue
        self.front = self.rear = None
        self._size = 0

    def to_list(self):
        # Convert queue to Python list for display
        cur = self.front
        out = []
        while cur:
            out.append(cur.exercise)
            cur = cur.next
        return out
