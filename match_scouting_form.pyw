import os
try:
    from Tkinter import *
except ImportError:
    from tkinter import *
#values:
#match_num, team_num, auton_ball_num, auton_high, auton_low, teleop_high
#teleop_high_miss, teleop_low, teleop_low_speed, ranged_pass
#truss_pass, fouls, tech_fouls, defense, truss_catch, range_catch, human_catch
#comments
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
        Label(self, text = " ").grid(row=11, column=0)
        pass_options = ["N/A", "Inconsistent", "Consistent"]
        #ranged_pass
        self.ranged_pass = StringVar()
        self.ranged_pass.set(None)
        col = 1
        for val in pass_options:
            Radiobutton(self, variable = self.ranged_pass, value = val
                        ).grid(row=10, column=col)
            col+=1
        #truss_pass
        self.truss_pass = StringVar()
        self.truss_pass.set(None)
        col = 1
        for val in pass_options:
            Radiobutton(self, variable = self.truss_pass, value = val
                        ).grid(row=9, column=col)
            col+=1
        #fouls
        Label(self, text="Fouls:").grid(row=12, column=0, sticky=E)
        self.fouls=Entry(self)
        self.fouls.grid(row=12, column=1, sticky=W)
        #tech_fouls
        Label(self, text="Technical Fouls:").grid(row=12, column=2, sticky=E)
        self.tech_fouls=Entry(self)
        self.tech_fouls.grid(row=12, column=3, sticky=W)
        Label(self, text = " ").grid(row=13, column=0)
        #defense
        Label(self, text="Defense:").grid(row=14, column=0, sticky=E)
        col=1
        defense_options = ["N/A", "Bad", "Mediocre", "Good"]
        self.defense = StringVar()
        self.defense.set(None)
        for val in defense_options:
            Radiobutton(self, variable=self.defense, value=val, text=val
                        ).grid(row=14, column=col)
            col+=1
        #catching: truss_catch, range_catch, human_catch
        Label(self, text="Catching:").grid(row=15, column=0, sticky=E)
        self.truss_catch = BooleanVar()
        self.range_catch = BooleanVar()
        self.human_catch = BooleanVar()
        Checkbutton(self, text="Truss", variable=self.truss_catch).grid(
            row=15, column=1, sticky=W)
        Checkbutton(self, text="Ranged", variable=self.range_catch).grid(
            row=16, column=1, sticky=W)
        Checkbutton(self, text="From Human", variable=self.human_catch).grid(
            row=17, column=1, sticky=W)
        #match_result
        Label(self, text="Match Result:").grid(row = 15, column=2, sticky=E)
        result_options = ["Win", "Loss", "Tie"]
        self.match_result = StringVar()
        self.match_result.set(None)
        row=15
        for val in result_options:
            Radiobutton(self, variable=self.match_result, value=val, text=val
                        ).grid(row=row, column=3, sticky=W)
            row+=1
        Label(self, text=" ").grid(row=18, column=0)
        #comments
        Label(self, text="Comments:").grid(row=19, column=0)
        self.comments = Text(self, width = 40, height=5, wrap=WORD,
                             background='#ffff00')
        self.comments.grid(row=19, column=1, columnspan=3, rowspan=2)
        #submit button
        Button(self, text="Submit Form", command = self.submit
               ).grid(row=20, column=4, sticky=E)

    def submit(self):
        """Read values from scouting form and save to a file"""
        coms = self.comments.get("0.0", END)
        match = self.match_num.get()
        team = self.team_num.get()
        auton_ball = self.auton_ball_num.get()
        auton_high = self.auton_high.get()
        auton_low = self.auton_low.get()
        data = [match+"\n",
                auton_ball+"\n",
                auton_high+"\n",
                auton_low+"\n",
                coms]
        #clear entries
        self.comments.delete("0.0", END)
        self.match_num.delete("0", END)
        self.team_num.delete("0", END)
        self.auton_ball_num.delete("0", END)
        self.auton_high.set("N/A")
        self.auton_low.set("N/A")
        #filename should be like 830_data.txt
        filename = os.path.join('data', team + "_data.txt")
        #this will create the file if it doesnt exist
        a=open(filename,"w")
        #write the latest data
        a.writelines(data)
        a.close()

    
root = Tk()
root.title("Aerial Assist Match Scouting Form")
app = Application(root)
root.mainloop()
