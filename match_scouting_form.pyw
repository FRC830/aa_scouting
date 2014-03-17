from tkinter import *
#values:
#match_num, team_num, auton_ball_num, auton_high, auton_low, teleop_high
#teleop_high_miss, teleop_low, teleop_low_speed  comments
class Application(Frame):
    """Application window for scouting sheet"""
    def __init__(self, master):
        """initialize the window"""
        Frame.__init__(self, master)
        self.grid()
        self.create_fields()
    def create_fields(self):
        """create input boxes and fields on the form"""
        #title
        Label(self, text = "(c) 2014 Colin Bott"
              ).grid(row=0, column=0, columnspan=2, sticky=W)
        #match_num input field
        Label(self, text="Match #:").grid(row=1, column=0, sticky=W)
        self.match_num = Entry(self)
        self.match_num.grid(row=1,column=1,sticky=W)
        #team_num input field
        Label(self, text="Team #:").grid(row=1, column=2)
        self.team_num = Entry(self)
        self.team_num.grid(row=1,column=3,sticky=W, columnspan=3)
        #auton_ball_num input field
        Label(self, text="Auton balls posessed:").grid(row=2, column=0, sticky=W)
        self.auton_ball_num = Entry(self)
        self.auton_ball_num.grid(row=2,column=1,sticky=W)
        #auton_high
        Label(self, text="Auton High Goal").grid(row=2, column=2)
        scoring_options=["N/A","Missed","Scored"]
        self.auton_high=StringVar()
        self.auton_high.set(None)
        col=3
        for val in scoring_options:
            Radiobutton(self, text = val, variable = self.auton_high, value=val
                        ).grid(row = 2, column=col, sticky=E)
            col+=1
        #auton_low
        Label(self, text="Auton Low Goal").grid(row=3, column=2)
        scoring_options=["N/A","Missed","Scored"]
        self.auton_low=StringVar()
        self.auton_low.set(None)
        col=3
        for val in scoring_options:
            Radiobutton(self, text = val, variable = self.auton_low, value=val
                        ).grid(row = 3, column=col, sticky=E)
            col+=1
        #teleop_high
        Label(self, text="Teleop High Goals:").grid(row=4, column=0, sticky=W)
        self.teleop_high = Entry(self)
        self.teleop_high.grid(row=4,column=1,sticky=W)       
        #teleop_high_miss
        Label(self, text="High Goals Missed:").grid(row=4, column=2, sticky=W)
        self.teleop_high_miss = Entry(self)
        self.teleop_high_miss.grid(row=4,column=3,sticky=W, columnspan=3)
        #teleop_low
        Label(self, text="Teleop Low Goals:").grid(row=5, column=0, sticky=W)
        self.teleop_low = Entry(self)
        self.teleop_low.grid(row=5,column=1,sticky=W)
        #teleop_low_speed
        Label(self, text="Teleop Low Goal Speed:").grid(row=6 , column=0,
                                                       columnspan=2, sticky=W)
        speed_options=["N/A", "Slow", "Medium", "Fast"]
        self.teleop_low_speed = StringVar()
        self.teleop_low_speed.set(None)
        col = 1
        for val in speed_options:
            Radiobutton(self, text=val, variable=self.teleop_low_speed, value=val
                        ).grid(row=6, column=col)
            col+=1

        #pass consistency
        Label(self, text = " ").grid(row=7, column=0, sticky=W)
        Label(self, text = "Pass Consistency").grid(row=8, column=0, sticky=W)
        Label(self, text = "N/A").grid(row=8, column=1, sticky=S)
        Label(self, text = "Inconsistent").grid(row=8, column=2, sticky=S)
        Label(self, text = "Consistent").grid(row=8, column=3, sticky=S)
        Label(self, text = "Over Truss").grid(row=9, column=0, sticky=W)
        Label(self, text = "Ranged Pass").grid(row=10, column=0, sticky=W)
        Label(self, text = " ").grid(row=11, column=0, sticky=W)
        
        #comments
        Label(self, text="Comments:").grid(row=15, column=0)
        self.comments=Entry(self)
        self.comments.grid(row=15, column=1)
        
root = Tk()
root.title("Aerial Assist Match Scouting Form")
app = Application(root)
root.mainloop()
