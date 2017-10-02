import TreeParse

def UPGMA( filename, fetch_list=None ):
    """ Create a full UPGMA tree from a file."""
    counter = 0
    ids, matrix = Read_Matrix_File(filename)    #Read file
    if fetch_list != None:
        ids, matrix = Filter_By_Fetch_list(ids, matrix, fetch_list)
    subtrees = []
    for leaf in ids:
        l = TreeParse.Data(leaf,0,counter)    #Create leaves out of all the gis
        counter = counter + 1
        ap_node = TreeParse.Node()
        ap_node.leaf(l)
        subtrees.append(ap_node)
    while(len(matrix) > 1):
        #Find Smallest Position
        stays, goes = Find_Smallest_Position(matrix)
        value = matrix[stays][goes]/2
        #print "stays",stays, "goes",goes, "value",value
        #Contract rows and columns
        Conjoin(matrix,stays,goes)
        #Join nodes
        subtrees[stays].data.length = value - subtrees[stays].data.length
        subtrees[goes].data.length = value - subtrees[goes].data.length
        d = TreeParse.Data('',value,counter)
        counter = counter + 1
        ap_node = TreeParse.Node()
        ap_node.internal(d,[subtrees[stays],subtrees[goes]])
        subtrees.pop(goes)
        subtrees[stays] = ap_node
    subtrees[0].data.length = 0
    tree_root = TreeParse.Tree(subtrees[0])
    return tree_root

def UPGMAFiltered( filename, fetch_list ):
    UPGMA(filename, fetch_list)
    
def Filter_By_Fetch_List( ids, matrix, fetch_list):
    """ Create a UPGMA tree using only the gi's in the fetch_list """
    counter = 0
    removal_list = []
    #remove non matching rows and columns
    for i in range( len( ids ) ):   #Make a list of indices to remove
        if not ids[i] in fetch_list:
            removal_list.append(i)
    popped = 0
    for i in removal_list:  #Remove columns
        for j in matrix:
            j.pop(i-popped)
        popped = popped+1
    popped = 0
    for i in removal_list:  
        matrix.pop(i-popped) #Remove rows    
        ids.pop(i-popped)   #Remove ids
        popped = popped+1
    return ids, matrix

def Read_Matrix_File( filename ):
    """ Read in a protein distance matrix file and create a matrix of its distances.
        Return the gi list and the matrix of distances. The gi list corresponds to 
        the distance matrix rows.
    """
    try:
        reader = open(filename)
    except IOError:
        print "Looking for a .dst file at %s that doesn't seem to exist"%(filename)
        return -1
    file_header = reader.readline() #read in the amount line
    file_header = file_header.strip()
    expected = int(file_header)
    line = reader.readline()    #read in the first line
    gi_list = []                # a list of the gi's
    matrix = []                 #the matrix
    while( line != '' ):
        id_header, line = line.split(' ',1)     #grab the gi
        lst = id_header.split('|',2)
        if len(lst) == 3:
            gi,id,db = lst[0],lst[1],lst[2]
        elif len(lst) == 1:
            id = lst[0]
        gi_list.append(id)
        line = line.strip().replace("  "," ")
        listing = line.split(' ')   #a list of values

        while(len(listing) < expected ): #If one line did not split into the expected amount
        #read other lines until filled    
            line = reader.readline()
            line = line.strip().replace("  "," ")
            listing = listing + line.split(' ') #append values to listing
        matrix.append(listing)  #append listing to the matrix
        line = reader.readline()
    reader.close()
    #Make triangular    
    for i in range( expected ):
        for j in range(i):
            matrix[i][j] = 0.0
        for j in range( expected - i ):
            to_add = float(matrix[i][i+j])
            matrix[i][i+j] = to_add
    return gi_list,matrix

def Find_Smallest_Position(matrix):
    """ Given a two dimensional matrix, find the smallest position
        return it as i,j.  Lowest position = matrix[i][j]
    """
    out_i = 0
    out_j = 1
    total = matrix[out_i][out_j]
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if( i<j  and matrix[i][j] < total ):
                out_i = i
                out_j = j
                total = matrix[i][j]
    return out_i,out_j

def Conjoin( matrix, stays, goes ):
    """ Given a matrix and a row that stays and a row that goes
        Condense the matrix
    """
    #Each item in the matrix will have one spot that stays and one spot that goes.  
    # Take the average of item[stays] and item[goes] and store it in item stays
    for i in range(len(matrix)):
        #For each item in the matrix
        if( i == stays or i == goes ):
            continue
        #Precondition, stays != goes, goes != i, stays != i
        stay_spot = [stays,i]
        stay_spot.sort()
        #At this point, stay_spot is a tuple representing the spot to stay        
        goes_spot = [goes,i]
        goes_spot.sort()
        #At this point, goes_spot is a tuple representing the spot to go
        #Since dealing with an upper triangular matrix, the sort accounts for this

        #Create and store the average        
        first = matrix[stay_spot[0]][stay_spot[1]]
        second = matrix[goes_spot[0]][goes_spot[1]]
        matrix[stay_spot[0]][stay_spot[1]] = (first+second)/2.0
    for i in matrix:    #Remove the goes-th column
        i.pop(goes)
    matrix.pop(goes)    #Remove the goes-th row
    return matrix

