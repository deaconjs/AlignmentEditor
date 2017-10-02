from Tkinter import *
import Pmw

#This is a dialog that handles the organization of the profiles.
class DialogProfileAdjustment:
    def __init__(self, parent, profile_list, listbox_title, box_title = ""):
        self.profile_list = profile_list    #the actual list of profile names
        self.remove_list = []               #the actual list of removed names
        self.root = Pmw.Dialog(parent,buttons=('Confirm','Cancel'),defaultbutton='Confirm',command=self.Execute,title=box_title )
        
        self.top = self.root.interior()
        self.label_new = Label( self.top, text = "New Name" )

        entry_column = 0
    #Entry- input name of new profile
        self.label_new.grid(row=1,column=entry_column)
        self.entry_new = Entry( self.top )
        self.entry_new.grid(row=2,column=entry_column)
        self.initial_focus=self.entry_new
    #Add Button - place Entry's text into the Profiles Listbox
        self.button_add = Button(self.top,text="Add",command=self.Append)
        self.button_add.grid(row=3,column=entry_column,sticky="e,w")
    #Profiles Listbox - show the current profiles
        self.profile = Pmw.ScrolledListBox(self.top,labelpos='n',label_text=listbox_title)
        self.profile.setlist( self.profile_list )
        self.profile.grid(row = 0, column = 1, rowspan = 8)
    #Remove button - remove selection from Profiles listbox, place in removed listbox
        self.button_remove = Button(self.top,text=">Remove>",command=self.Remove)
        self.button_remove.grid(row = 1, column = 2,sticky="e,w")
    #Unremove button - remove selection from Removed listbox, place in Profiles listbox
        self.button_unremove = Button( self.top, text="<Keep<",command=self.Unremove)
        self.button_unremove.grid(row = 3, column = 2,sticky="e,w")

        self.removed = Pmw.ScrolledListBox(self.top, labelpos="n", label_text='Removed')
        self.removed.grid(row = 0, column = 3, rowspan = 8)
        
        self.return_state = 0   #tells the program what was the return state, 1-good 0-cancelled
        self.root.activate()
        #self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        return
#Called when any of the bottom buttons are hit
    def Execute(self, result):
        if(result=='Confirm'):
            self.Confirm()
        elif(result=='Cancel'):
            self.Cancel()
        elif(result==None):
            self.Cancel()
#Create a new profile from Entry's text
    def Append(self):
        name_hopeful = self.entry_new.get()
    #Check that name is not reserved or already exists
        exclude = ["","BASE"]
        if( name_hopeful in exclude ):
            return
        if( name_hopeful in self.profile_list ):
            return
        if( name_hopeful in self.remove_list ):
            return
    #Precondition: Name does not exist
        self.profile_list.append(name_hopeful)
        self.profile.setlist(self.profile_list)
        return
#Cancel the dialog session
    def Cancel(self,one=""):
        self.root.destroy()
        self.return_state = 0
        return
#Confirm the dialog session
    def Confirm(self,one=""):
        self.root.destroy()
        self.return_state = 1
        return
#Remove a profile from the Profile's listbox and place in removed listbox
    def Remove(self):
        to_remove = self.profile.getvalue()
        for item in to_remove:
            self.profile_list.remove(item)
            self.remove_list.append(item)
        self.profile.setlist( self.profile_list )
        self.removed.setlist( self.remove_list )
        return
#Remove a name from the Removed listbox and place in profiles listbox
    def Unremove(self):
        to_remove = self.removed.getvalue()
        for item in to_remove:
            self.remove_list.remove(item)
            self.profile_list.append(item)
        self.profile.setlist( self.profile_list )
        self.removed.setlist( self.remove_list )
        return
        
                
        