import tkinter as tk
import time
import random

base = tk.Tk()

size = (10, 5)
cell_size = 100
frame = 30
num_tap_avgs = 6

class Cell:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.mode = "expand"
        self.reverse = True

        self.c_x = x * cell_size + cell_size/2
        self.c_y = y * cell_size + cell_size/2

        self.active = True

        self.bbox = (self.c_x - cell_size/2, self.c_y - cell_size/2,
            self.c_x + cell_size/2, self.c_y + cell_size/2)

        self.ID = 0
        self.create_object()
        self.bkg_colour = "black"
        self.fore_colour = "white"
        self.colour = "white"
        self.flipped = False
        self.one_or_two = True

    def do_colours(self):
        if not self.flipped:
            self.fore_colour = self.colour
            self.bkg_colour = "black"
        else:
            self.fore_colour = "black"
            self.bkg_colour = self.colour

        self.canvas.itemconfigure(self.backgroundID, fill=self.bkg_colour)
        self.canvas.itemconfigure(self.ID, fill=self.fore_colour)

    def create_object(self):
        if self.ID:
            self.canvas.delete(self.ID) # clear old object

        self.backgroundID = self.canvas.create_oval(*self.bbox)

        if self.mode == "expand":
            self.ID = self.canvas.create_oval(*self.bbox)
        elif self.mode == "pie":
            self.ID = self.canvas.create_arc(*self.bbox, start=90, extent = 0)
        else:
            self.ID = self.canvas.create_oval(*self.bbox)

    def tick(self, phase): # phase is 0-1
        if self.reverse:
            phase = 1 - phase
        if self.mode == "expand":
            self.canvas.coords(self.ID, self.c_x - phase*cell_size/2, self.c_y - phase*cell_size/2,
                                self.c_x + phase*cell_size/2, self.c_y + phase*cell_size/2)
            self.canvas.itemconfigure(self.ID)
        elif self.mode == "pie":
            self.canvas.itemconfigure(self.ID, start=90, extent = - phase * 360)
        else:
            pass

    def beat(self):
        self.tick
        print("do we ever end up here?")

    def disable(self):
        self.canvas.itemconfig(self.ID, state="hidden")
        self.active = False
        self.canvas.itemconfigure(self.backgroundID, state="hidden")

    def enable(self):
        self.canvas.itemconfig(self.ID, state="")
        self.active = True
        self.canvas.itemconfigure(self.backgroundID, state="")

def clock():
    #return int(time.perf_counter_ns() // 10e5)
    return int(time.time()*1000)

def avg_interval(l):
    diffs = [l[i] - l[i+1] for i in range(0,len(l)-1)]
    #print(diffs)
    return int(sum(diffs)/len(diffs))

