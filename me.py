#!/usr/bin/env python3
# Written by Roberto Rodriguez Jr
import tkinter as tk
import tkinter.font as font
import threading
import os
import sys
import re
import time
import datetime
import subprocess
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator


class App:

    def __init__(self, root):
        self.root = root
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=0)
        self.font = font.nametofont("TkFixedFont")
        self.font.configure(size=11)
        self.pyrathe_init()
        self.setup_keybindings()

    def setup_keybindings(self):
        # defaults
        # ctrl t = transpose char
        # ctrl b = cursor back
        # ctrl f = cursor fwd
        # ctrl k = delete from cursor to end of line
        # ctrl d = delete from front of insert
        # ctrl h = backspace
        # ctrl p = line up
        # ctrl i = insert tab
        # ctrl e = end of line
        # ctrl a = begin of line
        # ctrl o = add a newline
        # ctrl y = paste

        self.root.bind_all("<Control-l>", self.clear_buffer)
        self.root.bind_all("<Control-s>", self.save_focused_to_file)
        self.root.bind_all("<Control-S>", self.save_me_to_file)
        self.root.bind_all("<Control-Alt-a>", self.select_all_text)
        self.root.bind_all("<Control-n>", self.top_of_buffer)
        self.root.bind_all("<Control-m>", self.bottom_of_buffer)
        self.root.bind_all("<Control-Shift-Return>", self.execute_python_code)
        self.root.bind_all("<Control-Alt-Return>", self.eval_python_code)
        self.root.bind_all("<Control-Return>", self.execute_sh_command)
        self.root.bind_all("<Control-Alt-a>", self.select_all_text)
        self.root.bind_all('<ButtonRelease-1>', self.update_cursor_position)
        self.root.bind_all("<KeyRelease>", self.update_cursor_position)
        self.root.bind_all("<Control-r>", self.rss_program)
        self.root.bind_all("<Control-Q>", self.quit_program)
        self.root.bind_all("<Control-D>", self.add_new_tab)
        self.root.bind_all("<Control-C>", self.del_new_tab)
        self.root.bind_all("<Control-X>", self.add_term_tab)
        self.root.bind_all("<Control-Z>", self.add_py_tab)
        self.root.bind_all("<Control-u>", self.backkill)
        self.root.bind_all("<Control-z>", self.add_indent)

    def pyrathe_init(self):
        self.s_name = 0
        self.s_filetype = "_txt"
        self.txtPad_frames = []
        self.create()
        self.timeline()

    def create(self):

        self.msgBarFrame = tk.Frame(self.root, bg="black", padx=10)
        self.msgBarFrame.rowconfigure(0, weight=1)
        self.msgBarFrame.columnconfigure(0, weight=1)
        self.msgBarFrame.grid(row=1, column=1, sticky='nsew')

        self.msgBar = tk.Text(self.msgBarFrame, fg="red", bg="black", relief=tk.FLAT, highlightcolor="red", insertbackground="orange", font=self.font, cursor="pirate", highlightbackground="black", insertwidth=10, height=6)
        self.msgBar.grid(row=0, column=0, sticky='nsew')

        self.lineFrame = tk.Frame(self.root, bg="black", padx=10)
        self.lineFrame.rowconfigure(0, weight=1)
        self.lineFrame.columnconfigure(1, weight=1)
        self.lineFrame.grid(row=2, column=0, sticky='nsew')

        self.line_numbers = tk.Text(self.lineFrame, width=5, relief=tk.FLAT, bg="#000", fg="#666", font=self.font, highlightbackground="black", cursor="spider", spacing1=10.5, spacing3=10)
        self.line_numbers.grid(row=0, column=0, sticky='nsew')

        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=10, cursor="target", bg="black")
        self.paned.rowconfigure(0, weight=1)
        self.paned.columnconfigure(0, weight=1)
        self.paned.grid(row=2, column=1, sticky='nsew')

        self.mainTxtFrame = tk.Frame(self.paned, bg="black", padx=10)
        self.mainTxtFrame.rowconfigure(0, weight=1)
        self.mainTxtFrame.columnconfigure(0, weight=1)
        self.mainTxtFrame.grid(row=0, column=0, sticky='nsew')

        self.txtPad = tk.Text(self.mainTxtFrame, fg="orange", bg="black", wrap=tk.WORD, relief=tk.FLAT, highlightcolor="#666", insertbackground="red", font=self.font, cursor="heart", highlightbackground="black", insertwidth=10, spacing1=10, spacing3=10)
        Percolator(self.txtPad).insertfilter(ColorDelegator())
        self.txtPad.grid(row=0, column=0, sticky='nsew')

        self.paned.add(self.mainTxtFrame)
        self.txtPad.focus_set()

        self.cposFrame = tk.Frame(self.root, bg="black", padx=10)
        self.cposFrame.rowconfigure(0, weight=1)
        self.cposFrame.columnconfigure(0, weight=1)
        self.cposFrame.grid(row=3, column=1, sticky='sw')

        self.cpos = tk.Label(self.cposFrame, text='1,0', bg="black", fg="#777", font=self.font)
        self.cpos.grid(row=0, column=0, sticky='sw')
        
        self.timerLabelFrame = tk.Frame(self.root, bg="black", padx=10)
        self.timerLabelFrame.rowconfigure(0, weight=1)
        self.timerLabelFrame.columnconfigure(0, weight=1)
        self.timerLabelFrame.grid(row=3, column=0, sticky='sw')

        self.timerLabel = tk.Label(self.timerLabelFrame, bg="black", fg="green", text='000', font=self.font)
        self.timerLabel.grid(row=0, column=0, sticky='sw')


    def add_new_tab(self, event=None):
        self.new_frame = tk.Frame(self.paned, bg="black")
        self.new_frame.columnconfigure(0, weight=1)
        self.new_frame.rowconfigure(0, weight=1)
        self.new_frame.grid(row=0, column=0, sticky='nsew')

        self.new_txtPad = tk.Text(self.new_frame, fg="orange", bg="black", wrap=tk.WORD, relief=tk.FLAT, highlightcolor="orange", insertbackground="red", font=self.font, cursor="heart", highlightbackground="black")
        self.new_txtPad.grid(row=0, column=0, sticky='nsew')
        self.paned.add(self.new_frame)
        self.txtPad_frames.append((self.new_frame, self.new_txtPad))
        self.new_txtPad.focus_set()


    def add_py_tab(self, event=None):
        self.py_frame = tk.Frame(self.paned, bg="black")
        self.py_frame.columnconfigure(0, weight=1)
        self.py_frame.rowconfigure(0, weight=1)
        self.py_frame.grid(row=0, column=0, sticky='nsew')

        wid = self.py_frame.winfo_id()
        py_xterm = os.system('xterm -into %d -geometry 100x50 -e python3 &' % wid)
        self.txtPad_frames.append((self.py_frame, py_xterm))
        self.paned.add(self.py_frame)

    def add_term_tab(self, event=None):
        self.term_frame = tk.Frame(self.paned, bg="black")
        self.term_frame.columnconfigure(0, weight=1)
        self.term_frame.rowconfigure(0, weight=1)
        self.term_frame.grid(row=0, column=0, sticky='nsew')

        wid = self.term_frame.winfo_id()
        xterm = os.system('xterm -into %d -geometry 100x50 &' % wid)
        self.txtPad_frames.append((self.term_frame, xterm))
        self.paned.add(self.term_frame)

    def del_new_tab(self, event=None):
        if self.txtPad_frames:
            last_frame, last_txtPad = self.txtPad_frames.pop()
            self.paned.forget(last_frame)
            last_frame.destroy()
        return "break"

    def update_cursor_position(self, event):
        focused = self.root.focus_get()
        if isinstance(focused, tk.Text):
            cursor_position = focused.index(tk.INSERT)
            line, col = cursor_position.split('.')
            self.cpos.configure(text=f"{line},{col}")
            self.line_numbers.configure(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            first, last = focused.yview()

            first_line = int(first * float(focused.index('end').split('.')[0]))
            last_line = int(last * float(focused.index('end').split('.')[0]))

            line_numbers = "\n".join(str(i) for i in range(first_line+1, last_line))
            self.line_numbers.insert('1.0', line_numbers)
            self.line_numbers.configure(state='disabled')
            self.line_numbers.yview_moveto(first)

    def select_all_text(self, event):
        event.widget.tag_add("sel", "1.0", "end")
        return "break"

    def top_of_buffer(self, event):
        event.widget.mark_set("insert", "1.0")
        return "break"

    def bottom_of_buffer(self, event):
        event.widget.mark_set("insert", "end")
        return "break"

    def backkill(self, event):
        event.widget.delete("insert linestart", "insert lineend")
        return "break"

    def clear_buffer(self, event):
        event.widget.delete("1.0", "end")
        return "break"

    def save_focused_to_file(self, event):
        focused = self.root.focus_get()
        content = focused.get("1.0", "end-1c")
        filename = f"{self.s_name}{self.s_filetype}"
        self.s_name += 1
        with open(filename, "w") as file:
            file.write(content)
        self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} {filename} _Buffer Saved\n")
        return "break"

    def save_me_to_file(self, event):
        focused = self.root.focus_get()
        content = focused.get("1.0", "end-1c")
        filename = "me.py"
        with open(filename, "w") as file:
            file.write(content)
        self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} {filename} _Myself & I Saved\n")
        return "break"

    def execute_python_code(self, event):
        focused = self.root.focus_get()
        code = focused.get("1.0", "end-1c")
        try:
            exec(code, globals())
        except Exception as e:
            self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} {str(e)}\n")
        return "break"

    def eval_python_code(self, event):
        focused = self.root.focus_get()
        code = focused.get("insert linestart", "insert lineend")
        try:
            output = eval(code, globals())
            self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')}\n# >>>{output}\n")
        except Exception as e:
            self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} {str(e)}\n")
        return "break"

    def execute_sh_command(self, event):
        focused = self.root.focus_get()
        command = focused.get("insert linestart", "insert lineend")
        try:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                focused.insert("insert linestart", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} ")
                self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} {command}\n")
                focused.insert("1.0", f"{result.stdout}")
            else:
                focused.insert("insert linestart", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')} ")
                self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')}\n{result.stderr}\n")
        except Exception as e:
            self.msgBar.insert("1.0", f"#$%&*^ {datetime.datetime.now().strftime('%H:%M')}\n{str(e)}\n")
        return "break"

    def quit_program(self, event=None):
        command = "pkill xterm"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.root.quit()
        return "break"

    def rss_program(self, event=None):
        os.execv(sys.executable, ['python3'] + sys.argv)

    def timeline(self):
        self.timerFrame = tk.Frame(self.root, bg="black", pady=15, padx=10)
        self.timerFrame.columnconfigure(0, weight=1)
        self.timerFrame.rowconfigure(0, weight=1)
        self.timerFrame.grid(row=0, column=0, sticky='nsew', columnspan=2)

        self.timerBar = tk.Text(self.timerFrame, fg="green", bg="black", relief=tk.FLAT, highlightcolor="green", insertbackground="green", font=self.font, cursor="pirate", highlightbackground="black", insertwidth=10, height=2)
        self.timerBar.grid(row=0, column=0, sticky='nsew')

        self.char_line = threading.Thread(target=self.update_timeline)
        self.char_line.daemon = True
        self.char_line.start()
        
    def update_time_position(self, event=None):
        cursor_position = self.timerBar.index(tk.INSERT)
        line, col = cursor_position.split('.')
        i = int(col)
        c = int(line) - 1
        self.timerLabel.configure(text=f"{str(c)}{str(i)}")

    def update_timeline(self):
        while True:
            self.timerBar.insert("end", ">")
            self.update_time_position()
            time.sleep(60)



    def add_indent(self, event):
        text = event.widget
        line = text.get("insert linestart", "insert")
        match = re.match(r'^(\s+)', line)
        whitespace = match.group(0) if match else ""
        text.insert("insert", f"\n{whitespace}")


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background="black")
    app = App(root)
    root.mainloop()

