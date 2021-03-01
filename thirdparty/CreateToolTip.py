''' 
'''

try:
    # for Python2
    import Tkinter as tk
except ImportError:
    # for Python3
    import tkinter as tk


class CreateToolTip(object):
    '''
    create a tooltip for a given widget
    
    tk_ToolTip_class101.py
gives a Tkinter widget a tooltip as the mouse is above the widget
tested with Python27 and Python34  by  vegaseat  09sep2014

    * https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
    '''
    #Screen size
    scw = 0
    sch = 0
    tw = None
    
    def __init__(self, parent, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.scw = int(parent.winfo_screenwidth())
        self.sch = int(parent.winfo_screenheight())



    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        sch = int(self.widget.winfo_height())
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + sch
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background='yellow', relief='solid', borderwidth=1,
                       font=("times", "8", "normal"))
        label.pack(ipadx=1)



    def close(self, event=None):
        if self.tw:
            self.tw.destroy()
'''
# testing ...
if __name__ == '__main__':
    root = tk.Tk()

    btn1 = tk.Button(root, text="button 1")
    btn1.pack(padx=10, pady=5)
    button1_ttp = CreateToolTip(root, btn1, "mouse is over button 1")

    btn2 = tk.Button(root, text="button 2")
    btn2.pack(padx=10, pady=5)
    button2_ttp = CreateToolTip(root, btn2, "mouse is over button 2")

    root.mainloop()
'''