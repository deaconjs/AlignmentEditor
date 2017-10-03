import GUI
import string
import re
import os
from Tkinter import *
from tkFileDialog import *
import global_functions
import sys
sys.path.append(os.getcwd())

sys.path.append('./Tools/ConservationTools')
import ConservationTools

# application imports
import RefEntry
import Profile
import Sequencer
import UPGMA

# This code basically sets up the GUI and handles profiles

class Deleted_Tuple:
    """This is a class to store a deleted node
    The algorithm for deleting a branch requires that the
    parent and grandparent be stored for type High
    if no grandparent, then store the node and its parent for type Super
    """
    def __init__(self, child, parent, original_index,type ):
        self.child = child      #the subordinate node
        self.parent = parent    #the parent node
        self.original_index = original_index    #the original index of the removed child
        self.type=type          #type can be "Sub","High"
    def Get_Parent(self):
        return self.parent
    def Get_Child(self):
        return self.child
    def Get_Original_Index(self):
        return self.original_index
    def Get_Type(self):
        return self.type
    def Set_Index(self, index ):
        self.original_index = index
    def Switch_Index( self ):
        self.original_index = ( self.original_index + 1 ) % 2

class TreeSystem(Frame):
    """ The TreeSystem: a class for manipulating the internal data
        The main components are a base tree for manipulating(self.tree),
        the leaves of the trees contain gi numbers
        The database, self.ref_table where all information is stored in a
        dictionary referenced by gi
        The display, self.display, where all the current information is drawn
    """
    def __init__( self, parent, system, type = "FILE", view_mode='viewer', chain="", molecular_viewer=None):
        """ this contains some platform specific stuff since it calls clustalw as an 
            executable mode can be 'viewer', 'editor', or None, which simply
            creates a multple sequence alignment
            type can be 'FILE', 'SEQUENCE', or None. if None, looks for .aln or .clu file
            in the system's directory. if it fails, it recreates the file from sequence. If
            'FILE', it looks for .aln or .clu, then prompts the user for a file if none are
            found. if 'SEQUENCE', it automatically recreates the .clu file from the sequence.
        """
        Frame.__init__(self, parent, borderwidth=0)
        self.parent = parent    # the parent is the container widget within which the treesystem is packed
        self.system = system
        self.chain = chain
        self.molecular_viewer = molecular_viewer
        self.editor_view = view_mode
        self.ref_table = 0          #a dictionary by GI of titles and sequences
        self.deleted_nodes = []     #a list of deleted nodes
        self.isolated_nodes = []    #a list of the previous tree display roots
        self.profile_list = []      #a list of the profiles
        self.data_display = "Sequence" #What to display as the data for a leaf node
        self.view_mode = 0          #0 root, 1 root+, 2 root with profile highlights, 3 upgma
        self.current_profile = GUI.root_profile_name #the current profile or points to the GUI.root_profile_name
        self.counter = 0            #counter for determining the color of the profile
        self.selected_node = 0      #currently selected node, 0 when none
        self.aligned_file = ""      #the file to find the sequences 
        self.distance_file = ""     #The protein distance matrix file
        self.tree = 0               #the root tree to display
        self.sequences = []
        strg = ""
        # look for .clu then .aln. if neither, make a .clu
        print "hello world %s"%(system.get_filename_by_extension("fst", chain))
        if os.path.exists(system.get_filename_by_extension("aln", chain)) and os.path.getsize(system.get_filename_by_extension("aln", chain)):
            print 'opening alignment from a .aln file'
            aln_file = system.get_filename_by_extension("aln", chain)
        elif os.path.exists(system.get_filename_by_extension("clu", chain)) and os.path.getsize(system.get_filename_by_extension("clu", chain)):
            print 'opening alignment from a .clu file'
            aln_file = system.get_filename_by_extension("clu", chain)
        elif os.path.exists(system.get_filename_by_extension("cin", chain)) and os.path.getsize(system.get_filename_by_extension("cin", chain)):
            seq = system.ProteinDict[chain].get_sequence()
            aln_file = Sequencer.Resequence_From_CIN(seq,system,chain)
        else:
            if os.path.exists(system.get_filename_by_extension("fst", chain)) and os.path.getsize(system.get_filename_by_extension("fst", chain)):
                print 'opening alignment from a .fst file, realigning'
                seq = system.ProteinDict[chain].get_sequence()
                aln_file = Sequencer.Resequence_From_FST(seq,system,chain)
            else:
                print 'no preformed files located, initialize BLAST to ClustalW.'
                seq = system.ProteinDict[chain].get_sequence()
                aln_file = Sequencer.Sequence_Through_Clustalw(seq,system,chain)
                
        self.Load_File_Internal( aln_file )

        if view_mode in ['editor', 'viewer']:
            if view_mode == 'editor':
                self.editor_view = 1
            else:
                self.editor_view = 0
            self.display = GUI.TreeWindow(self, self.editor_view)           # Create a framework for the GUI
            self.Draw(self.editor_view)                                              #Draw the Tree; start out in non-editing mode
            self.sequences = self.display.Get_Sequence_List()
            self.Do_Conservation()

    def Do_Conservation(self):
        ConservationTools.apply_sequence_alignment(self.system, self.sequences)
        ConservationTools.calculate_conservation(self.system, 'asa', 0, self.molecular_viewer)
        
    def Get_Sequences(self):
        return self.sequences

    def Load_File_Internal( self, file ):
        """Load file with error checking"""
        self.aligned_file =  file.replace('/',os.sep)     #the file to find the protein distance matrix
        af = self.aligned_file
        index, slash = af.rfind('.'), af.rfind(os.sep)
        if( index == -1 or index < slash ):
            index = len( af )
        self.distance_file = af[0:index] + ".dst"
        try:
            print 'treesystem opening %s'%(self.aligned_file)
            Sequencer.Clustalw_Protein(self.aligned_file)     #Create protein distance matrix
            self.tree = UPGMA.UPGMA(self.distance_file)       #root tree is the base tree
        except IOError:
            print "File must be a FASTA formatted file with more than one sequence"
            return
        self.Grab_Info()                                  #Create a dictionary by GI of the titles and sequences
    
    def Draw( self, editor=0):
        """draw the tree given the mode and the root. The variable view_mode controls the tree
        sent and data displays and highlights"""
        # first get rid of all widgets in self.display
        if( self.view_mode == 0 ):                          #Base Tree No Profiles
            self.Send_Tree( 0, editor)
            self.display.Pair_Handles( self.ref_table )
        elif( self.view_mode == 1 ):                        #Base Tree With Profiles
            self.Send_Tree( 0, editor)
            self.display.Pair_Handles( self.ref_table )
            #Add tick bars where gi matches profile list
            for item in self.profile_list:
                self.display.Highlight_Handles_2( item.Get_GI_List(),item.Get_Color(),self.profile_list.index(item))
        elif( self.view_mode == 2 ):                        #Profile tree alone
            t = self.current_profile.Make_Tree( self.distance_file )
            self.display.Draw_Tree( t.node, 1, editor )
            self.display.Pair_Handles( self.ref_table )
        elif(self.view_mode == 3):                          #Profile tree on base tree
            self.Send_Tree( 1, editor)
            self.display.Pair_Handles( self.ref_table )
            #highlight gi's when they match the profile list
            self.display.Highlight_Handles(self.current_profile.Get_GI_List(),self.current_profile.Get_Color())
        self.Change_Seq(self.data_display)
    
    def Send_Tree( self, menu, editor=0):
        """Send the tree to the display"""
        if( self.tree != 0 ):
            self.display.Draw_Tree( self.tree.node, menu, editor )
        else:
            self.display.Draw_Tree( 0, menu, editor )
    
    def Grab_Info( self, aligned = 1 ):
        """create in program dictionary referenced by GI's with text, sequence, and header"""
        reader = open( self.aligned_file, 'r' )
        parsed_file = {}
        #initialize dictionary with GI to titles,headers,and sequences
        l = reader.readline( )
        while( l != "" ):
            if( l[0] == '>' ):
                gi, title = self.Grab_GI_Title( l )
                parsed_file[ gi ] = RefEntry.Ref_Entry( gi )
                parsed_file[ gi ].Set_Title( title )
                parsed_file[ gi ].Set_Header( l.strip() )                
                l, total_sequence = self.Grab_Sequence( reader )
                parsed_file[ gi ].Set_Seq_Text( total_sequence )
            else:                
                l = reader.readline( )
        reader.close( )
        self.ref_table = parsed_file

    def Change_Seq( self, id ):
        """Change the state of what information is shown"""
        if( id in ["Title","Sequence","Header"] ):
            self.data_display = id
            self.display.Change_Seq(self.ref_table,id)
    
    def Set_Selected_Node( self, node ):
        """Set the currently selected node"""
        self.selected_node = node

    def Set_Tree_View_Mode(self, value):
        """Set the viewing mode of the tree"""
        if(value >= 0 and value <= 3):
            self.view_mode = value
            self.Draw()
    
    def Delete_Sub(self):
        """Delete the current node and its subordinates
        Attach the sibling node to its grandparent with distance changed in place of parent
        Append parent node to list of deleted nodes.
        """
        if self.selected_node == 0:
            return
        #find parent
        target_parent = self.selected_node.parent
        if(target_parent == 0):
            #do not delete root
            return
        #grab the index of the child in the parent's subordinate list
        index = target_parent.sub.index( self.selected_node )
        #grab the index of the brother
        brother = target_parent.sub[(index+1)%2]
        target_grandparent = target_parent.parent
        if(target_grandparent != 0):
            #replace the parent node in the grandparent's children with
            #the remaining child
            second_index = target_grandparent.sub.index( target_parent )
            #append parent to a list of deleted nodes
            self.deleted_nodes.append( Deleted_Tuple(target_parent,target_grandparent,second_index,"Sub") )
            target_grandparent.sub[second_index] = brother
            #adjust the length
            brother.data.length = brother.data.length+target_parent.data.length
            brother.parent = target_grandparent
        else:
            #There was no grandparent
            second_index = target_parent.sub.index( brother )
            dt = Deleted_Tuple( self.selected_node, self.selected_node.parent, second_index, "High" )
            self.deleted_nodes.append( dt ) 
            brother.parent = 0
            self.selected_node.parent.sub.remove(brother)
            self.tree.node = brother    #instead of attaching deleted node to grandparent
            #make the sibling node the root
        self.Draw()

    def Undelete(self):
        """Undo a delete Operation"""
        count=len(self.deleted_nodes)-1
        if(count<0):
            return  #Check for items in deleted list
        target = self.deleted_nodes[count]
        #Reverse the operation of Delete_Sub based on its type
        if(target.Get_Type()=='Sub'):
            target_grandparent = target.Get_Parent()
            target_parent = target.Get_Child()
            
            i = target.Get_Original_Index()
            brother = target_grandparent.sub[i] #identify what was the original sibling
            brother.parent = target_parent
            #adjust its length
            brother.data.length = brother.data.length - target_parent.data.length
            other_child = target_grandparent.sub.pop(i)
            #replace parent of deleted node in its original position
            target_grandparent.sub.insert( i, target_parent )
        elif(target.Get_Type()=='High'):
            #There was no grandparent
            p = target.Get_Parent()
            i = target.Get_Original_Index()
            self.tree.node.parent = p   #Replace the brother's parent
            p.sub.insert( i, self.tree.node )  #Reposition the brother in the parent
            self.tree.node = p
        self.deleted_nodes.pop(count)
        self.Draw()

    def Isolate(self):
        """The tree to display is only from the selected node down"""
        if self.selected_node == 0:
            return
        if( self.selected_node == self.tree.node ):
            return
        #Append current root
        self.isolated_nodes.append( self.tree.node )
        #switch root node
        self.tree.node = self.selected_node
        self.selected_node.parent = 0
        self.Draw()

    def Unisolate(self):
        """Undo an Isolate operation"""
        if( len( self.isolated_nodes ) == 0 ):
            return
        end = self.isolated_nodes[ len( self.isolated_nodes ) - 1 ]
        self.isolated_nodes.remove( end )
        self.tree.node.parent = end
        self.tree.node = end    #Set the root of the tree to 
        self.Draw()

    def Switch( self ):
        """Switch the child branches of the selected node"""
        if self.selected_node == 0:
            return
        if self.selected_node.children() == 2:
            #Swap children
            temp = self.selected_node.sub[ 0 ]
            self.selected_node.sub[ 0 ] = self.selected_node.sub[ 1 ]
            self.selected_node.sub[ 1 ] = temp
            #You must check for swapping in grandparents of deleted nodes or
            #else the undo algorithm will break
            for item in self.deleted_nodes:
                if item.Get_Parent() == self.selected_node:
                    item.Switch_Index()
        self.Draw()

    def Set_Profile_Color( self, color ):
        """Set the color of the current profile, when it is not the root"""
        if( self.current_profile != GUI.root_profile_name ):
            self.current_profile.Set_Color( color )
            if( self.view_mode == 3 ):
                self.display.Highlight_Handles( self.current_profile.Get_GI_List(), self.current_profile.Get_Color())

    def Get_Color( self ):
        """Get the color of current profile, return "#FF0000" if none"""
        if( self.current_profile != GUI.root_profile_name ):
            return self.current_profile.Get_Color()
        return "#FF0000"

    def New_Profile( self, name, term_list = [] ):
        """Create a new profile given a name and a term list"""
        if(name == '' or name == GUI.root_profile_name): return 0
        if( self.Is_Profile( name ) ):
                return 0
        #at this point name is valid
        p = Profile.Profile( name, self.counter )
        self.counter = self.counter + 1
        self.profile_list.append( p )
        p.term_list = term_list
        self.Apply_Profile_Term_List( p )
        self.display.Add_Profile( name )
        return 1

    def Change_Profile( self, target ):
        """change the current profile to the one given by target"""
        if( target == GUI.root_profile_name ):
            #changes to root
            if( self.current_profile != GUI.root_profile_name ):
                self.view_mode = 0
            self.current_profile = GUI.root_profile_name
        else:
            #changes to current profile
            for item in self.profile_list:
                if( item.Get_Name() == target ):
                    if self.current_profile == GUI.root_profile_name:
                        self.view_mode = 2
                    self.current_profile = item
                    break
        self.Draw()

    def Remove_Profile(self, target):
        """Remove the profile with the name equal to target"""
        if(target=='' or target==GUI.root_profile_name):
            return
        else:
            for item in self.profile_list:
                if( item.Get_Name() == target ):
                    #if target is the current profile, set it to root
                    if( self.current_profile == item ):
                        self.display.Root_Profile()
                    #must set the display to root if deleting the current profile
                        self.Change_Profile( GUI.root_profile_name )
                    self.profile_list.remove( item )
        self.display.Remove_Profile_Name( target )

    def Add_Empty_Profile( self, target ):
        """Add a profile given just a name"""
        if( self.Is_Profile( target ) == 1 ):
            return
        else:
            p = Profile.Profile( target )
            self.profile_list.append( p )
            self.display.Add_Profile( target )

    def Is_Profile(self, name):
        """Tell if there exists a profile with the given name"""
        if( name in self.Profile_List() ):
            return 1

    def Profile_List(self):
        """Return a list of the profile names"""
        to_return = []
        for i in self.profile_list:
            to_return.append(i.Get_Name())
        return to_return
    
    def Add_GI_Leaves( self ):
        """Add GI's subordinate to the currently selected node"""
        if(self.current_profile != GUI.root_profile_name and
           self.selected_node != 0):
            gi_list = self.selected_node.GI_List()
            self.current_profile.Add_GI_List(gi_list)
            self.Draw()
    
    def Remove_GI_Leaves( self ):
        """Remove GI's subordinate to the currently selected node"""
        if(self.current_profile != GUI.root_profile_name and
           self.selected_node != 0):
            gi_list = self.selected_node.GI_List()
            self.current_profile.Remove_GI_List(gi_list)
            self.Draw()
    
    def Reset_Profile( self ):
        """Clear all GI's and apply profile Term list"""
        if(self.current_profile != GUI.root_profile_name ):
            self.current_profile.Clear_GIs()
            self.Apply_Profile_Term_List()

    def Get_Term_List(self):
        """Grab the profile's term list"""
        if self.current_profile != GUI.root_profile_name:
            return self.current_profile.Get_Term_List()
        else:
            return []

    def Set_Term_List(self, term_list):
        """Set the profile's term list"""
        if self.current_profile != GUI.root_profile_name:
            self.current_profile.Set_Term_List(term_list)

    def Apply_Profile_Term_List_2( self ):
        """Apply the profile term list but keep any GI's that have been added
        an improvement over the original version of this function
        """

        gi_list = self.current_profile.Get_GI_List()
        gi_adds = []    #list of added Gi's
        for item in gi_list:
            #Added gi's will have "" as their reason, others will have the first match keyword
            if (self.current_profile.Get_GI_Reason( item ) == ""):
                gi_adds.append( item )
        self.Reset_Profile()    #Apply Profile Term List
        self.current_profile.Add_GI_List( gi_adds ) #Add added Gi's
        self.Draw()
        
    def Apply_Profile_Term_List(self, scp = 0 ):
        """Match titles with the search terms of scp/self.current_profile
        sum of (+terms) without sum of (-terms)
        """
        if( scp == 0 ):
            scp = self.current_profile
        if(scp == GUI.root_profile_name):
            return
        gi_list = self.tree.node.GI_List()
        current_gi_list = scp.Get_GI_List()
        term_list = scp.Get_Term_List()
        #Always add the query
        if( "QUERY" in gi_list ):
            scp.Add_GI( "QUERY" )
        for gi in gi_list:
            #for each gi
            entry = self.ref_table[gi]
            for item in term_list:
                #for each term
                hopeful = re.compile(".*"+item.term+".*", re.I)
                title = entry.Get_Title()
                if hopeful.match( title ):
                    #add it immediately if Include
                    #if any "Exclude" terms match, remove and go to next GI
                    if( item.type == "Include" ):
                        scp.Add_GI(entry.Get_GI(), item.term )
                    elif( item.type == "Exclude" ):
                        scp.Remove_GI( entry.Get_GI() )
                        continue
        scp.Make_Tree(self.distance_file)
        self.Draw()

    def Save_Current_Profile( self, filename=None ):
        """Save a single profile to a cin file"""
        if filename == None:
            filename = self.system.get_filename_by_extension("cin", self.chain)
        gi_list = []
        writer = open( filename, 'w' )
        if( self.current_profile == GUI.root_profile_name ):
            #for base profile, save all gi's in tree
            gi_list = self.tree.node.GI_List( )
        else:
            #for other profiles, get the gi list
            gi_list = self.current_profile.Get_GI_List( )
            #loop through the gi's        
        for item in gi_list:
            #Write the header
            title_line = self.ref_table[ item ].Get_Header( )
            # #$!Q$ clustalw does something screwey to headers
            print 'original title line %s'%(title_line)
            while title_line[1:3] != 'gi' and title_line[1:2] != '|':
                title_line = title_line[:1] + title_line[2:]
            print 'new title line %s'%(title_line)                
            writer.write( title_line )
            #Write the sequence in chunks of 50 character lines
            seq = self.ref_table[ item ].Get_Seq_Text()
            seq = seq.replace('-', '')
            writer.write ( "\n" )
            while( seq != "" ):
                writer.write( seq[ 0:50 ] )
                writer.write( "\n" )
                seq = seq[ 50: ]
            writer.write("\n")
        writer.close()
        
        self.display.Clear_Widgets()

        seq = self.system.ProteinDict[self.chain].get_sequence()
        os.remove(self.system.get_filename_by_extension("aln", self.chain))
        os.remove(self.system.get_filename_by_extension("clu", self.chain))
        strg = Sequencer.Resequence_From_CIN(seq, self.system, self.chain)

        self.Load_File_Internal( strg )

        self.display = GUI.TreeWindow(self, self.editor_view)           # Create a framework for the GUI
        self.Draw(self.editor_view)                                              #Draw the Tree; start out in non-editing mode
        self.sequences = self.display.Get_Sequence_List()
        self.Do_Conservation()

    def Grab_GI_Title( self, line ):
        """given line = fasta header line, extract a title"""
        line = line.replace( ">", "" )
        individuals = string.split( line, '|')
        if len(individuals) != 1:
            gin = individuals[1]
            title = individuals[ len( individuals ) - 1 ].strip("\n ")
        else:
            gin = individuals[0]
            title = individuals[0]
        return gin, title
    
    def Grab_Sequence( self, reader ):
        """given reader is the position after a fasta header, extract a sequence
        return the last line read and the sequence
        """
        #read and concatenate lines until > found or other non-sequence character found
        total_sequence = ''
        sequence = reader.readline( )
        while( sequence != '' and sequence.find( '>' ) == -1 ):
            total_sequence = total_sequence + sequence
            sequence = reader.readline()
        total_sequence = total_sequence.replace( '\n', '' )
        total_sequence = total_sequence.replace( '*', '' )
        
        return sequence, total_sequence
        
    def Filter_By_Protein_Distance( self, distance ):
        """Given a distance, search back from the query node, make the root node the
        the highest ancestor before this distance
        """
        node = self.tree.Get_Node_By_Name("QUERY")  #Find QUERY,
        if( node == 0 ):
            return
        sum = node.data.length  #sum of the traversed distances
        #Go up chain and sum distances while going up tree
        while distance >= sum and node != self.tree.node:
            node = node.parent
            sum = sum + node.data.length
        self.tree.node = node
        node.parent = 0
        self.Draw()

    def Filter_By_Protein_Gap( self, percentage ):
        """Given a filter percentage, remove any sequence whose unmatched gap percentage between the first
        and last characters of the QUERY sequence is higher than the percentage
        """
        if( percentage < 0 or percentage > 100 ):
            return
        token = 'QUERY'
        try:
            self.ref_table[token]
        except KeyError:
            token = 'query'
            
        original_sequence = self.ref_table[token].Get_Seq_Text()
        copy_seq = original_sequence.strip("-")
        index = original_sequence.find( copy_seq[0] )   #index of first character
        if( index == -1 ):
            return
        end_index = index + len( copy_seq ) #index of the last character

        split_list = copy_seq.split('-')
        space_list = []     #a list of where the gaps,'-', occur
        count = 0
        for i in range( len (split_list) - 1 ):
            count = count + len( split_list[i] )
            space_list.append( count )
            count = count + 1
        gi_list = self.tree.node.GI_List() #Get the gi's of the whole tree

        removing_gi_list = []   # a list of the gi's to remove
        for item in gi_list:
            #Get corresponding sequence segment
            comp_seq = self.ref_table[ item ].Get_Seq_Text()[index:end_index]
            
            space_count = comp_seq.count('-')   #count the spaces
            for i in range( len(space_list) ):  #decrement for Matched spaces
                if( comp_seq[space_list[i] ] == '-' ):
                    space_count = space_count - 1
            #end for i
            if( float(space_count*100) / len( comp_seq ) >= percentage ):
                removing_gi_list.append( item )

        hold = self.selected_node
        
        #for each item in removing_gi_list, get its node, delete it
        #this makes the deleted_nodes unrecoverable.
        for item in removing_gi_list:        
            self.selected_node = self.tree.Get_Node_By_Name( item )
            if self.selected_node != 0:
                self.Delete_Sub()
        self.selected_node = hold
        self.deleted_nodes = []
        self.Draw()
    
                