class Situation:

    def __init__(self):
        self.canvas = tk.Canvas(base, bg="black", height=size[1]*cell_size, width=size[0]*cell_size)
        self.canvas.pack()

        self.time = 0
        self.cells = []
        self.tempo = 5000
        self.last_taps = [-1000]
        self.beat_start_time = 0
        self.beat_counter = 0
        self.colour_mode = "odds"
        self.colour_one = "blue"
        self.colour_two = "red"
        self.pattern = "LCR"

        for x in range(0, size[0]):
            self.cells.append([])
            for y in range(0, size[1]):
                self.cells[x].append(Cell(self.canvas, x, y))

        self.beat(False)
        self.set_colours()

        self.setup_control()

    def set_cells(self):
        if self.pattern == "odds":
            for x, col in enumerate(self.cells):
                for y, cell in enumerate(col):
                    if (x+y+self.beat_counter)%2:
                        cell.enable()
                    else:
                        cell.disable()
        elif self.pattern == "RL":
            for x, col in enumerate(self.cells):
                if (x+self.beat_counter)%size[0] == 0:
                    [cell.enable() for cell in col]
                else:
                    [cell.disable() for cell in col]
        elif self.pattern == "LR":
            for x, col in enumerate(reversed(self.cells)):
                if (x+self.beat_counter)%size[0] == 0:
                    [cell.enable() for cell in col]
                else:
                    [cell.disable() for cell in col]
        elif self.pattern == "LCR":
            num = int((size[0]+1)//2)
            print(self.beat_counter%num)
            for col in self.cells:
                [cell.disable() for cell in col]
            [cell.enable() for cell in self.cells[self.beat_counter%num]]
            [cell.enable() for cell in self.cells[size[0]-1-self.beat_counter%num]]
        elif self.pattern == "rand1":
            for col in self.cells:
                for cell in col:
                    if random.random() > 0.90:
                        cell.enable()
                    else:
                        cell.disable()
        elif self.pattern == "rand2":
            for col in self.cells:
                for cell in col:
                    if random.random() > 0.75:
                        cell.enable()
                    else:
                        cell.disable()
        elif self.pattern == "rand3":
            for col in self.cells:
                for cell in col:
                    if random.random() > 0.50:
                        cell.enable()
                    else:
                        cell.disable()
        elif self.pattern == "down":
            for col in self.cells:
                for y, cell in enumerate(col):
                    if not (y+self.beat_counter)%size[1]:
                        cell.enable()
                    else:
                        cell.disable()
        elif self.pattern == "alt lr":
            for x, col in enumerate(self.cells):
                if x < size[0]/2:
                    if self.beat_counter%2:
                        [cell.enable() for cell in col]
                    else:
                        [cell.disable() for cell in col]
                else:
                    if self.beat_counter%2:
                        [cell.disable() for cell in col]
                    else:
                        [cell.enable() for cell in col]
        elif self.pattern == "alt tb":
            for col in self.cells:
                for y, cell in enumerate(col):
                    if y < size[1]/2:
                        if self.beat_counter%2:
                            cell.enable()
                        else:
                            cell.disable()
                    else:
                        if self.beat_counter%2:
                            cell.disable()
                        else:
                            cell.enable()
                    
        else:
            for row in self.cells:
                [cell.enable() for cell in row]

    def beat(self, auto):
        cl = clock()
        #print(self.tempo,cl - self.beat_start_time)
        lateness = 0
        
        if not auto and (cl - self.beat_start_time) < 70: #this prevents two beats firing when user taps just after the last automatic beat hit
            pass
        else:
            #following lines moved from the top of tap()
            if hasattr(self, 'tick_job'): # these ifs only fail right at the start of a run
                self.canvas.after_cancel(self.tick_job) # cancel current tick
            if hasattr(self, 'beat_job'):
                self.canvas.after_cancel(self.beat_job) # cancel current beat
        
            if auto: # if this beat was triggered automatically, let's calculate how late it was
                lateness = cl - self.beat_start_time - self.tempo

            self.beat_job = self.canvas.after(self.tempo - lateness,self.beat,True)
            self.beat_start_time = cl

            #make right cells active
            self.set_cells()
            
            self.animate()
            self.beat_counter += 1

    def animate(self): # this is a one shot function, it plays one animation then stops
        time = clock() - self.beat_start_time
        if time < self.tempo:
            for col in self.cells:
                for cell in col:
                    if cell.active:
                        cell.tick( time / self.tempo )
                    
            self.tick_job = self.canvas.after(frame, self.animate)
        else:
            print("animate else",time)

    def tap(self, params):
        # do tap tempo logic
        now = clock()
        if now - self.last_taps[0] < 2000: # adding to an already started series of taps
            self.last_taps.insert(0, now)
            self.tempo = avg_interval(self.last_taps)

            if len(self.last_taps) > num_tap_avgs + 1:
                self.last_taps.pop()

            #self.beat(False) # call new beat
        else: # starting a new tap after a while running automatically
            self.last_taps = [now]

        self.beat(False) # call new beat

    def set_colours(self):
        if self.colour_mode == "odds":
            for x, col in enumerate(self.cells):
                for y, cell in enumerate(col):
                    if (x+y)%2:
                        cell.colour = self.colour_one
                        cell.one_or_two = True
                    else:
                        cell.colour = self.colour_two
                        cell.one_or_two = False
        elif self.colour_mode == "rows":
            for col in self.cells:
                for y, cell in enumerate(col):
                    if y&2:
                        cell.colour = self.colour_one
                        cell.one_or_two = True
                    else:
                        cell.colour = self.colour_two
                        cell.one_or_two = False
        elif self.colour_mode == "cols":
            for x, col in enumerate(self.cells):
                if x%2:
                    for cell in col:
                        cell.colour=self.colour_one
                        cell.one_or_two = True
                else:
                    for cell in col:
                        cell.colour=self.colour_two
                        cell.one_or_two = False
        else:
            for col in self.cells:
                for cell in col:
                    cell.colour=self.colour_one
                    cell.one_or_two = True

        for col in self.cells:
            for cell in col:
                cell.do_colours()

    def set_pattern(self,pattern):
        self.pattern = pattern

    def set_spawn(self,spawn):
        for col in self.cells:
            for cell in col:
                cell.mode = spawn
                cell.create_object()

    def set_colour_mode(self,mode):
        self.colour_mode = mode
        self.set_colours()

    def set_colour_one(self,col):
        self.colour_one = col
        self.set_colours()

    def set_colour_two(self,col):
        self.colour_two = col
        self.set_colours()

    def flip_colour_one(self,*d):
        for col in self.cells:
            for cell in col:
                if cell.one_or_two:
                    cell.flipped = not cell.flipped

    def flip_colour_two(self,*d):
        for col in self.cells:
            for cell in col:
                if not cell.one_or_two:
                    cell.flipped = not cell.flipped

    def reverse_spawn(self,*d):
        for col in self.cells:
            for cell in col:
                cell.reverse = not cell.reverse

    def setup_control(self):
        self.control = tk.Toplevel(base)

        self.control.bind("<space>",self.tap)

        pattern = tk.Label(self.control, text="pattern").grid(row=0, column=0)
        all_    = tk.Button(self.control, text="all")
        all_.grid(row=1, column=0)
        all_.bind("<1>", lambda d:self.set_pattern("all"))
        
        p_odds  = tk.Button(self.control, text="odds/evens")
        p_odds.grid(row=2, column=0)
        p_odds.bind("<1>", lambda d:self.set_pattern("odds"))
        
        LR      = tk.Button(self.control, text="L to R")
        LR.grid(row=3, column=0)
        LR.bind("<1>", lambda d:self.set_pattern("LR"))
        
        RL      = tk.Button(self.control, text="R to L")
        RL.grid(row=4, column=0)
        RL.bind("<1>", lambda d:self.set_pattern("RL"))
        
        LCR     = tk.Button(self.control, text="in to centre")
        LCR.grid(row=5, column=0)
        LCR.bind("<1>", lambda d:self.set_pattern("LCR"))
        
        rand1  = tk.Button(self.control, text="random 10%")
        rand1.grid(row=6, column=0)
        rand1.bind("<1>", lambda d:self.set_pattern("rand1"))
        
        rand2  = tk.Button(self.control, text="random 25%")
        rand2.grid(row=7, column=0)
        rand2.bind("<1>", lambda d:self.set_pattern("rand2"))
        
        rand3  = tk.Button(self.control, text="random 50%")
        rand3.grid(row=8, column=0)
        rand3.bind("<1>", lambda d:self.set_pattern("rand3"))
        
        down  = tk.Button(self.control, text="top to bottom")
        down.grid(row=9, column=0)
        down.bind("<1>", lambda d:self.set_pattern("down"))
        
        down  = tk.Button(self.control, text="alternate L/R")
        down.grid(row=10, column=0)
        down.bind("<1>", lambda d:self.set_pattern("alt lr"))
        
        down  = tk.Button(self.control, text="alt. top/bottom")
        down.grid(row=11, column=0)
        down.bind("<1>", lambda d:self.set_pattern("alt tb"))


        
        spawn   = tk.Label(self.control, text="spawn").grid(row=0, column=1)
        on      = tk.Button(self.control, text="on")
        on.grid(row=1, column=1)
        on.bind("<1>", lambda d:self.set_spawn("on"))
        
        expand  = tk.Button(self.control, text="expand")
        expand.grid(row=2, column=1)
        expand.bind("<1>", lambda d:self.set_spawn("expand"))
        
        pie     = tk.Button(self.control, text="pie")
        pie.grid(row=3, column=1)
        pie.bind("<1>", lambda d:self.set_spawn("pie"))

        reverse_spawn = tk.Checkbutton(self.control, text="reverse")
        reverse_spawn.grid(row=4, column=1)
        reverse_spawn.bind("<1>", self.reverse_spawn)
        
        
        col_mode    = tk.Label(self.control, text="colour mode").grid(row=0, column=2)
        single      = tk.Button(self.control, text="single")
        single.grid(row=1, column=2)
        single.bind("<1>", lambda d:self.set_colour_mode("single"))
        
        c_odds      = tk.Button(self.control, text="odds/evens")
        c_odds.grid(row=2, column=2)
        c_odds.bind("<1>", lambda d:self.set_colour_mode("odds"))
        
        rows        = tk.Button(self.control, text="rows")
        rows.grid(row=3, column=2)
        rows.bind("<1>", lambda d:self.set_colour_mode("rows"))
        
        cols        = tk.Button(self.control, text="columns")
        cols.grid(row=4, column=2)
        cols.bind("<1>", lambda d:self.set_colour_mode("cols"))
        
        col_one     = tk.Label(self.control, text="colour one").grid(row=0, column=3)
        one_white   = tk.Button(self.control, text="white")
        one_white.grid(row=1, column=3)
        one_white.bind("<1>", lambda d:self.set_colour_one("white"))
        
        one_red     = tk.Button(self.control, text="red")
        one_red.grid(row=2, column=3)
        one_red.bind("<1>", lambda d:self.set_colour_one("red"))
        
        one_blue    = tk.Button(self.control, text="blue")
        one_blue.grid(row=3, column=3)
        one_blue.bind("<1>", lambda d:self.set_colour_one("blue"))

        flip_cols_butt = tk.Checkbutton(self.control, text="flip colours")
        flip_cols_butt.grid(row=5, column=3)
        flip_cols_butt.bind("<1>", self.flip_colour_one)
        
        col_two     = tk.Label(self.control, text="colour two").grid(row=0, column=4)
        two_white   = tk.Button(self.control, text="white")
        two_white.grid(row=1, column=4)
        two_white.bind("<1>", lambda d:self.set_colour_two("white"))
        
        two_red     = tk.Button(self.control, text="red")
        two_red.grid(row=2, column=4)
        two_red.bind("<1>", lambda d:self.set_colour_two("red"))
        
        two_blue    = tk.Button(self.control, text="blue")
        two_blue.grid(row=3, column=4)
        two_blue.bind("<1>", lambda d:self.set_colour_two("blue"))

        flip_cols_butt2 = tk.Checkbutton(self.control, text="flip colours")
        flip_cols_butt2.grid(row=5, column=4)
        flip_cols_butt2.bind("<1>", self.flip_colour_two)

        tk.Label(self.control, text="space for tap tempo").grid(row=6, column=2)


situ = Situation()
#base.bind("<space>",situ.tap)

base.mainloop()
