from tkinter import *
from webbrowser import open_new
from threading import Thread
import random

def main():
    #  The main loop in a separate process.
    def action():
        if pause:
            return
        global speed, flagmove
        flagmove = 1
        move()
        if flagmove == 0:
            cv.addtag_withtag('stop', 'figure')
            cv.itemconfigure('figure', width=3, outline='gray50')
            cv.dtag('figure')
            cv.dtag('pivot')
            delrow()
            newfigure()
            cv.update()
        cv.after(speed, action)
    
    #  Processes pressed buttons. The periodic downward movement does the same.
    def move(route='Down'):
        if route == 'Down':
            cv.move('figure', 0, size)
            if check(route):
                cv.move('figure', 0, -size)
        if route == 'Up':
            rotation(route)
        if route == 'Left':
            cv.move('figure', -size, 0)
            if check(route):
                cv.move('figure', size, 0)
        elif route == 'Right':
            cv.move('figure', size, 0)
            if check(route):
                cv.move('figure', -size, 0)
        cv.update()
        
    # The function fixes impossible positions and,
    #                    in case of an error, returns 'True'   
    def check(route):
        global flagmove
        flag = 0
        for j in cv.find_withtag('figure'):
            for i in cv.find_withtag('stop'):
                if cv.coords(j) == cv.coords(i):
                    flagmove = 0
                    return True 
            if 1 < cv.coords(j)[0] < 274 and cv.coords(j)[1] < 573:
                flag += 1
            if flag == 4:
                return
        if route == 'Down':
            flagmove = 0
        else:
            flagmove = 1
        return True
    
    #  We rotate the figures. In case of errors, we cancel the rotation.
    def rotation(route):
        if cv.coords(cv.find_withtag('pivot')) == []: # Do not rotate the square
            return
        x1, y1, x2, y2 = cv.coords(cv.find_withtag('pivot'))
        for j in cv.find_withtag('figure'):
            xt, yt, x2, y2 = cv.coords(j)
            cv.move(j, (x1 - xt) + (y1 - yt), (y1 - yt) - (x1 - xt))
        if check(route):
            for i in cv.find_withtag('figure'):
                xt, yt, x2, y2 = cv.coords(i)
                cv.move(i, (x1 - xt) - (y1 - yt), (y1 - yt) + (x1 - xt))
                
    #  Clean up the collected rows with progressive scoring.
    #  one row - 100 points, 2 rows - 300 points, 3 - 700 , 4  - 1500 
    def delrow():
        global score, speed
        rowline = 100
        for i in ylist:
            line = 0
            for t in cv.find_withtag('stop'):
                if cv.coords(t)[1] == i:
                    cv.addtag_withtag('test', t)
                    cv.addtag_withtag('up', t)
                    line += 1
            if line == 10:
                score += rowline
                rowline *= 2
                speed -= 1
                lab3['text'] = score
                cv.delete('test')
                cv.move('up', 0, size)
            cv.dtag('test')
        cv.dtag('up')
        
    #  Shape creation function.
    def newfigure():
        global colorlist, newcolor, nextfigure
        x, y = 123, 2
        cv2.delete('all')
        figurelist =(((0,30),(0,0),(30,0),(30,30)),((0,30),(0,0),(30,30),(30,60)),
                 ((0,30),(30,0),(30,30),(0,60)),((0,30),(0,0),(0,60),(30,60)),
                 ((0,30),(0,0),(0,60),(-30,60)),((0,30),(0,0),(0,60),(30,30)),
                 ((0,30),(0,0),(0,60),(0,90)))
        # Choosing a random, non-repeating color for the shapes.
        while True:
            color = newcolor
            newcolor = random.randint(0, 8)
            if color != newcolor:
                break
        firstfigure = nextfigure
        nextfigure = random.randint(0, 6)
        #  Create a shape with a pivot point.
        for nx, ny in figurelist[firstfigure]:
            cv.create_rectangle(x+nx, y+ny, x+nx+size, y+ny+size, tag='figure',
                                fill=colorlist[color], width=2, outline='gray25')
            if nx == 0 and ny == 30 and firstfigure != 0:
                cv.addtag_withtag('pivot', 'figure')
        #  Draw the next shape
        for nx, ny in figurelist[nextfigure]:
            cv2.create_rectangle(nx/3 + 16, ny/3 + 6, nx/3 + 26, ny/3 + 16,
                                 fill=colorlist[newcolor])
        #  Determine the moment of loss.
        if check('Down'):
            print('Game over!  Score: ' + str(score))
            gameover()
        cv2.update()
        
    #  We read the record file, in case of its absence we create.
    def readrecord():
        try:
            with open('record.txt', 'r') as text:
                temp = text.read()
            if temp != '':
                rec = int(temp)
            else:
                rec = 0
        except FileNotFoundError:
            with open('record.txt', 'w') as text:
                rec = 0
        return rec
    
    #  Preparing the game completion menu and showing the frame.
    def gameover():
        global pause, score
        pause = True
        rec = readrecord()
        if rec <= score:
            with open('record.txt', 'w') as text:
                text.write(str(score))
            rec = score
            lab5.configure(text ='New record!!', fg='red')
        else:
            lab5.configure(text ='Game over!', fg='black')
        lab6.configure(text='You score: ' + str(score) + '\nGame record: '
                       + str(rec), font="Arial 11")
        frame1.pack(side='top', expand=17)
           
    #   Clears game data, starts a new game
    def newgame():
        global score, speed, pause
        speed = 400
        lab3['text'] = score = 0
        cv2.delete('all')
        cv.delete('stop', 'figure')
        pause = False
        frame1.pack_forget()
        action()
        
    #  For the "exit" button
    def gamedestroy():
        root.destroy()
        print('Stop programm.')
        
    #  Right-click menu.  You can dock the game on top of other windows.
    def about(event):
        menu2 = Menu(tearoff=False, font="Arial 12")
        menu2.add_radiobutton(label="Pin on",
                              command=lambda: root.attributes("-topmost", True))
        menu2.add_radiobutton(label="Pin off",
                              command=lambda: root.attributes("-topmost", False))
        menu2.add_separator()
        menu2.add_command(label="About", command=dialog)
        menu2.post(event.x_root, event.y_root)
   
   # Right-click dialog      
    def dialog():
        global aboutflag
        def destroy_about_window():
            global aboutflag
            win.destroy()
            aboutflag = False

        def callback(blank=None):
            open_new(r"https://github.com/chicory-ru")
            destroy_about_window()
            
        #  A deeply hidden function to reset the record :)
        def norec():
            with open('record.txt', 'w') as text:
                text.write('0')
            clearecord.config(state='disable')
        
        if not aboutflag:
            win = Toplevel(bg="light gray", bd=7, relief="ridge")  # About.
            win.geometry(f"280x170+{650}+{400}")
            win.title("About")
            win.minsize(width=250, height=110)
            win.resizable(width=False, height=False)
            win.attributes("-topmost", True)
            win.overrideredirect(True)
            ok = Button(win, text='OK', font="Arial 10",
                        command=destroy_about_window, width=9, bd=3)
            ok.pack(side=BOTTOM, padx=10, pady=10)
            version = Label(win, text="Simple tetris v.1.0", font="Arial 14",
                            bg="light gray")
            version.pack(padx=9, pady=9)
            link = Label(win, text="github", fg="blue",
                         cursor="hand2", font="Arial 12", bg="light gray")
            link.pack()
            link.bind("<Button-1>", callback)
            clearecord = Checkbutton(win, text='reset record', font="Arial 7",
                                command=norec, width=20, bd=3,
                                bg="light gray")
            clearecord.pack(padx=1, pady=1)
            aboutflag = True
    
    # Call functions by pressing keyboard buttons.       
    def movebind(event):
        key = event.keysym
        #print(key)
        try:
            if key == 'Return' and frame1.pack_info():
                newgame()
            if key in ('Left', 'Right', 'Up', 'Down'):
                move(key)
        except TclError:  #  Don't even ask about it :)
            pass  
        
    #  Speed up the game by pressing the on-screen button 'Down'.        
    def speedup(blank=None):
        global speed
        speed = 50
              
    def speeddown(blank=None):
        global  speed
        speed = 500
    
    root = Tk()
    root.title("Simple tetris")
    root.geometry("330x710+100+100")
    root.resizable(width=False, height=False)
    root.bind('<Button-3>', about)
    root.bind('<KeyPress>', movebind)
    
    cv = Canvas(width=302, height=602, bg='grey85')  # Main canvas
    cv2 = Canvas(width=64, height=46)   #  Preview canvas
    cv2.place(x=250, y=0)
    cv.place(x=12, y=50)
    
    #  Draw the grid.
    for x in range(3, 303, 30):
        for y in range (3, 603, 30):
            cv.create_rectangle(x, y, x+30, y+30, outline='gray70', width=2)
    
    b1 = Button(root, text='Left ←', font="Arial 11", width=6, relief=RIDGE,
                bd=4, bg='light blue', command=lambda: move('Left'))
    b2 = Button(root, text='Down ↓', font="Arial 11", width=6, relief=RIDGE,
                bd=4, bg='light green')
    b3 = Button(root, text='Right →', font="Arial 11", width=6, relief=RIDGE,
                bd=4, bg='light yellow', command=lambda: move('Right'))
    b4 = Button(root, text='Turn ↑', font="Arial 11", width=6, relief=RIDGE,
                bd=4, bg='light salmon', command=lambda: move('Up'))
    
    b2.bind('<ButtonPress-1>', speedup)
    b2.bind('<ButtonRelease-1>', speeddown)
    
    b1.place(x=6, y=662)
    b3.place(x=246, y=662)
    b2.place(x=86, y=662)
    b4.place(x=166, y=662)
    
    lab = Label(text='Next:', font="Arial 12")
    lab2 = Label(text='Score:', font="Arial 12")
    lab3 = Label(text=str(score), font="Arial 17", fg='blue')
    lab.place(x=200, y=14)
    lab2.place(x=10, y=14)
    lab3.place(x=75, y=10)
    
    #  Start menu
    frame1 = Frame(root, width=420, height=500)
    lab4 = Label(frame1, bd=14, relief=SUNKEN)
    lab5 = Label(lab4, text='New game', font="Arial 22", fg='blue')
    lab6 = Label(lab4, text='You score: ' + str(score) + '\nGame record: '
                 + str(readrecord()), font="Arial 11",  height=3)
    b5 = Button(lab4, text='Start new game', font="Arial 12", width=15,
                relief=RIDGE, bd=4, bg='light green', command=newgame)
    b6 = Button(lab4, text='Exit', font="Arial 12", width=15, relief=RIDGE,
                bd=4, bg='light salmon', command=gamedestroy)
    
    frame1.pack(side='top', expand=17)
    lab4.pack()
    lab5.pack()
    lab6.pack(side='top', expand=19)
    b5.pack()
    b6.pack()

    #  Second stream.
    th = Thread(target=action, args=())
    th.start()
    
    root.mainloop()
    
if __name__ == "__main__":
    
    #   Global data.
    aboutflag = False                                 
    pause = True                         
    speed = 400                            
    score = 0                            
    size = 30                              
    newcolor = random.randint(0, 8)
    flagmove = 0
    nextfigure = random.randint(0, 6)
    ylist = [j for j in range(32, 602, 30)]
    colorlist = ('SpringGreen3', 'cyan', 'gold', 'brown2', 'coral2',
             'deep sky blue', 'OliveDrab3', 'maroon2', 'purple1')
    main()
