from Tkinter import *
import Pmw
import re
import Profile

#The dialog for the expression organizer
class ExpressionAdjuster:
    def __init__(self, parent, e_list, listbox_title, box_title = ""):
        
        self.profile_list = list( e_list )  # a copy of the expression list
        self.expression_list = e_list
        self.remove_list = []               #a list of terms to remove
        self.root = Pmw.Dialog(parent,buttons=('Confirm','Cancel'),defaultbutton='Confirm',command=self.Execute,title=box_title )
        
        self.top = self.root.interior()     #top frame
        
        self.label_new = Label( self.top, text = "New Term" )

        entry_column = 0
        self.label_new.grid(row=1,column=entry_column)
    #Entry - User types in text here
        self.entry_new = Entry( self.top )
        self.entry_new.grid(row=2,column=entry_column)
        self.initial_focus=self.entry_new
    #Include button - transfer text in Entry to Keywords listbox, mark as include
        self.button_add = Button(self.top,text="Include>",command=self.Include)
        self.button_add.grid(row=3,column=entry_column,sticky="e,w")
    #Exclude button -  transfer text in Entry to Keywords listbox, mark as exclude 
        self.button_exclude = Button(self.top,text="Exclude>",command=self.Exclude)
        self.button_exclude.grid(row=4,column=entry_column,sticky="e,w")
    #Change from an include to an exclude, or exclude to an include
        self.button_toggle = Button( self.top, text="Toggle",command=self.Toggle)
        self.button_toggle.grid(row = 5, column = entry_column,sticky="e,w")
    #Keyword Listbox - PMW scrolled box of terms to keep 
        self.profile = Pmw.ScrolledListBox(self.top,labelpos='n',label_text=listbox_title)
        dl = self.Make_Display_List( self.profile_list )
        self.profile.setlist( dl )
        self.profile.grid(row = 0, column = 1, rowspan = 8)
    #Remove button - transfer term from Keyword listbox to Removed listbox
        self.button_remove = Button(self.top,text=">Remove>",command=self.Remove)
        self.button_remove.grid(row = 1, column = 2,sticky="e,w")
    #Keep button -transfer term from Removed listbox to Keyword listbox
        self.button_unremove = Button( self.top, text="<Keep<",command=self.Unremove)
        self.button_unremove.grid(row = 5, column = 2,sticky="e,w")

    #Removed Listbox - PMW scrolled box of terms to leave out
        self.removed = Pmw.ScrolledListBox(self.top, labelpos="n", label_text='Removed')
        self.removed.grid(row = 0, column = 3, rowspan = 8)
        
        self.return_state = 0
        self.root.activate()
        
        if not self.initial_focus:
            self.initial_focus = self
        return
#Final function run when closing the dialog.
    def Execute(self, result):
        if(result=='Confirm'):
            self.Confirm()
        elif(result=='Cancel'):
            self.Cancel()
        elif(result==None):
            self.Cancel()
    #Determine if the name preexists in either the profile_list or remove_list
    def Name_Preexists( self, name ):
        exclude = ["","BASE"]
        if( name in exclude ):
            return 1
        dl = self.Make_Display_List( self.profile_list )
        rl = self.Make_Display_List( self.remove_list )
       #Check for any occurence of the name with "(+)" or "(-)"
        if( ("(+)"+ name ) in dl ):
            return 1
        elif( ("(-)"+ name ) in dl ):
            return 1
        elif( ("(+)"+ name ) in rl ):
            return 1
        elif( ("(-)"+ name ) in rl ):
            return 1
        return 0
    #Attempt to add an included term
    def Include( self ):
        name_hopeful = self.entry_new.get()
        if( self.Name_Preexists( name_hopeful ) == 1 ):
            return  #failed
        new_term = Profile.Term( name_hopeful, "Include" )
        self.profile_list.append( new_term )    #append to profile_list
        dl = self.Make_Display_List( self.profile_list )    #update display box
        self.profile.setlist( dl )
        return
    #Attempt to add an excluded term
    def Exclude( self ):
        name_hopeful = self.entry_new.get()
        if( self.Name_Preexists( name_hopeful ) == 1 ):
            return  #failed
        new_term = Profile.Term( name_hopeful, "Exclude" )
        self.profile_list.append( new_term )    #append to profile_list
        dl = self.Make_Display_List( self.profile_list )    #update display box
        self.profile.setlist( dl )
        return
    #Close and cancel
    def Cancel(self,one=""):
        self.root.destroy()
        self.return_state = 0
        return
    #Close and confirm
    def Confirm(self,one=""):
        self.root.destroy()
        self.return_state = 1
        return
    #Transfer a selection from the included listbox to the removed listbox
    def Remove(self):
        to_remove = self.profile.getcurselection()
        pl = self.Make_Display_List( self.profile_list )
        for item in to_remove:
            index = pl.index( item )
            removed = self.profile_list.pop( index )
            self.remove_list.append( removed )
        #Update the listboxes
        pl = self.Make_Display_List( self.profile_list )
        self.profile.setlist( pl )
        rl = self.Make_Display_List( self.remove_list )
        self.removed.setlist( rl )
        return
    #Transer a selection from the removed listox to the included listbox
    def Unremove(self):
        to_remove = self.removed.getcurselection()
        rl = self.Make_Display_List( self.remove_list )
        for item in to_remove:
            index = rl.index( item )
            removed = self.remove_list.pop( index )
            self.profile_list.append( removed )
        #update lists
        pl = self.Make_Display_List( self.profile_list )
        self.profile.setlist( pl )
        rl = self.Make_Display_List( self.remove_list )
        self.removed.setlist( rl )
        return
    #Make the list of the terms in a displayable format
    def Make_Display_List( self, list ):
        display_names = []
        for item in list:
            display_names.append( item.Display_() )
        return display_names
    def Toggle( self ):
        to_remove = self.profile.getcurselection()
        if( len( to_remove ) <= 0 ):
            return
        for item in self.profile_list:
            if item.Display_() == to_remove[0]:
                item.Toggle_Type()
                break
        pl = self.Make_Display_List( self.profile_list )
        self.profile.setlist( pl )
            
    def Generate_Profile( self ):
        p = Profile.Profile("Name")
        p.term_list = self.profile_list
        return p
                
        