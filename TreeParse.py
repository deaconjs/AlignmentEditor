class Data:
    #Class Data is designed to hold an object in a tree
    #   name: the name of the node, generally more for the leaves and root
    #   length: the length of the branch from its top node
    def __init__( self, name, length, id = 0 ):
        self.name = name
        self.length = length
        self.id = id
    def __str__( self ):
        return "["+self.name+", "+ str( self.length ) + "]"
    def Name( self ):
        return self.name
    def Length( self ):
        return self.length
    def Match( self, to_match ):
        return to_match == self.name
    
class Node:
    #Class Node has
    #   data: holding the node's current data
    #   sub: a list of the node's subordinate nodes
    def __init__( self ):
        self.data = Data("","0")
        self.sub = []
        self.parent = 0
    def leaf( self, data ):
        self.data = data
        self.sub = []
    def internal( self, data, sub ):
        self.sub = sub
        for item in self.sub:
            item.parent = self
        self.data = data
    def children( self ):
        return len( self.sub )
    def __str__( self ):
        total = ""
        total = self.data.__str__()
        
        if len( self.sub ) > 0:
            total = total + "->("
            for item in self.sub:
                total = total + item.__str__() + ","
            total = total[:len(total)-1] + ")"
        return total
    #Search current node and subordinate nodes for the node with data.name equal to name
    def Search_For_Name( self, name ):
        for item in self.sub:
            if item.data.name == name:
                return item
            else:
                to_return = item.Search_For_Name( name )
                if( to_return != 0 ):
                    return to_return
        return 0
    #Find the longest branch distance below this node
    def Longest_Branch( self ):
        current_x = self.data.Length()
        middle_x = 0
        for each_item in self.sub:
            newest_x = each_item.Longest_Branch()
            if middle_x < newest_x:
                middle_x = newest_x
        returning = current_x + middle_x
        return returning
    #Return a list of the gi's found subordinate to this node
    def GI_List( self ):
        gi_list = []
        if(len(self.sub)>0):
            for item in self.sub:
                if item.data.name != '':
                    gi_list.append(item.data.name)
                else:
                    gi_list = gi_list + item.GI_List()
        else:
            gi_list.append( self.data.name )
        return gi_list

#Wrapper class to hold a node
class Tree:
    def __init__(self, node):
        self.node = node
    #Find the longest branch in the tree.  If root_node is not 0, it is the star point
    def Longest_Branch(self, root_node=0):
        if( root_node == 0 ):
            root_node = self.node
        current_x = root_node.data.Length()
        middle_x = 0
        for each_item in root_node.sub:
            newest_x = self.Longest_Branch(each_item)
            if middle_x < newest_x:
                middle_x = newest_x
        returning = current_x + middle_x
        return returning
    #Search for a node given a name
    def Get_Node_By_Name( self, name ):
        if self.node.data.name == name:
            return root
        else:
            return self.node.Search_For_Name( name )
    

