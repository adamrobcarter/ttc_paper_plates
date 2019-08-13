import tkinter as tk
import time

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

        if self.mode == "expand":
            self.ID = self.canvas.create_oval(*self.bbox, fill="white")
        elif self.mode == "pie":
            self.ID = self.canvas.create_arc(*self.bbox, start=90, extent = 0, fill="white")

    def tick(self, phase): # phase is 0-1
        if self.reverse:
            phase = 1 - phase
        if self.mode == "expand":
            self.canvas.coords(self.ID, self.c_x - phase*cell_size/2, self.c_y - phase*cell_size/2,
                                self.c_x + phase*cell_size/2, self.c_y + phase*cell_size/2)
        elif self.mode == "pie":
            self.canvas.itemconfigure(self.ID, start=90, extent = - phase * 360)

    def beat(self):
        self.tick

    def disable(self):
        self.canvas.itemconfig(self.ID, fill="black")
        self.active = False

    def enable(self):
        self.canvas.itemconfig(self.ID, fill="white")
        self.active = True

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

        for x in range(0, size[0]):
            self.cells.append([])
            for y in range(0, size[1]):
                self.cells[x].append(Cell(self.canvas, x, y))

        self.beat(False)

    def set_cells(self):
        pattern = "LCR"
        if pattern == "odds":
            for x, col in enumerate(self.cells):
                for y, cell in enumerate(col):
                    if (x+y+self.beat_counter)%2:
                        cell.enable()
                    else:
                        cell.disable()
        elif pattern == "RL":
            for x, col in enumerate(self.cells):
                if (x+self.beat_counter)%size[0] == 0:
                    [cell.enable() for cell in col]
                else:
                    [cell.disable() for cell in col]
        elif pattern == "LR":
            for x, col in enumerate(self.cells.reverse()):
                if (x+self.beat_counter)%size[0] == 0:
                    [cell.enable() for cell in col]
                else:
                    [cell.disable() for cell in col]
        elif pattern == "LCR":
            num = int((size[0]+1)//2)
            print(self.beat_counter%num)
            for col in self.cells:
                [cell.disable() for cell in col]
            [cell.enable() for cell in self.cells[self.beat_counter%num]]
            [cell.enable() for cell in self.cells[size[0]-1-self.beat_counter%num]]
        else:
            for row in self.cells:
                [cell.enable() for cell in row]

    def beat(self, auto):
        cl = clock()
        #print(self.tempo,cl - self.beat_start_time)
        lateness = 0
        
        if not auto and (cl - self.beat_start_time) < 70: #this prevents two beats firing when user taps just after the last automatic beat hit
            print(cl - self.beat_start_time)
        else:
            if auto:
                lateness = cl - self.beat_start_time - self.tempo
                #print(lateness)
            self.beat_job = self.canvas.after(self.tempo - lateness,self.beat,True)
            self.beat_start_time = cl


            #make right cells active
            self.set_cells()
            
            self.animate()
            self.beat_counter += 1

    def animate(self):
        time = clock() - self.beat_start_time
        if time < self.tempo:
            for col in self.cells:
                for cell in col:
                    if cell.active:
                        cell.tick( time / self.tempo )
                    
            self.tick_job = self.canvas.after(frame, self.animate)

    def tap(self, params):
        self.canvas.after_cancel(self.tick_job) # cancel current tick
        self.canvas.after_cancel(self.beat_job) # cancel current beat

        # do tap tempo logic
        now = clock()
        if now - self.last_taps[0] < 2000: # adding to an already started series of taps
            self.last_taps.insert(0, now)
            self.tempo = avg_interval(self.last_taps)

            if len(self.last_taps) > num_tap_avgs + 1:
                self.last_taps.pop()

            self.beat(False) # call new beat
        else:
            self.last_taps = [now]

situ = Situation()
base.bind("<space>",situ.tap)

base.mainloop()
