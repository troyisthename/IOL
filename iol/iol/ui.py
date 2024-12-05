from main import *
import tkinter as tk
from tkinter import Scrollbar, ttk, Menu, filedialog, BOTH, END, scrolledtext, simpledialog


class App(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.state('zoomed')
        self.geometry("1400x700")
        self.title('Lexical Analyzer - *Untitled.iol')
        self.resizable(1, 1)
        self.src = ''
        # Configure the grid layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)

        # Initialize window widgets
        self.create_widgets()

        # For key press detection == If key press detected, then there is a change in file 
        self.bind("<Key>", self.key_pressed)
        self.fileStatus = True

    # Detect if key is pressed
    def key_pressed(self, event):
        self.updateTitle("*Please save file changes")
        self.fileStatus = False

    # Creates widgets on the root window 
    def create_widgets(self):
        # Setup Frames
        editorFrame = ttk.LabelFrame(self, text="Editor")
        editorFrame.grid(column=0, row=0, sticky=tk.W, padx=0, pady=0)

        consoleFrame = ttk.LabelFrame(self, text="Console", height= 20, width=100)
        consoleFrame.grid(columnspan=3, row=1, sticky=tk.SW, padx=5, pady=5)

        resultFrame = ttk.LabelFrame(self, text="Table")
        resultFrame.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)

        # Menu Bar Setup
        menubar = Menu(self)
        self.config(menu=menubar)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label="New File", command=self.newFile)
        fileMenu.add_command(label="Open File", command=self.onOpen)
        fileMenu.add_command(label="Save File", command=self.saveFile)
        menubar.add_cascade(label="File", menu=fileMenu)

        compileMenu = Menu(menubar)
        compileMenu.add_command(label="Compile", command=self.compile)
        compileMenu.add_command(label="Save and Compile", command=self.saveCompile)
        menubar.add_cascade(label="Compile", menu=compileMenu)

        # Text Editor Content
        self.editorContent = scrolledtext.ScrolledText(editorFrame)
        self.editorContent.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)


        # Console Content
        self.consoleContent = scrolledtext.ScrolledText(consoleFrame, height=12)
        self.consoleContent.grid(column=0, row=0,sticky="nsew", padx=5, pady=5)
        self.consoleContent.config(state='disabled')

        # Table Content Tabs
        resultTabs = ttk.Notebook(resultFrame)

        errorsTab = ttk.Frame(resultTabs)
        lexemeTab = ttk.Frame(resultTabs)
        variablesTab = ttk.Frame(resultTabs)

        resultTabs.add(errorsTab, text="Errors")
        resultTabs.add(lexemeTab, text="Lexemes")
        resultTabs.add(variablesTab, text="Variables")
        resultTabs.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)

        self.lexemeContent = scrolledtext.ScrolledText(lexemeTab)
        self.lexemeContent.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
        self.lexemeContent.config(state='disabled')

        self.variablesContent = scrolledtext.ScrolledText(variablesTab)
        self.variablesContent.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
        self.variablesContent.config(state='disabled')

        self.errorsContent = scrolledtext.ScrolledText(errorsTab)
        self.errorsContent.grid(column=0, row=0, sticky="nsew", padx=5, pady=5)
        self.errorsContent.config(state='disabled')

    # Create new file by clearing frame contents, and reseting source file to empty
    def newFile(self):
        self.src = ""
        self.contentEditable(True)
        self.editorContent.delete(1.0,END)
        self.lexemeContent.delete(1.0, END)
        self.variablesContent.delete(1.0, END)
        self.errorsContent.delete(1.0, END)
        self.contentEditable(False)
        self.updateTitle("*Untitled.iol")

    # Helper function to toggle content state to normal or disabled
    def contentEditable(self, edit):
        if edit:
            self.lexemeContent.config(state='normal')
            self.variablesContent.config(state='normal')
            self.errorsContent.config(state='normal')
            self.consoleContent.config(state='normal')
        else:
            self.lexemeContent.config(state='disabled')
            self.variablesContent.config(state='disabled')
            self.errorsContent.config(state='disabled')
            self.consoleContent.config(state='disabled')

    # Open file dialog to get content directory
    def onOpen(self):
        ftypes = [('IOL files', '*.iol'), ('All files', '*')]
        fl = filedialog.askopenfilename(filetypes = ftypes)
        if fl == "":
            return
        self.src = fl

        # Clear 
        self.contentEditable(True)
        self.lexemeContent.delete(1.0, END)
        self.editorContent.delete(1.0, END)
        self.contentEditable(False)

        if fl != '':
            text = self.readFile(fl)
            self.editorContent.insert(END, text)
        self.updateTitle(fl)
        self.consoleMessage('OPEN_FILE',fl)
        self.fileStatus = True

    # With a non-empty source file, invoke lexer, parser, and semantic analyzer from Main class
    # If no errors from compilation, it creates an executor object to run the source file
    def compile(self):
        if self.src == '':
            self.consoleMessage('FILE_UNSAVED')
            return

        if self.fileStatus == False:
            self.consoleMessage('FILE_UNSAVED')
            return

        self.contentEditable(True)
        self.lexemeContent.delete(1.0, END)
        compileResult = Main.compiler(self.src)

        # Insert tokens from generated tkn file
        fl = self.src.replace('.iol', '.tkn')
        text = self.readFile(fl)
        self.lexemeContent.insert(END, text)
        
        # insert Variables
        self.variablesContent.delete(1.0, END)
        self.variablesContent.insert(END,"variable list (name, type) \n")
        for var in compileResult[0]:
            self.variablesContent.insert(END, '\t' + var + '\n')

        # insert errors list
        self.errorsContent.delete(1.0, END)
        # self.errorsContent.insert(END,"ERR\n")
        for err in compileResult[1]:
            self.errorsContent.insert(END, '\t' + err + '\n')


        # Update console message and toggle content editable
        self.contentEditable(False)
        fsrc = self.src.split('/')[-1]
        fsrc_raw = fsrc.split('.')[0]

        # has compilation errors
        if compileResult[1]:
            info = f'{fsrc} compiled with {len(compileResult[1])} error(s) found. Unable to execute program {fsrc_raw}, see Errors tab for the error list...\n\n'
            self.consoleMessage('COMPILE_ERROR', info)
            self.fileStatus = True
            return

        info = f'{fsrc} compiled with no errors found. Program {fsrc_raw} will now be executed...\n\n'
        self.consoleMessage('COMPILE_SUCCESS', info)
        
        # execute code, if no errors from source file
        executor = Executor(self, compileResult[2], compileResult[3])
        
        self.fileStatus = True


    # Save and compile current editor content
    def saveCompile(self):
        
        if self.src == '':
            self.src = "./Untitled.iol"

        self.contentEditable(True)
        text = self.editorContent.get(1.0, "end-1c")
        with open(self.src, 'w') as output:
            output.write(text)
            self.updateTitle(self.src)
        self.fileStatus = True
        self.compile()
        self.contentEditable(False)
        self.fileStatus = True
        
    # Save current content inside the editor frame content
    def saveFile(self):
        ftypes = [('IOL files', '*.iol'), ('All files', '*')]
        fl = filedialog.asksaveasfilename(initialfile='Untitled.iol',filetypes= ftypes, defaultextension='.iol')

        if fl=="":
            return

        text = self.editorContent.get(1.0, "end-1c")
        with open(fl, 'w') as output:
            output.write(text)
            self.src = fl
        self.updateTitle(fl)
        self.consoleMessage('SAVE_FILE',fl)
        self.fileStatus = True


    # function to update window title
    def updateTitle(self, title):
        self.title(f"Lexical Analyzer - {title}")

    # Helper function to read file
    def readFile(self, filename):
        f = open(filename, "r")
        text = f.read()
        return text

    # For producing console messages
    def consoleMessage(self, message, info = ''):
        self.contentEditable(True)
        self.consoleContent.delete(1.0, END)
        if message == 'FILE_UNSAVED':
            self.consoleContent.insert(END, "Unable to compile. Please save file first")
        elif message == 'COMPILE_SUCCESS':
            self.consoleContent.insert(END, "Compile success: " + info)
        elif message == 'COMPILE_ERROR':
            self.consoleContent.insert(END, "Compile error: " + info)
        elif message == 'OPEN_FILE':
            self.consoleContent.insert(END, "Opened " + info)
        elif message == 'SAVE_FILE':
            self.consoleContent.insert(END, "Saved " + info)
        self.contentEditable(False)

if __name__ == "__main__":
    app = App()
    app.mainloop()