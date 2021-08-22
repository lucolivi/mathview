# this is a pretty basic tree implementation with some nice stuff for parsing.
import tree_parser

import networkx as nx

class Tree:
    _tree_num = 0
    def __init__(self,value=None, leaves = [], parent = None, nested_list=None):
        self.value = value
        self.leaves = list()
        self._parents = list()

        self._tree_num = Tree._tree_num
        Tree._tree_num += 1

        for leaf in leaves:
            self.add_leaf(leaf)
        
        

        if not nested_list is None:
            self.value = nested_list[0]
            #self.leaves = [Tree(nested_list=sublist) for sublist in nested_list[1:]] replaced due to the parents ref need
            for sublist in nested_list[1:]:
                self.add_leaf(Tree(nested_list=sublist))

    def add_leaf(self,leaf):
        self.leaves.append(leaf)
        leaf.parent = self
        leaf._parents.append(self)

    def degree(self):
        return len(self.leaves)

    def size(self):
        # THIS IS INEFFICIENT. I SHOULD STORE THIS
        return 1 + sum([l.size() for l in self.leaves])

    def height(self):
        if len(self.leaves)==0: return 0
        return 1 + max([l.height() for l in self.leaves])


    def total_append(self):
        out = []
        for l in self.leaves:
            out+=l.total_append()
        out+=[self.value]
        return out

    def total_prepend(self):
        out = []
        for l in self.leaves:
            out+=l.total_prepend()
        return out

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '<Tree: '+self.stringify()+'>'

    def stringify(self):
        if self.value is None: return "???"  # for the beam search
        out = self.value+"("
        dontaddcomma = True
        for l in self.leaves:
            if not dontaddcomma: out+=","
            else: dontaddcomma = False
            out+=l.stringify()
        out+=")"
        return out

    def lists(self):
        return [self.value, [l.lists() for l in self.leaves]]

    # overload the equality operator and the not equality operator
    def __eq__(self,target):
        return self.value==target.value and len(self.leaves)==len(target.leaves) and not any(self.leaves[i] != target.leaves[i] for i in range(len(self.leaves)))


    def __ne__(self,target):
        return not self.__eq__(target)

    # fit attempts to make self appear like tree by replacing variables in tree
    # with subtrees.  It returns a substitution dictionary if the replacement is valid
    # and otherwise returns None
    def fit(self,tree,variables):
        if tree.value in variables:
            # return a replacement
            return {tree.value:self}

        if not self.value==tree.value: return None              #values must be the same
        #if not len(self.leaves)==len(tree.leaves): return None

        # otherwise, compare the leaves
        out = {}
        for i in range(len(self.leaves)):
            next_dict = self.leaves[i].fit(tree.leaves[i],variables)
            if next_dict == None:
                return None
            for var in next_dict:
                if var in out:
                    if not out[var]==next_dict[var]:
                        return None
                else:
                    out[var]=next_dict[var]
        return out

    # overloads the in operator
    def __contains__(self, key):
        return self.value == key or any(leaf.__contains__(key) for leaf in self.leaves)


    # returns a deep copy of the current tree.
    #Need to verify already copied items to avoid recursive loops
    def copy(self, _copy_dict=None, _already_copied=None, _copy_parent=None, _copy_child=None):

        if _copy_dict == None:
            _copy_dict = dict()

        if len(self.leaves) == 0:
            return self

        if self._tree_num in _copy_dict and len(self.leaves) > 0:
            #print id(_copy_dict), id(self), len(self.leaves)
            #print ("")
            return _copy_dict[self._tree_num]      

        out = Tree(value=self.value)
        _copy_dict[self._tree_num] = out

        #[leaf.copy(_copy_dict=_copy_dict) for leaf in self.leaves]
        for leaf in self.leaves:
            out.leaves.append(leaf.copy(_copy_dict=None))
            #out.add_leaf(leaf.copy())
            #if id(leaf) in _copy_dict:
            #    out.leaves.append(_copy_dict[id(leaf)])
            #else:
                #out.leaves.append(leaf.copy(_copy_dict=_copy_dict))

        #out._parents = [p.copy(_copy_dict=_copy_dict) for p in self._parents]

        #out.leaves = [leaf.copy(_copy_parent=self) for leaf in self.leaves]
        #out._parents = [p.copy() for p in self._parents if _copy_parent and id(_copy_parent) != id(p)]
        #out.leaves = [leaf.copy(_already_copied, _copy_parent=out) for leaf in self.leaves if _copy_child != None and id(_copy_child) != id(out)]
        #out._parents = [p.copy(_copy_child=self) for p in self._parents if _copy_parent != None and id(_copy_parent) != id(out)]

        if self.stringify() != out.stringify():
            print(self.stringify())
            print(out.stringify())
            raise Exception("Different data")

        return out

    # modifies the current tree, replacing all the nodes with values in replacement_dictionary
    # with a copy of the subtree indicated by replacement_dictionary
    def replace(self,replacement_dictionary):
        if self.value in replacement_dictionary:
            self = replacement_dictionary[self.value].copy()
        else:
            for i in range(len(self.leaves)):
                self.leaves[i] = self.leaves[i].replace(replacement_dictionary)
                #l = self.leaves[i]
                #if l.value in replacement_dictionary:
                    #new_rep_tree = replacement_dictionary[l.value].copy()
                    #self.leaves[i].value = new_rep_tree.value
                    #self.leaves[i].leaves = new_rep_tree.leaves #Since here we are replacing the node, we need to get hid of all its previous children
                    #self.leaves[i]._parents.extend(new_rep_tree._parents) #Here we preserve the previous parents but add the new 

                    #self.leaves[i] = new_rep_tree #previous form

                #else: l.replace(replacement_dictionary)
        return self

    def replace_values(self,replacement_dictionary):
        if self.value in replacement_dictionary:
            self.value = replacement_dictionary[self.value]

        for l in self.leaves:
            l.replace_values(replacement_dictionary)
        return self

    def set(self):
        # out = set([self.value])
        # for l in self.leaves:
        #     out.union(l.set())
        # return out
        return set(self.list())

    # given a list [0,1,2], returns the value of the node at that position
    def value_at_position(self,position):
        current = self
        for i in position:
            current=current.leaves[i]
        return current.value

    def set_value_at_position(self, position, value):
        current = self
        for i in position:
            current=current.leaves[i]
        current.value = value

    def node_at_position(self,position):
        current = self
        for i in position:
            current=current.leaves[i]
        return current

    def add_node_at_position(self, position, node):
        current = self
        for i in position:
            current=current.leaves[i]
        current.leaves.append(node)

    def get_first_none_position(self):
        if self.value is None: return []
        for index in range(len(self.leaves)):
            l = self.leaves[index]
            out = l.get_first_none_position()
            if not out is None: return [index]+out
        return None


    # given a list as above, returns the next node in a breath-first search of the tree
    def next_breadth_position(self,position):
        pos_list = self.breadth_first_position_list()
        for i in range(len(pos_list)):
            if pos_list[i]==position:
                if i+1 == len(pos_list): return None
                else: return pos_list[i+1]
        assert False # position not in the breadth_first_position_list


    def breadth_first_position_list(self):
        # list all the positions in a breadth-first manner.
        # the trees we're dealing with are all small --- like 50 nodes or so,
        # so this is probably fine

        node_list = [self]
        position_list = [()]

        i = 0
        while i<len(node_list):
            node = node_list[i]
            position = position_list[i]

            node_list += node.leaves
            position_list += [position+(n,) for n in range(len(node.leaves))]

            i+=1

        return position_list

    def list(self):
        # gets the values in a left-traversal
        out = [self.value]
        for l in self.leaves:
            out += l.list()
        return out

    def right_list(self):
        # gets the values in a left-traversal
        out = []
        for l in self.leaves:
            out += l.right_list()
        out.append(self.value)
        return out

    def annotate(self, current_depth = 0, current_position = 0, parent=None):
        # adds depth and left-traversal position to the tree
        # now also adds parentage information
        self.depth = current_depth
        self.position = current_position
        current_position+=1
        self.parent = parent

        for l in self.leaves:
            current_position = l.annotate(current_depth=current_depth+1, current_position=current_position, parent=self)
        return current_position
        
    def get_equation(self, lm, context):
        string = tree_parser.tree_to_string(self, lm.database, context)
        string =  ' '.join(string)
        #string = string.replace(" ", "") # so that the display fits on one line
        return string


    def eval(self, database, context):
        return " ".join(tree_parser.tree_to_string(self, database, context))