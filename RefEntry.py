#This class is a structure to hold the data of a sequence together

class Ref_Entry:
    def __init__( self, gi ):
        self.id = gi        #The gi number
        self.sq = ''        #The sq number
        self.header = ''    #The full header information
        self.title = ''     #Everything after the last '|'
    def Get_GI( self ):
        return self.id
    def Get_Header(self):
        return self.header
    def Get_Seq_Text(self):
        return self.sq
    def Get_Title(self):
        return self.title
    def Set_Header( self, header ):
        self.header = header
    def Set_Seq_Text( self, sq ):
        self.sq = sq
    def Set_Title( self, title ):
        self.title = title
        
