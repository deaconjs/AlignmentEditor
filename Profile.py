import UPGMA
import TreeParse

#generate the next color given a number
def Generate_Next_Color( counter ):
    colors = ["blue","green","yellow","red","orange","brown","gray","purple"]
    if( counter < len( colors ) ):
        return colors[ counter ]
    color = '#'
    bin_list = [ 2, 16, 4, 32, 8, 64 ]
    for item in bin_list:
        if counter%item == 0:
            color = color + "C"
        else:
            color = color + "F"
    return color

#Class for encapsulating items of the search list of a profile
class Term:
    def __init__( self, term, type ):
        self.term = term    #string
        self.type = type    #type can be "Include","Exclude"
    def Get_Type( self ):
        return self.type
    #Toggle the type between Include and Exclude
    def Toggle_Type( self ):
        if( self.type == "Include" ):
            self.type = "Exclude"
        elif( self.type =="Exclude" ):
            self.type = "Include"
    #Create a string for displaying
    def Display_( self ):
        to_display = "("
        if( self.type == "Include" ):
            to_display = to_display + "+"
        elif( self.type == "Exclude" ):
            to_display = to_display + "-"
        to_display = to_display + ")" + self.term
        return to_display
        
#class that encapsulates a profile of a tree
class Profile:
    def __init__( self, name, counter = 0 ):
        self.name = name    #name
        self.color = Generate_Next_Color( counter )   #highlight color
        self.gi_list = []   #list of gi's that references UPGMA file
        self.reason_list = []   #list of reasons why GI's were added
        self.tree = 0       #the tree
        self.term_list = [] #list of search terms
        self.changed = 0
    #Remove all GI's, make way for a reapply of the search terms
    def Clear_GIs( self ):
        self.gi_list = [ ]
        self.reason_list = [ ]
    #Add each GI in a list
    def Add_GI_List( self, gi_list, reason = ""):
        for item in gi_list:
            self.Add_GI( item, reason )
    #Remove eacch GI in a list
    def Remove_GI_List( self, gi_list ):
        for item in gi_list:
            self.Remove_GI( item )
    #Get the name
    def Get_Name( self ):
        return self.name
    def Has_Term( self, term ):
        for i in self.term_list:
            if( i.term == term ):
                return 1
        return 0
    #Add a single GI
    def Add_GI( self, gi, reason = "" ):
        if not gi in self.gi_list:
            self.gi_list.append( gi )
            self.reason_list.append(reason)
            self.changed = 1
        else:
            index = self.gi_list.index( gi )
            self.reason_list[ index ] = reason
        return
    #Get the reason a GI is in the list
    def Get_GI_Reason( self, gi ):
        if gi in self.gi_list:
            index = self.gi_list.index( gi )
            return self.reason_list[ index ]
        else:
            return 0
    #Remove a single GI
    def Remove_GI( self, gi ):
        if gi in self.gi_list:
            index = self.gi_list.index( gi )
            self.gi_list.remove( gi )
            self.reason_list.pop( index )
            self.changed = 1
    #Make the corresponding protein distance tree
    def Make_Tree( self, file ):
        if( len( self.gi_list ) > 0 ):
            self.tree = UPGMA.UPGMAFiltered( file, self.gi_list )
        else:
            self.tree = TreeParse.Tree( 0 )
        self.changed = 0
        return self.tree
    #Get the tree
    def Get_Tree( self ):
        return self.tree
    #See if the tree needs updating
    def Needs_Update( self ):
        return self.changed
    #Get the list of GI's
    def Get_GI_List( self ):
        return self.gi_list
    #Get the list of terms
    def Get_Term_List( self ):
        return self.term_list
    #Set the list of terms
    def Set_Term_List( self, term_list ):
        self.term_list = term_list
    #Set the color
    def Set_Color( self, color ):
        self.color = color
    #Get the color
    def Get_Color( self ):
        return self.color
        

    
    