#$%&*^ 14:10 cat me
#$%&*^ 14:11 cat me.py
#$%&*^ 14:12 cat me.py
#$%&*^ 14:14 cat me.py

#$%&*^ 14:15 cat me.py
#$%&*^ 14:18 cat me.py
#$%&*^ 14:19 cat me.py
#$%&*^ 14:20 cat me.py
#$%&*^ 14:21 cat me.py
#$%&*^ 14:21 cat me.py
#$%&*^ 14:22 cat me.py
#$%&*^ 14:23 cat me.py
#$%&*^ 14:23 cat me.py
#$%&*^ 14:24 cat me.py
#$%&*^ 14:25 cat me.py
#$%&*^ 14:26 cat me.py

#$%&*^ 14:27 cat me.py
#$%&*^ 14:28 cat me.py
#$%&*^ 14:28 cat me.py
#$%&*^ 14:28 cat me.py
#$%&*^ 14:29 cat me.py
#$%&*^ 14:32 cat me.py
#$%&*^ 14:38 cat me.py
#$%&*^ 14:39 cat me.p
#$%&*^ 14:40 cat me.py
#$%&*^ 14:41 cat me.py
#$%&*^ 14:41 cat me.py
#$%&*^ 14:43 cat me.py
#$%&*^ 14:51 cat me.py
#$%&*^ 17:46 cat me.py
#$%&*^ 17:50 cat me.py
#$%&*^ 17:53 cat me.py
#$%&*^ 17:54 cat me.py
#$%&*^ 17:54 cat me.py
#$%&*^ 17:56 cat me.py
#$%&*^ 17:57 cat me.py
#$%&*^ 17:58 cat me.py
#$%&*^ 18:00 cat me.py
#$%&*^ 18:00 cat me.py
#$%&*^ 18:01 cat me.py
#$%&*^ 18:03 cat me.py
#$%&*^ 18:06 cat me.py
#$%&*^ 18:08 cat me.py
#$%&*^ 18:10 cat me.py
#$%&*^ 18:19 cat me.py
#$%&*^ 18:21 cat me.py
#$%&*^ 18:24 cat me.py
#$%&*^ 18:25 cat me.py

#$%&*^ 18:38 cat me.py
#$%&*^ 18:40 cat  me.py
#$%&*^ 18:41 cat me.py
#$%&*^ 18:42 cat me.py
#$%&*^ 18:43 cat me.py
#$%&*^ 18:45 cat me.py

#$%&*^ 18:51 cat me.py
#$%&*^ 18:52 cat me.py
#$%&*^ 18:54 cat me.py
#$%&*^ 18:54 cat me.py
#$%&*^ 19:00 cat me.py

#$%&*^ 19:09 cat me.py
#$%&*^ 19:10 cat me.py
#$%&*^ 19:13 cat me.py
#$%&*^ 19:14 cat me.py
#$%&*^ 19:15 cat me.py
#$%&*^ 19:15 cat me.py
#$%&*^ 19:18 cat me.py
#$%&*^ 19:19 cat me.py
#$%&*^ 19:20 cat me.py
#$%&*^ 19:21 cat me.py
#$%&*^ 19:22 cat me.py
#$%&*^ 19:23 cat me.py
#$%&*^ 19:23 cat me.py
#$%&*^ 19:24 cat me.py
