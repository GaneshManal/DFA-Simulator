from Tkinter import *
from dfa_logic import DFA
import sys

if sys.version_info<(3,0,0):
    python3= False
    import tkMessageBox
else:
    python3= True
    from tkinter import messagebox
    
pop_in = None
SUPPORT_SIZE = 6
TRACE = False
eventInstance = None

class PopupWindow(object):

    def __init__(self, master):
        top = self.top = Toplevel(master)
        self.l = Label(top, text="Label Name")
        self.l.pack()
        self.e = Entry(top)
        self.e.pack()
        self.b = Button(top, text='Ok', command=self.cleanup)
        self.b.pack()

    def cleanup(self):
        global pop_in
        pop_in = self.e.get()
        self.top.destroy()


class DFAApplication:

    def __init__(self, parent=None):
        self.type, self.vertex_iter = 'vertex', 1
        self.master = Tk()
        self.master.title('DFA Simulator')

        self.graph_details, self.state_table_matrix = {}, []
        self.graph_json = dict()
        self.node_count, self.edge_count, self.label_count, self.curve_count = 0, 0, 0, 0
        self.tableTextMapping = {}
        self.clear_canvas_graph()

        tool_frame = Frame(width=800, height=200, bg="black", pady=5, colormap="new")
        self.button2 = Button(tool_frame, text='Vertex', width=15, height=2, command=self.drawVertex)
        self.button2.pack(side='left')
        self.button1 = Button(tool_frame, text='Edge', width=15, height=2, command=self.drawEdge)
        self.button1.pack(side='left')
        self.button4 = Button(tool_frame, text='Curve', width=15, height=2, command=self.drawCurve)
        self.button4.pack(side='left')
        self.button3 = Button(tool_frame, text='Label', width=15, height=2, command=self.writeText)
        self.button3.pack(side='left')
        self.button5 = Button(tool_frame, text='Clear', width=15, height=2, command=self.onClear)
        self.button5.pack(side='left')
        self.button6 = Button(tool_frame, text='Undo', width=15, height=2, command=self.undoHandler)
        self.button6.pack(side='left')
        self.button7 = Button(tool_frame, text='Help', width=15, height=2, command=self.create_help_window)
        self.button7.pack(side='left')
        tool_frame.pack(side='top')

        draw_frame = Frame(width=800, height=300, bg="white", colormap="new")
        self.canvas = Canvas(draw_frame, width=580, height=300, bg='white')
        # self.canvas.create_arc(100, 100, 200, 200, extent=180, style=ARC)
        self.canvas.pack(side='left')

        # this data is used to keep track of an 
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None, "oldPosCoords":None}

        self.canvas.bind('<ButtonPress-1>', self.onStart)
        self.canvas.bind('<ButtonRelease-1>', self.onRelease)
        self.canvas.bind('<B1-Motion>', self.onGrow)
        self.canvas.bind('<ButtonPress-2>', self.onDeleteSelectedItem)
        #self.canvas.bind('<ButtonPress-3>', self.onMove)
        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-3>", self.onDragStart)
        self.canvas.tag_bind("token", "<ButtonRelease-3>", self.onDragComplete)
        self.canvas.tag_bind("token", "<B3-Motion>", self.onDragMotion)
        
        self.state_table = Frame(draw_frame, width=220, height=300, colormap="new")
        '''
        self.startLabel = Label(self.state_table, text='Start State:', width=10)
        self.startLabel.pack(padx=10, pady=10)
        self.startEntry = Entry(self.state_table, width=32)
        self.startEntry.pack(padx=10, pady=10)

        self.acceptLabel = Label(self.state_table, text='Accept String:', width=10)
        self.acceptLabel.pack(padx=10, pady=10)
        self.acceptEntry = Entry(self.state_table, width=32)
        self.acceptEntry.pack(padx=10, pady=10)
        '''
        self.state_table.pack(side='left')
        draw_frame.pack(side='top')

        input_frame = Frame(width=800, bg="grey")
        self.inputLabel = Label(input_frame, text='Input String:', width=18, height=3, bg='Green')
        self.inputLabel.pack(side=LEFT, padx=1, pady=1)

        # self.inputEntry = Entry(input_frame, width=50)
        # self.inputEntry.pack(side=LEFT, padx=10, pady=1)
        self.input_entry = StringVar()
        self.inputEntry = Entry(input_frame, width=50, textvariable=self.input_entry)
        self.inputEntry.pack(side=LEFT, padx=10, pady=1)

        self.btnValidate = Button(input_frame, text='Validate', command=self.onValidate, width=20, height=3)
        self.btnValidate.pack(side=LEFT, padx=10, pady=1)

        self.btnClear = Button(input_frame, text='Clear Log', command=self.logClear, width=20, height=3)
        self.btnClear.pack(side=RIGHT, padx=10, pady=1)
        input_frame.pack(side='top', padx=1)

        log_frame = Frame(width=800, height=200, bg="black")
        logLabel = Label(log_frame, text='Log (String Traversal): ', width=18, height=2, fg='white', bg='black')
        logLabel.pack(side=TOP, anchor=W)
        self.text = Text(log_frame, width=100, height=10)
        self.text.insert(INSERT, "Hello, Logs will be printed here.")
        self.text.insert(END, "\n\n\nBye Bye.....\nACCEPTED\nREJECTED")
        self.text.tag_add("ACCEPTED", "5.0", "5.9")
        self.text.tag_add("REJECTED", "6.0", "6.8")
        self.text.tag_config("ACCEPTED", background="green", foreground="black")
        self.text.tag_config("REJECTED", background="RED", foreground="black")
        self.text.pack()
        log_frame.pack(side=LEFT, padx=10, pady=1)
        # log_frame.pack(side='top', padx=5)

        self.drawn = None
        self.kinds, self.shape = None, None
        
    def create_help_window(self):
        root = Tk()
        root.wm_title("Help")
        T = Text(root, height=30, width=100)
        T.tag_config("HELP", background="RED", foreground="black")
        T.insert(END, "\
    DFA Simulator\n\
    ===============\n\
    This python program allows you to design Deterministic Finite Automata graphically and\n\
    simulate them.The DFA simulator makes it easy to design deterministic finite automata.\n\
    Its graphical editor provides an easy to use interface and a context help. The simulation\n\
    function shows the steps graphically and helps to understand the way these state machines work.\n\n\
    COMMANDS:\n\n\
    Mouse Click-\n\
    -------------\n\
    Left Mouse click(single click) 	 - Draw selected component\n\
    Middle Mouse click(single click) - Delete the mouse cursor component\n\
    Right Mouse click(press, drag, release) - Drag and drop selected component\n\n\
    Button help-\n\
    --------------\n\
    Vertex/Edge/Curve/Label- select to draw respective component\n\
    Clear - To Clear the everthing drawn on canvas\n\
    Undo  - To undo the last drawn component(not available for edge/curve component)\n\
    Help  - To get the help about DFA \n")
        T.pack(expand=True)
        
    def onDragStart(self, event):
        #record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        vertexCoords = self.canvas.coords(self._drag_data["item"])
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["oldPosCoords"] = vertexCoords


    def onDragComplete(self, event):
        #update graph json and reset the drag information
        item = self._drag_data["item"]
        vertexCoords = self.canvas.coords(item)
        oldPosCoords = self._drag_data["oldPosCoords"]
        
        for x_node in self.graph_details['nodes']:
                    if x_node['x1'] == int(oldPosCoords[0]) and x_node['y1'] == int(oldPosCoords[1]) and x_node['x2'] == int(oldPosCoords[2]) and x_node['y2'] == int(oldPosCoords[3]):
                        node_id = x_node['id']
                        node_label = None
                        if 'label' in x_node:
                            node_label = x_node['label']
                        self.graph_details['nodes'].remove(x_node)
                        xCoord = int(vertexCoords[0])
                        yCoord = int(vertexCoords[1])
                        if node_label not in self.graph_json['states']:
                            self.graph_details['nodes'].append({'id': node_id, 'x1': xCoord, 'y1': yCoord, 'x2': xCoord + 60, 'y2': yCoord + 60})
                        else:
                            self.graph_details['nodes'].append({'id': node_id, 'x1': xCoord, 'y1': yCoord, 'x2': xCoord + 60, 'y2': yCoord + 60, 'label': node_label})
                        break

        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self._drag_data["oldPosCoords"] = None

    def onDragMotion(self, event):
        # Handle dragging of an object
        # compute how much this object has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def clear_canvas_graph(self):
        self.graph_details = dict()
        self.graph_details['nodes'] = []
        self.graph_details['edges'] = []
        self.graph_details['curves'] = []
        self.graph_details['labels'] = []

        self.graph_json = dict()
        self.graph_json['states'] = []
        self.graph_json['alphabet'] = []
        self.graph_json['transitions'] = {}
        self.graph_json['start'] = ''
        self.graph_json['accept'] = []

        self.state_table_matrix = []
        for x in range(SUPPORT_SIZE):
            self.state_table_matrix.append([None for x in range(SUPPORT_SIZE)])
        self.tableTextMapping = {}

    def drawEdge(self):
        self.type = 'edge'

    def drawVertex(self):
        self.type = 'vertex'

    def writeText(self):
        self.type = 'text'

    def drawCurve(self):
        self.type = 'curve'

    def onValidate(self):
        # Read START & ACCEPT State and validate the DFA
        input_str = self.input_entry.get()
        self.graph_json['start'] = self.start_entry.get()
        self.graph_json['accept'] = self.accept_entry.get().split(',')

        logs = []
        dfa_instructions = DFA(self.graph_json)
        logs = dfa_instructions.run_dfa(input_str)
        print( "DFA OUTPUT:", logs)
        last_line_no = len(logs)
        self.logClear()

        if len(logs) == 0:
            logs.append("DFA REJECTED: In-valid Input String or States.")
        for line in logs:
            self.text.insert(END, line)

            if 'ACCEPTED' in line:
                self.text.tag_add("ACCEPTED", (last_line_no + 0.4), (last_line_no + 0.12))
                self.text.tag_config("ACCEPTED", background="green", foreground="black")

            if 'REJECTED' in line:
                self.text.tag_add("REJECTED", (last_line_no + 0.4), (last_line_no + 0.12))
                self.text.tag_config("REJECTED", background="red", foreground="black")

    def onRelease(self, event):
        global eventInstance
        eventInstance = event
        self.button6.config(state=ACTIVE)
        if self.drawn and self.type in ['edge', 'curve']:
            self.button6.config(state=DISABLED)
            self.edge_count += 1
            lbl_name = PopupWindow(self.master)
            self.master.wait_window(lbl_name.top)
            global pop_in
            self.graph_details['edges'].append({'id': self.edge_count, 'x1': self.start.x, 'y1': self.start.y, 'x2': event.x, 'y2': event.y})
            obj = self.canvas.create_text((self.start.x+event.x)/2, -10 + (self.start.y+event.y)/2, text=pop_in, fill='red', tags = "token")

            if pop_in not in self.graph_json['alphabet']:
                self.graph_json['alphabet'].append(pop_in)

            row, column = 0, 0
            source, dest = "", ""
            key = str((self.start.x+event.x)/2) + "," + str(-10 + (self.start.y+event.y)/2)
            for x_node in self.graph_details['nodes']:
                if (self.start.x >= x_node['x1']) and (self.start.x <= x_node['x2']):
                    if (self.start.y >= x_node['y1']) and (self.start.y <= x_node['y2']):
                        row, source = x_node['id'], x_node['label']

                if self.type == 'edge':
                    if (event.x >= x_node['x1']) and (event.x <= x_node['x2']):
                        if (event.y >= x_node['y1']) and (event.y <= x_node['y2']):
                            column, dest = x_node['id'], x_node['label']

            if pop_in:
                if source not in self.graph_json['transitions'].keys():
                    self.graph_json['transitions'][source] = {}

                if self.type == 'edge':
                    self.state_table_matrix[row-1][column-1] = pop_in
                    self.tableTextMapping[key] = str(row) + "," + str(column)
                    if dest != "":
                        if ',' in pop_in:
                            for item in pop_in.split(','):
                                self.graph_json['transitions'][source][item] = dest
                        else:
                            self.graph_json['transitions'][source][pop_in] = dest
                    else:
                        print( "onRelease:transition not provided along with edge")

                if self.type == 'curve':
                    self.state_table_matrix[row-1][row-1] = pop_in
                    self.tableTextMapping[key] = str(row) + "," + str(row)
                    if ',' in pop_in:
                        for item in pop_in.split(','):
                            self.graph_json['transitions'][source][item] = source
                    else:
                        self.graph_json['transitions'][source][pop_in] = source
                
        if self.drawn and self.type == 'vertex':
            self.button6.config(state=ACTIVE)
            if self.node_count < 6:
                self.node_count += 1
                self.graph_details['nodes'].append({'id': self.node_count, 'x1': self.start.x, 'y1': self.start.y, 'x2': self.start.x+60, 'y2': self.start.y+60})
            else:
                print( "Vertex limit has reached:", self.node_count)

        if self.drawn and self.type == 'text':
            self.button6.config(state=ACTIVE)
            self.label_count += 1
            self.graph_details['labels'].append({'id': self.label_count, 'x1': self.start.x, 'y1': self.start.y, 'x2': event.x, 'y2': event.y})

            for x_node in self.graph_details['nodes']:
                if (self.start.x >= x_node['x1']) and (self.start.x <= x_node['x2']):
                    if (self.start.y >= x_node['y1']) and (self.start.y <= x_node['y2']):
                        state_name = 'Q' + str(self.vertex_iter)
                        if state_name not in self.graph_json['states']:
                            self.graph_json['states'].append(state_name)
                            x_node['label'] = state_name

            self.vertex_iter += 1

        separateLabel = Label(self.state_table, text='-' * 30)
        separateLabel.grid(row=0, column=0, columnspan=6)

        transLabel = Label(self.state_table, text='Transition Table:')
        transLabel.grid(row=1, column=0, columnspan=6)
        self.drawTable()
        print( "onRelease:graph_json:", self.graph_json)

    def onStart(self, event):
        self.shape = self.kinds
        self.start = event
        self.drawn = None

    def onGrow(self, event):
        self.canvas = event.widget
        obj = None
        if self.drawn:
            self.canvas.delete(self.drawn)

        if self.type == 'edge':
            obj = self.canvas.create_line(self.start.x, self.start.y, event.x, event.y, fill='black', width=3, arrow=LAST, smooth=True, tags="token")

        elif self.type == 'vertex':
            # objectId = self.shape(self.start.x, self.start.y, self.start.x + 10, self.start.y + 10)
            if self.node_count < 6:
                obj = self.canvas.create_oval(self.start.x, self.start.y, self.start.x+60, self.start.y+60, fill='pink', tags="token")
            else:
                if python3 == True:
                    messagebox.showerror("Vertex Limit Reached", "There is a limit of 6 vertices.")
                else:
                    tkMessageBox.showerror("Vertex Limit Reached", "There is a limit of 6 vertices.")

            '''
            e = Entry(self.master, width=50)
            e.pack()
            print e.get()
            '''

        elif self.type == 'text':
            # objectId = self.shape(self.start.x, self.start.y, self.start.x + 10, self.start.y + 10)
            obj = self.canvas.create_text(self.start.x, self.start.y, text='Q' + str(self.vertex_iter), tags="token")

        elif self.type == 'curve':
            # objectId = self.shape(self.start.x, self.start.y, self.start.x + 10, self.start.y + 10)
            obj = self.canvas.create_arc(self.start.x, self.start.y, event.x, event.y, extent=350, width=3, style=ARC, fill='black', tags="token")

        else:
            pass

        if TRACE:
            print obj

        if obj != None:
            self.drawn = obj

    def onClear(self, event=None):
        self.node_count, self.edge_count, self.label_count, self.curve_count = 0, 0, 0, 0
        allItems = self.canvas.find_all()
        for i in allItems:  # delete all the items on the canvas
            self.canvas.delete(i)
        self.clear_canvas_graph()
        self.vertex_iter = 1
        self.node_count = 0
        self.drawTable()

    def logClear(self, event=None):
        self.text.delete('1.0', END)
    
    #undo the last action - NOT supported for edge
    def undoHandler(self):
        if self.drawn:
            if TRACE:
                print self.drawn
            self.canvas = eventInstance.widget
            diffX, diffY = (eventInstance.x - self.start.x), (eventInstance.y - self.start.y)
            self.canvas.delete(self.drawn, diffX, diffY)

        if self.type == 'vertex':
            self.node_count-=1
            if self.graph_details['nodes']:
                self.graph_details['nodes'].pop()
        elif self.type == 'text':
            self.label_count -= 1
            if self.graph_details['labels']:
                self.graph_details['labels'].pop()
            if self.graph_json['states']:
                self.vertex_iter-=1
                self.graph_json['states'].pop()
                '''
                elif self.type == 'edge' or self.type == 'curve':
                    self.edge_count -= 1
                    if self.graph_details['edges']:
                        self.graph_details['edges'].pop()
                    if self.graph_json['alphabet']:
                        self.graph_json['alphabet'].pop()
                '''
        else:
            print( "undoHandler:Unknown type")
        self.drawTable()
        self.button6.config(state=DISABLED)
    
    #Return true if mouse is clicked around earlier event 
    def checkeventArgRange(self, eventArg, mouseClick):
        if mouseClick in range(eventArg-7, eventArg+7):
            return True
        else:
            return False

    def onDeleteSelectedItem(self, event):
        self.canvas = event.widget
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y)[0]
        #item = self.canvas.find_closest(event.x, event.y)[0] #either
        itemType = self.canvas.type(item)

        if itemType == 'oval':
            self.type = 'vertex'
            self.node_count-=1
            if self.graph_details['nodes']:
                vertexCoords = self.canvas.coords(item)
                for x_node in self.graph_details['nodes']:
                    if x_node['x1'] == int(vertexCoords[0]) and x_node['y1'] == int(vertexCoords[1]) and x_node['x2'] == int(vertexCoords[2]) and x_node['y2'] == int(vertexCoords[3]):
                        self.graph_details['nodes'].remove(x_node)

        elif itemType == 'line' or itemType == 'arc': #edge
            self.type = 'edge'
            self.edge_count -= 1
            if self.graph_details['edges']:
                edgeCoords = self.canvas.coords(item)
                for x_node in self.graph_details['edges']:
                    if x_node['x1'] == int(edgeCoords[0]) and x_node['y1'] == int(edgeCoords[1]) and x_node['x2'] == int(edgeCoords[2]) and x_node['y2'] == int(edgeCoords[3]):
                        self.graph_details['edges'].remove(x_node)

        elif itemType == 'text':
            self.type = 'text'
            self.label_count -= 1
            if self.graph_details['labels']:
                labelCoords = self.canvas.coords(item)
                for x_node in self.graph_details['labels']:
                    if x_node['x1'] == int(labelCoords[0]) and x_node['y1'] == int(labelCoords[1]):
                        self.graph_details['labels'].remove(x_node)
                    
            itemText = self.canvas.itemcget(item, "text")

            if self.graph_json['states']:
                if itemText in self.graph_json['states']:
                    self.graph_json['states'].remove(itemText)
                    self.vertex_iter-=1
                    if itemText in self.graph_json['transitions'].keys():
                        del self.graph_json['transitions'][itemText]
            
            if self.graph_json['alphabet']:
                if itemText in self.graph_json['alphabet']:
                    self.graph_json['alphabet'].remove(itemText)
                    for state in self.graph_json['states']:
                        if (state in self.graph_json['transitions'].keys() and 
                                itemText in self.graph_json['transitions'][state].keys()):
                            del self.graph_json['transitions'][state][itemText]
            
            #Update 'state_table_matrix'
            for key in self.tableTextMapping.keys():
                keyTuple = key.split(',')
                event_x = int(keyTuple[0])
                event_y = int(keyTuple[1])
                if self.checkeventArgRange(event.x, event_x) and self.checkeventArgRange(event.y, event_y):
                        textPos = self.tableTextMapping[key]
                        textPosTuple = textPos.split(',')
                        row = int(textPosTuple[0])
                        column = int(textPosTuple[1])
                        self.state_table_matrix[row-1][column-1] = None
                        break
        else:
            print( "Unknown item type")
        
        self.canvas.delete(item)
        self.drawTable()
        self.button6.config(state=DISABLED)
        if itemType == 'text':
            if python3 == True:
                messagebox.showinfo("Remove Vertex/Edge", "Please Remove the respective Vertex or Edge, If any.")
            else:
                tkMessageBox.showinfo("Remove Vertex/Edge", "Please Remove the respective Vertex or Edge, If any.")

    def drawTable(self):
        inputBox = []
        for i in range(2, 9):
            inputBox_row = []
            for j in range(2, 9):
                if i == 2 and j == 2:
                    inputBox_row.append('x')
                    continue

                if i == 2 and j <= (self.node_count + 2):
                    '''
                    x = StringVar(self.master, value='V' + str(j))
                    b = Entry(self.state_table, textvariable=x, width=5)
                    b.grid(row=i, column=j)
                    '''
                    labelText = StringVar()
                    labelText.set('Q' + str(j - 2))
                    inputBox_row.append(Label(self.state_table, textvariable=labelText, width=3))
                    inputBox_row[j - 2].grid(row=i, column=j - 2)
                    continue

                if j == 2 and i <= (self.node_count + 2):
                    labelText = StringVar()
                    labelText.set('Q' + str(i - 2))
                    inputBox_row.append(Label(self.state_table, textvariable=labelText, width=3))
                    inputBox_row[j - 2].grid(row=i, column=j - 2)
                    continue

                if i <= (self.node_count + 2) and j <= (self.node_count + 2):
                    x = StringVar()
                    if self.state_table_matrix[i - 3][j - 3]:
                        x.set(self.state_table_matrix[i - 3][j - 3])
                        inputBox_row.append(Entry(self.state_table, width=4, textvariable=x))
                    else:
                        x.set('-')
                        inputBox_row.append(Entry(self.state_table, width=4, textvariable=x, bg='grey'))
                    inputBox_row[j - 2].grid(row=i, column=j - 2)

                else:
                    labelText = StringVar()
                    labelText.set(' ')
                    inputBox_row.append(Label(self.state_table, textvariable=labelText, width=3))
                    inputBox_row[j - 2].grid(row=i, column=j - 2)

            inputBox.append(inputBox_row)

        separateLabel = Label(self.state_table, text='-' * 30)
        separateLabel.grid(row=i + 1, column=0, columnspan=6)

        # separateLabel = Label(self.state_table, text=' ' * 30)
        # separateLabel.grid(row=i+2, column=0, columnspan=6)

        startLabel = Label(self.state_table, text='Start State:', width=10)
        startLabel.grid(row=i + 3, column=0, columnspan=6)

        self.start_entry = StringVar()
        startEntry = Entry(self.state_table, width=20, textvariable=self.start_entry)
        startEntry.grid(row=i + 4, column=0, columnspan=6)

        acceptLabel = Label(self.state_table, text='Accept State:', width=10)
        acceptLabel.grid(row=i + 5, column=0, columnspan=6)

        self.accept_entry = StringVar()
        self.acceptEntry = Entry(self.state_table, width=20, textvariable=self.accept_entry)
        self.acceptEntry.grid(row=i + 6, column=0, columnspan=6)

        separateLabel = Label(self.state_table, text=' ' * 30)
        separateLabel.grid(row=i + 7, column=0, columnspan=6)

        separateLabel = Label(self.state_table, text='-' * 30)
        separateLabel.grid(row=i + 8, column=0, columnspan=6)

        separateLabel = Label(self.state_table, text=' ' * 30)
        separateLabel.grid(row=i + 9, column=0, columnspan=6)

    '''
    def onMove(self, event):
        #Moves the last drawn component
        print event.x, event.y
        print self.start.x, self.start.y
        print "self.drawn:", self.drawn
        if self.drawn:
            if TRACE:
                print self.drawn

            self.canvas = event.widget
            diffX, diffY = (event.x - self.start.x), (event.y - self.start.y)
            self.canvas.move(self.drawn, diffX, diffY)
            self.start = event

            if self.type == 'edge':
                self.edge_count += 1
                #SAT:TODO- Update the graph_details for edge

            if self.type == 'vertex':
                #self.node_count += 1
                #SAT:TODO- Update the graph_details for nodes/vertex
                print "Moving Vertex"
    '''