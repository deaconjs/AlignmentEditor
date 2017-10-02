from Tkinter import *
from CanvasBox import *
import string
import Pmw
#Dialogs
import tkColorChooser
import tkFileDialog
import DialogProfileAdjust
import ExpressionAdjust
import tkMessageBox

root_profile_name ='BASE'
#A class associating the drawn handles to a specific node in the tree
class LineSegment:
    def __init__( self, line_handle, node, state = "P" ):
        self.line_handle = line_handle  #line segment
        self.node = node                #node in tree
        self.text_handle = 0            #data handle
        self.gi_handle = 0              #gi handle
    
    def Add_Text( self, th ):
        """Add a text handle to the LineSegment"""
        self.text_handle = th
        
    def Get_Text(self):
        return self.text_handle
        
    def Add_GI( self, gih ):
        """ Add a gi handle to the LineSegment """
        self.gi_handle = gih

    def __str__( self ):
        return "[" + str(self.line_handle) + "," + self.node.data.name + "]"

#holds the dimensions for the drawing,
cb = CanvasBox( 20, 30, 1, 5, 250, 0 )

#Class dealing specifically with the GUI
class TreeWindow:
    def __init__( self, tree_system, editor=0):
        """ Create the tree. The editor option gives full control, including menus. 
            If iditor is 0, toplevel should be 'None'
        """
        cb.order = 1
        self.root = tree_system        #a widget to pack all of this in
        self.system = tree_system            #the parent system
        self.selected = 0               #handle of the rectangle drawn around selected branch and children
        self.selected_ls = 0            #LineSegment that is currently selected
        self.handle_list = []           #list of the the LineSegments for the current tree
        self.leaf_list = []             #list of the LineSegments that are also leaves
        self.profile_name_list = [ root_profile_name ] #list of the profile names
        self.branch_color = "black"     #color for the tree
        self.highlight_color = "red"    #color for highlights, affects self.filter_line, selected_ls
        if editor:
            self.Create_Menu( )         #initialize menu
            #Profile listbox
            self.combobox_profile = Pmw.ComboBox( self.root, label_text='Current Profile', labelpos='n',scrolledlist_items=self.profile_name_list,dropdown=1,selectioncommand=self.system.Change_Profile)
            self.combobox_profile.pack( side = TOP )
            self.Root_Profile( )        #Set combobox selection to 0, which should be the root profile
        #Vertical scroll    
        self.frame_scroll = Frame( self.root )
        self.frame_scroll.pack(side=LEFT,fill=Y)
        #Create the paned widget
        self.pane_widget = Pmw.PanedWidget( self.root, orient = "horizontal", command = self.Pane_Resized )
        self.pane_widget.pack( side = LEFT, expand = 2,fill = BOTH )

        self.Tree_Frame()           # build Frame for the tree stuff
        self.Data_Frame()           # another Frame for the data to show
        self.Configure_YScroll()

        self.filter_line = 0        #This is the line connected to the scale
        self.filter_line_on = 0     #Tells the state of the scale, 0-Off 1-On
        self.filter_distance = 0    #The current position of the line
        self.scale_text = 0         #this is the handle to the text for the scale canvas box
        self.scale_marker = 0       #this is a list of two elements,
                                    #the first is the handle to the line on the canvas_scale
                                    #the second is the handle to the line on the canvas_one
    def Clear_Widgets( self ):
        self.combobox_profile.destroy()
        self.menu.destroy()
        self.pane_widget.destroy()
        
    def Adjust_Menu( self, menuoptions = 0):
        """ Create the menu
            Adjust the menu according to menuoptions
            If menuoptions == 0, it is displaying a base tree
            Else if menuoptions == 1, it is displaying a profile tree
            See Create_Menu if indices change
        """
        pass
        #base_tree = 6
        #profile_tree = 7
        #if( menuoptions == 0 ):
        #    self.treeview_menu.entryconfig( base_tree , state="active" )
        #    self.treeview_menu.entryconfig( profile_tree , state="disabled" )
        #    self.menu.entryconfig( 4 , state="active" )
        #    self.menu.entryconfig( 5 , state="disabled" )
        #elif(menuoptions == 1):
        #    self.treeview_menu.entryconfig(base_tree ,state="disabled")
        #    self.treeview_menu.entryconfig(profile_tree ,state="active")
        #    self.menu.entryconfig(4 ,state="disabled")
        #    self.menu.entryconfig(5 ,state="active")

    def Create_Menu( self ):
        self.menu = Pmw.MenuBar(self.root, hull_relief = 'raised',hull_borderwidth = 1)
        self.menu.addmenu('Profile', 'Profile Controls')
        self.menu.addmenuitem('Profile', 'command', 'Add/Remove Profiles', command=self.Adjust_Profile_List, label='Add/Remove Profiles')
        self.menu.addmenuitem('Profile', 'command', 'Create New Profile', command=self.Create_Profile, label='Create New Profile')
        self.menu.addmenuitem('Profile', 'command', 'Save Current Profile', command=self.Save_Current_Profile, label='Save Current Profile')
        self.menu.addmenuitem('Profile', 'command', 'Load New Base', command=self.Load_Base, label='Load New Base')

        #menu drop for the viewing options of the tree
        self.menu.addmenu('Tree View', 'Base Tree Controls')
        self.menu.addmenuitem('Tree View', 'command', 'Preorder', command=self.View_Preorder, label='Preorder')
        self.menu.addmenuitem('Tree View', 'command', 'Inorder', command=self.View_Inorder, label='Inorder')
        self.menu.addmenuitem('Tree View', 'command', 'Postorder', command=self.View_Postorder, label='Postorder')
        self.menu.addmenuitem('Tree View', 'command', 'Scale Line', command=self.Toggle_Filter_Line, label='Scale Line')

        #cascade 1, an index to note
        self.menu.addcascademenu('Tree View', 'Base Tree')
        self.menu.addmenuitem('Base Tree', 'command', 'Alone', command=self.View_Tree_0, label='Alone')
        self.menu.addmenuitem('Base Tree', 'command', 'With Profiles', command=self.View_Tree_1, label='With Profiles')
        
        #cascade 2, an index to note
        self.menu.addcascademenu('Tree View', 'Profile Tree')
        self.menu.addmenuitem('Profile Tree', 'command', 'Alone', command=self.View_Tree_2, label='Alone')
        self.menu.addmenuitem('Profile Tree', 'command', 'Against Base Tree', command=self.View_Tree_3, label='Against Base Tree')

        #menu drop for the data to be shown in the right canvas
        self.menu.addmenu('Data View', 'Data View Controls')
        self.menu.addmenuitem('Data View', 'command', 'Sequence', command=self.Show_Sequences, label='Sequence')
        self.menu.addmenuitem('Data View', 'command', 'Title', command=self.Show_Titles, label='Title')
        self.menu.addmenuitem('Data View', 'command', 'Header', command=self.Show_Headers, label='Header')
        
        #menu for performing operations on the base tree
        self.menu.addmenu('Base Operations', 'Base Operation Controls')
        self.menu.addmenuitem('Base Operations', 'command', 'Delete Selection', command = self.system.Delete_Sub, label='Delete Selection')
        self.menu.addmenuitem('Base Operations', 'command', 'Undo Deletion',command = self.system.Undelete, label='Undo Deletion')
        self.menu.addmenuitem('Base Operations', 'command', 'Isolate Selection', command = self.system.Isolate, label='Isolate Selection')
        self.menu.addmenuitem('Base Operations', 'command', 'Undo Isolation', command = self.system.Unisolate, label='Undo Isolation')
        self.menu.addmenuitem('Base Operations', 'command', 'Switch Branches', command = self.system.Switch, label='Switch Branches')
        self.menu.addmenuitem('Base Operations', 'command', 'Separate Query By Distance', command = self.Apply_Line_Filter, label='Separate Query By Distance')
        self.menu.addmenuitem('Base Operations', 'command', 'Separate Query By Gaps', command = self.Apply_Space_Filter, label='Separate Query By Gaps')

        #menu for performing operations on a profile tree
        self.menu.addmenu('Profile Operations', 'Profile Operation Controls')
        self.menu.addmenuitem('Profile Operations', 'command', 'Remove Leaves', command = self.system.Remove_GI_Leaves, label='Remove Leaves')
        self.menu.addmenuitem('Profile Operations', 'command', 'Add Leaves', command= self.system.Add_GI_Leaves, label='Add Leaves')
        self.menu.addmenuitem('Profile Operations', 'command', 'Reset to Keywords', command=self.system.Reset_Profile, label='Reset to Keywords')
        self.menu.addmenuitem('Profile Operations', 'command', 'Reapply Keywords', command=self.system.Apply_Profile_Term_List_2, label='Reapply Keywords')
        self.menu.addmenuitem('Profile Operations', 'command', 'Change Color', command=self.Set_Profile_Color, label='Change Color')
        self.menu.addmenuitem('Profile Operations', 'command', 'Organize Keywords', command=self.Adjust_Keyword_List, label='Organize Keywords')
        self.menu.pack(side='top', fill=BOTH, expand=1)
    
    def Tree_Frame( self ):
        """Setup the frame that will be displaying the tree"""
        #Create pane
        p = self.pane_widget.add( "Tree", min = 0.2, max = 0.9, size = 0.5 )
        frame_tree = Frame( p )
        #Add the scale
        self.canvas_scale = Canvas( frame_tree, height = 10 )
        self.canvas_scale.bind( '<Button-1>', self.Scale_Pick )
        self.canvas_scale.bind( '<B1-Motion>', self.Scale_Pick )
        self.canvas_scale.pack(side = TOP)
        #canvas for drawing the tree on            
        self.canvas_one = Canvas( frame_tree )
        #Make sure these values are consistent with self.canvas_two in Data_Frame
        self.canvas_one.pack( side = TOP , fill = BOTH , expand = 1 )
        self.canvas_one.bind( '<ButtonRelease-1>', self.Tree_Pick )
        frame_tree.pack( side = LEFT, fill = BOTH )
    
    def Data_Frame( self ):
        """Setup the frame that will display data corresponding to the leaves of the tree"""
        #Create pane
        p = self.pane_widget.add( "Data", min = 0.1, max = 0.9)
        frame_sequence = Frame( p )
        #xscroll at the top
        self.xscroll = Scrollbar( frame_sequence, orient = HORIZONTAL  )
        self.xscroll.pack(side = TOP, fill = X )
        #create the canvas where the data will be displayed
        self.canvas_two = Canvas( frame_sequence )
        #Make sure these values are consistent with self.canvas_one in Tree_Frame
        self.canvas_two.pack( side = TOP, fill = BOTH, expand = 1 )
        self.xscroll.config( command = self.canvas_two.xview )
        self.canvas_two.config( xscrollcommand = self.xscroll.set )
        frame_sequence.pack(side=LEFT, fill = BOTH)

    def Configure_YScroll( self ):
        """configure the settings of the yscroll and of its relation with canvas_one, canvas_two"""
        Label(self.frame_scroll).pack( side = TOP )
        self.yscroll = Scrollbar( self.frame_scroll )
        self.yscroll.config( command = self.Vertical_Scroll )
        self.canvas_one.config( yscrollcommand = self.Double_Expand )
        self.canvas_two.config( yscrollcommand = self.Double_Expand )

    def Double_Expand( self, one = -1, two = -1 ):
        """The y distance to view changed"""
        pre = self.yscroll.get()
        if( one == '0' and two == '1' and pre[0]!='0' and pre[1]!='1' ):
            #hide scroll if inactive
            self.yscroll.pack_forget( )
        elif( pre[0] != '0' and pre[1] != '1' ):
            #show scroll if inactive and needed
            self.yscroll.pack( side = LEFT, fill = Y )
        self.yscroll.set( one, two )

    def Vertical_Scroll( self, event, one = 0, two = 0 ):
        """ Vertical scroll happened """
        if(event == 'moveto' ):
            self.canvas_one.yview( 'moveto', one )
            self.canvas_two.yview( 'moveto', one )
        else:
            self.canvas_one.yview( event, one, two )
            self.canvas_two.yview( event, one, two )
        #Is there any hesitancy with the Tree_Pick when the event is yscroll?
    
    def Draw_Tree( self, rooted_tree, menuoptions = 0, editor = 0 ):
        """ draw a tree, rooted_tree is of class Node from TreeParse
            menuoptions is the type of tree, base or profile, its main function is in Adjust_Menu
            editor=1 indicates full menu presence
        """
        #Clear the previous information
        self.Reset_Selection()
        self.canvas_one.delete( ALL )
        self.canvas_two.delete( ALL )
        self.handle_list = []
        
        if editor:
            self.Adjust_Menu( menuoptions )
        #if no node
        if( rooted_tree == 0 ):
            self.canvas_one.create_text( cb.xorigin, 5, text="There is no tree to display", anchor = NW )
            ys = 0
        #one node
        elif( rooted_tree.sub == [] ):
            #if there is only one node, make its length one because a zero length will not show up
            store = rooted_tree.data.length
            rooted_tree.data.length = 1
            xlong = rooted_tree.Longest_Branch( )
            cb.New_XLong( xlong )
            ys = self.Draw_Node( rooted_tree, cb.xorigin, cb.yorigin)
            rooted_tree.data.length = store
        else:
            #recursively draw the tree, temporarily store the root's length and make it zero
            #If the root is long(Isolated), it does not squish the rest of the data
            store = rooted_tree.data.length
            rooted_tree.data.length = 0
            #Get the longest distance from root to leaf
            xlong = rooted_tree.Longest_Branch( )
            cb.New_XLong( xlong )   #Change the scale
            ys, ypos1 = self.Rec_Draw_Tree( rooted_tree, cb.xorigin, cb.yorigin )
            #Extend the root node so that it is visible
            ls = self.Find_Line_By_Node( rooted_tree )
            self.canvas_one.coords( ls.line_handle, cb.xorigin-5, ypos1, cb.xorigin, ypos1 )
            rooted_tree.data.length = store #restore the root node's length
        ys = ys + cb.ytick
        self.canvas_one.create_text(20,ys,text="_____")
        self.canvas_two.create_text(20,ys,text="_____") #end markers
        #Set the scrollregions of the canvases
        ys = ys + cb.ytick
        self.ys = ys + 0*cb.ytick
        self.canvas_one.config( scrollregion = ( 0, 0, 300, self.ys ) )
        self.canvas_two.config( scrollregion = ( 0, 0, 300, self.ys ) )
        self.Draw_Scale()

    def Draw_Scale( self ):
        """ Draw the scale object on top of the tree frame """
        self.canvas_scale.delete(ALL)
        if(cb.longx != 0):
            value = str( round( cb.longx, 3 ) )
            self.canvas_scale.create_line( cb.xorigin,5,cb.xorigin + cb.xtotal,5 )
            splits = 10.0
            increment = cb.xtotal/splits
            for i in range(int(splits + 1)):
                self.canvas_scale.create_line( int(cb.xorigin+i*increment),1,int(cb.xorigin+i*increment),9 )
            if( self.filter_distance > cb.longx ):
                self.filter_distance = cb.longx
            x = cb.xtotal - self.filter_distance*cb.xtotal/cb.longx + cb.xorigin
            top = str(round(self.filter_distance,3))
            
            while len(top) < 5:
                top = top + "0"
            self.scale_text = self.canvas_scale.create_text( cb.xorigin + cb.xtotal + 10,1,anchor = "nw",text = top + "/" + value)
            self.scale_marker = self.canvas_scale.create_polygon( x,7, x+4,3, x-4,3, fill=self.highlight_color,outline=self.highlight_color )
            if( self.filter_line_on ):
                if(self.filter_line != 0 ):
                    self.canvas_one.delete( self.filter_line )
                self.filter_line = self.canvas_one.create_line( x,0,x,self.ys, fill=self.highlight_color)

    def Rec_Draw_Tree( self, cur_node, xs, ys ):
        """ Draw the tree recursively, cur_node points to the current_node,
            xs is the horizontal start, ys is the vertical start
        """
        yhold = []  #holds the y values of the children
        ypos1 = 0   #the yvalue of the current node
        ypos = 0
        new_xstart = cur_node.data.length * cb.xtick + xs
        #for each child of the current node
        for i in range( len( cur_node.sub ) ):
            #current node is to be drawn before the (cb.order)-th child
            if ( i == cb.order ):
                ypos1 = self.Draw_Node( cur_node, xs, ys )
                if( cb.order == 1 ):
                    ypos1 = ys
                    ys = ypos1 + cb.ytick
            if( len( cur_node.sub[i].sub ) == 0 ):#Draw a leaf
                ypos = self.Draw_Node( cur_node.sub[i], new_xstart, ys )
                yhold.append( int(ypos) )
            else: #Draw an internal node
                ys, ypos = self.Rec_Draw_Tree( cur_node.sub[i], new_xstart, ys )
                yhold.append( ypos )
            if( i < len( cur_node.sub ) - 1 ):
                ys = ys + cb.ytick
        if ( cb.order != 1 and cb.order == len( cur_node.sub ) ):
            ypos1 = self.Draw_Node( cur_node, xs, ys )
        elif( cb.order == 1 and cb.order == len( cur_node.sub) ):
            ypos1 = self.Draw_Node( cur_node, xs , ys+cb.ytick )
            ypos1 = ypos1 - cb.ytick

        #draw the vertical lines to the children
        for item in yhold:
            self.canvas_one.create_line( new_xstart, item, new_xstart, ypos1, width = 3, fill=self.branch_color )
        #return the farthest vertical position drawn and the position of the line of the current segment
        return ys, ypos1

    def Draw_Node( self, node, xstart, ystart):
        """draw only the current node given xstart, ystart"""
        xdist = node.data.length * cb.xtick
        handle = self.canvas_one.create_line( xstart, ystart, xstart+xdist, ystart,width = 3, fill=self.branch_color )
        #Attach a handle to a node and place in the handle_list of all LineSegments
        ls = LineSegment( handle, node )
        self.handle_list.append(ls)
        return ystart

    def Pair_Handles( self, ref_list ):
        """Of the line segments that were drawn, grab the node's id
        match it in the ref_list, and draw the corresponding text to go with it
        """
        longest = 0
        self.leaf_list = []
        for x in self.handle_list:
            if( x.node.children() == 0 and x.node.data.name != '' ):
                ref_entry = x           #Copy the LineSegment
                id = x.node.data.name
                #Get the top of the line, place the id value on the canvas
                yheight = self.canvas_one.bbox( x.line_handle )[ 3 ]
                tag = self.canvas_one.create_text( cb.xtotal + 30, yheight,
                                                   anchor = SW, text = id, fill = self.branch_color )
                ref_entry.Add_GI( tag ) #Add the GI handle to the LineSegment
                if not ref_list.has_key( id ):
                    continue
                total_sequence = ref_list[ id ].Get_Seq_Text()
                if(len( total_sequence ) > longest):
                    longest = len(total_sequence)
                #create the handle for the canvas_two display but give it no text
                #text will be filled in by self.Change_Seq
                texttag = self.canvas_two.create_text( 10, yheight, text="", anchor = SW,font=("courier",10) )
                ref_entry.Add_Text( texttag )
                #At this point add LineSegments with leaf nodes into a separate list
                self.leaf_list.append( ref_entry )
                
    def Get_Sequence_List(self, index=None):
        sequence_list = []
        for x in self.handle_list:
            if( x.node.children() == 0 and x.node.data.name != '' ):
                handle = x.Get_Text()
                sequence_list.append(self.canvas_two.itemcget(handle, 'text'))
        return sequence_list

    def Change_Seq( self, ref_list, type):
        """ Change the data that is being shown in canvas_two
            ref_list is like a database and type is what to display
        """
        longest = 0
        ender = 0
        #for each LineSegment in the leaf_list
        for id in self.leaf_list:
            name = id.node.data.name    #grab the name
            item = ref_list[ name ]     #look up the name
            sqh = id.text_handle
            textin = ""
            #Store information
            if type == 'Sequence':
                textin = item.Get_Seq_Text()
            elif type == 'Title':
                textin = item.Get_Title()
            elif type == 'Header':
                textin = item.Get_Header()
            self.canvas_two.itemconfig( sqh, text=textin ) #display information
            if( len( textin ) > longest ):
                ender = self.canvas_two.bbox( sqh )[2]
                longest = len( textin )
        #Configure the scroll region in the x direction
        current_bounds = self.canvas_two.cget( "scrollregion" )
        x1,y1,x2,y2 = current_bounds.split(' ')
        longest = longest*1
        self.canvas_two.config( scrollregion= ( 0, int(y1), ender, int(y2) ) )
    
    def Tree_Pick(self, event):
        """ Mouseclick on self.canvas_one """
        x = event.x
        y = event.y + self.yscroll.get()[0]*self.ys
        #find the LineSegment given the x and y click position
        index = self.Find_Line_By_XY( x, y )
        if( self.selected_ls == index ):    #Deselect if it is the current selection
            self.Reset_Selection()
            return
        if( self.selected_ls != 0 ):
            self.Reset_Selection()  #nothing found
        if( index!=-1 ):#if found
            gi_list = index.node.GI_List()  #Get the list of children of the current node
            #grab the GI children of the branch, they will be in the order that they were drawn
            index_upper = index_lower = index

            if( len(gi_list) > 0 ): #gi_list will be empty if the node picked was a leaf
                index_upper = self.Find_Line_By_GI( gi_list[ 0 ] )
                index_lower = self.Find_Line_By_GI( gi_list[ len( gi_list ) - 1 ] )
            #calculate the dimensions of a bounding rectangle
            bbox = self.canvas_one.bbox(index.line_handle)
            xb1 = bbox[2]-5 #a little xback from the chosen node, left
            bbox = self.canvas_one.bbox(index_upper.line_handle)
            yb1 = bbox[1]-cb.ytick/2    #above the highest node, top
            bbox = self.canvas_one.bbox(index_lower.line_handle)
            yb2 = bbox[3]+cb.ytick/2    #below the lowest node, bottom
            xb2 = bbox[2]               #right
            self.selected_ls = index
            #set the selected node in the system
            self.system.Set_Selected_Node( self.selected_ls.node )
            #change color, draw bounding box
            self.canvas_one.itemconfig( self.selected_ls.line_handle, fill = self.highlight_color)
            self.selected = self.canvas_one.create_rectangle(xb1,yb1,xb2,yb2,outline= self.highlight_color )
        if( index==-1 ):
            self.Reset_Selection()

    def Find_Line_By_XY( self, x, y ):
        """ Find a LineSegment within reasonable distance of x,y on self.canvas_one
            Return the LineSegment if found or -1 if not
        """
        for i in self.handle_list:
            #examine the bounding box of each line
            bbox = self.canvas_one.bbox( i.line_handle )
            xb1 = bbox[ 0 ]
            yb = ( bbox[ 1 ] + bbox[ 3 ] ) / 2
            xb2 = bbox[ 2 ]
            if x >= xb1 and x <= xb2 and abs( y-yb ) <= cb.ytick / 2:
                #found, return handle
                return i
        #not found return -1
        return -1

    def Find_Line_By_Node( self, node ):
        """ Find a LineSegment given a node to match
            Returns the node if found, -1 if not
        """
        for i in self.handle_list:
            if i.node == node:
                #found, return handle
                return i
        #not found return -1
        return -1

    def Find_Line_By_GI(self,gi):
        """ Find a LineSegment by its gi value
            Returns the node if found, -1 if not
        """
        for i in self.leaf_list:
            #for each item in the leaf_list, since leaves are the only lines with GI's
            if gi == i.node.data.name:
                return i
        return -1

    def Add_Profile( self, name ):
        """ Add a name to the profile combobox """
        self.profile_name_list.append( name )
        self.combobox_profile.setlist( self.profile_name_list )

    def Remove_Profile_Name(self,name):
        """ Remove a name from the profile combobox """
        if name in self.profile_name_list:
            self.profile_name_list.remove(name)
            self.combobox_profile.setlist( self.profile_name_list )

    def Reset_Profile_Name( self ):
        """ Set the combobox back to """
        self.profile_name_list = [ root_profile_name ]
        self.combobox_profile.setlist( self.profile_name_list )
        self.Root_Profile()

    def Root_Profile(self):
        """ Set combobox selection to 0, which should be the root profile """
        self.combobox_profile.selectitem( 0 )
        
    def Highlight_Handles( self, gi_list, color_to ):
        """ Highlight the gi's in the gi_list to color_to,
            and gi's not in the list are set to the branch_color
        """
        for i in self.leaf_list:
            gi = i.node.data.name
            if gi in gi_list:
                self.canvas_one.itemconfig( i.gi_handle, fill = color_to )
            else:
                self.canvas_one.itemconfig( i.gi_handle, fill = self.branch_color )
    
    def Highlight_Handles_2(self,gi_list,color_to,row):
        """ Add bars next to the gi's in the gi_list of color_to in specific row """
        xamount = cb.xtotal + 75 + 5*row
        for i in self.leaf_list:
            gi = i.node.data.name
            if gi in gi_list:
                bbox = self.canvas_one.bbox( i.line_handle )
                self.canvas_one.create_line(xamount,bbox[1],xamount,bbox[3], fill=color_to,width=4  )
        return

    def Adjust_Profile_List( self ):
        """ Manage the profile list using the DialogProfileAdjustment Dialog """
        listing = self.system.Profile_List()    #Get the list of current profiles
        d=DialogProfileAdjust.DialogProfileAdjustment( self.root, listing, 'Profiles', 'Organize the Profiles' )
        if( d.return_state == 0 ):
            return  #Cancel hit
        #Go through d's profile list, and try to add names not seen before
        for item in d.profile_list:
            self.system.Add_Empty_Profile( item )
        #Go through d's remove list, and try to remove names if they existed
        for name in d.remove_list:
            self.system.Remove_Profile( name )
    
    def Adjust_Keyword_List( self ):
        """ Manage the keyword list using the ExpressionAdjust Dialog """
        listing = list( self.system.Get_Term_List( ) )  #get the term list of the current profile

        d=ExpressionAdjust.ExpressionAdjuster( self.root, listing, 'Keywords' )
        if(d.return_state==0):
            return  #Cancel hit
        self.system.Set_Term_List( d.profile_list )
        self.system.Apply_Profile_Term_List_2()
    
    def Set_Profile_Color(self):
        """ Set a profile's color """
        default= self.system.Get_Color()
        color = tkColorChooser.askcolor(default,parent=self.root)
        if( color[1] == None ):
            return
        else:
            self.system.Set_Profile_Color( color[1] )
    
    def Create_Profile(self):
        """ Create an individual profile"""
        #Run the dialog to get a list of the keywords
        d=ExpressionAdjust.ExpressionAdjuster( self.root, [], 'Keywords', "Create the keyword list" )
        if d.return_state == 0:
            return  #Cancel hit
        name = self.Generate_Profile_Name(d.profile_list)
        result = ""
        title_string = 'Name the Profile',
        #loop until cancel hit or (ok and name does not exist)
        while( result != "OK" and result != "Cancel" ):
            prompt_dialog = Pmw.PromptDialog(self.root,
                title = title_string,
                label_text = 'Name:',
                entryfield_labelpos = 'w',
                defaultbutton = 0,
                buttons = ('OK','Cancel'))
            prompt_dialog.insert(END,name)
            result = prompt_dialog.activate()
            if( result == "OK" ):
                name =  prompt_dialog.get()
                if self.system.Is_Profile( name ) == 1 or name == root_profile_name:
                    title_string = 'Name: ' + name + ' is already used'
                    result = ''
        #Create the new profile in the system, given a name and a profile list                    
        self.system.New_Profile(name, d.profile_list)

    def Generate_Profile_Name(self, profile_list):
        """ Generate a profile name given a profile_list """
        name = ""
        #Take the first three letters of the word itself-
        #   the real first three letters are (+) or (-)
        for term in profile_list:
            name = name + term.Display_()[3:6]
        original_length = len(name)
        counter = 1
        spl = self.system.Profile_List()
        #While there are matches, increment the counter and try again
        while( name in spl ):
            name = name[:original_length]+str(counter)
        return name
        
    def Save_Current_Profile(self):
        """ Prompt the user to save the current profile to disk """
        #name = tkFileDialog.asksaveasfilename()
        #if( name == "" ):
        #    return
        #self.system.Save_Current_Profile(name)
        self.system.Save_Current_Profile()
    
    def Load_Base(self):
        """ Prompt the user to Load a new profile as the base tree """
        name = tkFileDialog.askopenfilename()
        if( name == "" ):
            return
        self.system.Load_File_Internal(name)
    
    def Reset_Selection(self):
        """ Reset the selection items """
        #if previous selection
        if( self.selected != 0 ):
            self.canvas_one.delete( self.selected ) #remove bounding rectangle
        #return chosen node to branch_color
            self.canvas_one.itemconfig( self.selected_ls.line_handle , fill = self.branch_color )
            self.system.Set_Selected_Node(0)
            self.selected = 0
            self.selected_ls = 0
    
    def Pane_Resized( self, new_sizes ):
        """ The pane was resized """
        if(new_sizes[0] > 200 ):
            cb.xtotal = new_sizes[0]-100
            self.canvas_one.config(width = new_sizes[0])
            self.canvas_scale.config(width = new_sizes[0])
        else:
            cb.xtotal = 200-100
            self.canvas_one.config(width = 200)
            self.canvas_scale.config(width = 200)
        if (len(new_sizes) > 1 ):
            self.canvas_two.config(width=new_sizes[1])
        self.system.Draw()

    
    def Scale_Pick( self, event ):
        """ Event-canvas_scale mouse click, mouse move """
        x = event.x - cb.xorigin
        y = event.y
        #Was the position within the scale?
        if x < 0 and x > -2:
            x = 0   #low adjust
        if x > cb.xtotal and x < cb.xtotal+2:
            x = cb.xtotal   #high adjust
        if( x >= 0 and x <= cb.xtotal ):
            self.filter_distance = round((cb.xtotal - float(x))/cb.xtotal*cb.longx,3)
            self.Draw_Scale()
        return
    
    def Toggle_Filter_Line( self ):
        """ Reverse whether the filter line is displayed or not """
        if self.filter_line_on == 1:
            if( self.filter_line != 0 ):
                self.canvas_one.delete( self.filter_line )
            self.filter_line = 0
            self.filter_line_on = 0
        elif self.filter_line_on == 0:
            if(self.filter_line != 0 ):
                self.canvas_one.delete( self.filter_line )
            x = cb.xtotal - self.filter_distance*cb.xtotal/cb.longx + cb.xorigin
            self.filter_line = self.canvas_one.create_line( x,0,x,self.ys, fill=self.highlight_color)
            self.filter_line_on = 1
    
    def Get_Filter_Distance( self ):
        """ Retrieve the filter distance """
        return self.filter_distance
    
    def Apply_Line_Filter( self ):
        """ Apply the filter by Protein Distance """
        self.system.Filter_By_Protein_Distance( self.filter_distance )
    
    def Apply_Space_Filter( self ):
        """ Apply a filter for space correlation """
        result = ""
        #prompt for a percentage to filter out
        while( result != "OK" and result != "Cancel"):
            prompt_dialog = Pmw.PromptDialog(self.root,
                title = "Input Percentage",
                label_text = 'Gap %(0-100):',
                entryfield_labelpos = 'w',
                defaultbutton = 0,
                buttons = ('OK','Cancel'))
            prompt_dialog.insert(END,"0")
            result = prompt_dialog.activate()
            if( result == "OK" ):
                spercent =  prompt_dialog.get()
                if( not spercent.isdigit() or spercent.find('.')!=-1):
                    result = ""
        if(result == "OK"):
            fpercent = float( spercent )
            self.system.Filter_By_Protein_Gap( fpercent )
        
    def Warning_Message( self ):
        """ Display a warning message about an improper load """
        message = "This program prefers the FASTA file format\nPlease check the file for >gi|id|title followed by the sequence,\n or for enough sequences"
        tkMessageBox.showwarning(
            "File Opening Error",
            message
        )
    
    def Show_Sequences( self ):
        """ Tell the system to display the sequence data """
        self.system.Change_Seq( "Sequence" )

    def Show_Titles( self ):
        """ Tell the system to display the Title data """
        self.system.Change_Seq( "Title" )

    def Show_Headers( self ):
        """ Tell the system to display the header data """
        self.system.Change_Seq( "Header" )
    
    def View_Inorder( self ):
        """ draw the tree Inorder """
        cb.order = 1
        self.system.Draw( )
        
    def View_Preorder( self ):
        """ draw the tree Preorder """
        cb.order = 0
        self.system.Draw( )
    
    def View_Postorder( self ):
        """ draw the tree Postorder """
        cb.order = 2
        self.system.Draw( )
    
    def View_Tree_0(self):
        """ Tell the system to show the base tree no profiles """
        self.system.Set_Tree_View_Mode(0)

    def View_Tree_1(self):
        """ Tell the system to show the base tree with profiles """
        self.system.Set_Tree_View_Mode(1)
    
    def View_Tree_2(self):
        """ Tell the system to show the profile tree  """
        self.system.Set_Tree_View_Mode(2)
    
    def View_Tree_3(self):
        """ Tell the system to show the profile tree "imposed" against the base tree """
        self.system.Set_Tree_View_Mode(3)
    
