#This class is a holding class for storing information about
#positions where the tree should be drawn
class CanvasBox:
    def __init__( self, xorigin, yorigin, longx, delta_y, xtotal, order ):
        self.xorigin = xorigin  #x dimension origin
        self.yorigin = yorigin  #y dimension origin
        if(longx != 0):
            self.xtick = xtotal / longx #x dimension spacing
        else:
            self.xtick = 1
        self.xtotal = xtotal    #The relative end distance
        self.ytick = delta_y    #y dimension spacing
        self.order = order      #inorder, preorder, or postorder view
        self.longx = longx      #The real end distance
    #Function for storing a new longest branch distance.
    def New_XLong(self, xlong):
        self.longx = xlong
        if(xlong != 0):
            self.xtick = self.xtotal/xlong
        else:
            self.xtick = 1
        

