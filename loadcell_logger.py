import pathlib
import tkinter as tk
import tkinter.ttk as ttk
import sys
import glob
import serial
import time
import datetime

from tkinter.filedialog import asksaveasfile

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "main_prog.ui"


class MainProgApp:
    def __init__(self, master=None):
        self.recording_state = 0
        self.terminate = False
        self.offset = 10
        # build ui
        self.main_toplevel = tk.Tk() if master is None else tk.Toplevel(master)
        self.frame1 = ttk.Frame(self.main_toplevel)
        self.stop_button = ttk.Button(self.frame1)
        self.stop_button .configure(state='disabled', text='STOP', width='15')
        self.stop_button .grid(column='19', padx='10', row='1', sticky='e')
        self.stop_button .configure(command=self.stop_button_pressed)
        self.port_combobox = ttk.Combobox(self.frame1)
        self.comport = tk.StringVar(value='')
        self.port_combobox.configure(textvariable=self.comport, width='8')
        self.port_combobox.grid(column='1', padx='10 10', row='0', sticky='w')
        self.label1 = ttk.Label(self.frame1)
        self.label1.configure(font='{TH Niramit AS} 16 {}', text='เลือกคอมพอร์ต')
        self.label1.grid(column='0', padx='10 0', pady='10', row='0', sticky='w')
        self.label2 = ttk.Label(self.frame1)
        self.label2.configure(font='{TH Niramit AS} 16 {}', text='ข้อมูล')
        self.label2.grid(column='0', padx='10', row='1', sticky='w')
        self.logging_text = tk.Text(self.frame1)
        self.logging_text.configure(font='{TH Niramit AS} 16 {}', height='20', width='100',state='disabled')
        self.logging_text.grid(column='0', columnspan='21', padx='10', pady='10', row='3')
        self.save_button = ttk.Button(self.frame1)
        self.save_button.configure(state='disabled', text='SAVE', width='15')
        self.save_button.grid(column='20', padx='10', row='0', sticky='e')
        self.save_button.configure(command=self.save_button_pressed)
        self.clear_button = ttk.Button(self.frame1)
        self.clear_button.configure(state='disabled', text='CLEAR', width='15')
        self.clear_button.grid(column='20', padx='10', row='1', sticky='e')
        self.clear_button.configure(command=self.clear_button_pressed)
        self.start_button = ttk.Button(self.frame1)
        self.start_button.configure(text='START', width='15')
        self.start_button.grid(column='19', padx='10', row='0', sticky='e')
        self.start_button.configure(command=self.start_button_pressed)
        self.vertical_scrollbar = ttk.Scrollbar(self.frame1)
        self.vertical_scrollbar.configure(orient='vertical')
        self.vertical_scrollbar.grid(column='21', row='3', sticky='ns')
        self.frame1.configure(height='200', padding='10', width='500')
        self.frame1.pack()
        self.main_toplevel.configure(height='200', width='200')
        self.main_toplevel.resizable(False, False)
        self.main_toplevel.title('Loadcell logger')

        # add code
        self.logging_text['yscrollcommand'] = self.vertical_scrollbar.set
        self.vertical_scrollbar['command'] = self.logging_text.yview

        list_available_port = self.list_serial_ports()
        if len(list_available_port)<=0:
            list_available_port = ['']
        self.port_combobox['values'] = list_available_port

        self.serial_link = serial.Serial()
        self.retry_connect = 0
        # Main widget
        self.mainwindow = self.main_toplevel
    
    def run(self):
        self.mainwindow.mainloop()

    def stop_button_pressed(self):
        try:
            self.serial_link.write(b'0\n')
            self.terminate = True
            self.stop_button.configure(state='disabled')
            self.save_button.configure(state='normal')
            self.clear_button.configure(state='normal')
            while self.serial_link.in_waiting:
                try:
                    print("xxx")
                    print(self.serial_link.readall().decode())
                except:
                    pass
            try:
                self.serial_link.close()
            except:
                pass
        except:
            pass
        
        
    def save_button_pressed(self):
        file_type = [('Text Document', '*.txt')]
        file_path = asksaveasfile(filetypes = file_type, defaultextension = file_type)
        if file_path != None:
            file_path.write(self.logging_text.get(1.0, tk.END))
            file_path.close()

    def clear_button_pressed(self):
        self.logging_text.configure(state='normal')
        self.logging_text.delete('1.0', tk.END)
        self.logging_text.configure(state='disabled')

        self.start_button.configure(state='normal')
        self.save_button.configure(state='disabled')
        self.clear_button.configure(state='disabled')

    def pre_recording(self):
        if self.serial_link.isOpen():
            self.port_combobox.configure(state='disbled')
            self.save_button.configure(state='disabled')
            self.clear_button.configure(state='disabled')
            self.stop_button.configure(state='normal')
            self.start_button.configure(state='disabled')
            #========== add record date and time on logging area =================
            log_message = "# Record date and time: " + str(datetime.datetime.now()) + "\n"
            self.logging_text.config(state='normal')
            self.logging_text.insert(tk.END,log_message)
            self.logging_text.config(state='disabled')
            #=====================================================================
            self.serial_link.write(b'1\n')
            self.main_toplevel.after(20,self.record_loop)
        else:
            self.serial_link.open()
            self.retry_connect = self.retry_connect + 1
            if self.retry_connect >=50:
                print("can not connect to device")
            else:
                self.main_toplevel.after(100,self.pre_recording)

    def record_loop(self):
        try:
            if self.terminate == False:
                if self.serial_link.isOpen():
                    if self.serial_link.in_waiting:
                        self.logging_text.config(state='normal')
                        serial_message = self.serial_link.readline().decode().split(',')
                        log_message = str(datetime.datetime.now().time()) + "," + str((int(serial_message[0])-10)/40) + "," + str((int(serial_message[1])-10)/40) + "," + str((int(serial_message[2])-10)/40) + "\n"
                        self.logging_text.insert(tk.END,log_message)
                        self.logging_text.config(state='disabled')
                    if(self.terminate==False):
                        self.main_toplevel.after(10,self.record_loop)        
        except:
            tk.messagebox.showinfo(title="Device is disconnected", message="serial link loss")
        

    def start_button_pressed(self):
        self.terminate = False
        comport_name = self.port_combobox.get()
        if  comport_name != "":
            try:
                self.serial_link.baudrate = 115200
                self.serial_link.port = comport_name
                self.serial_link.timeout = 0.1
                if self.serial_link.isOpen():
                    self.main_toplevel.after(100,self.pre_recording)
                else:
                    self.serial_link.open()
                    self.main_toplevel.after(3000,self.pre_recording)
            except:
                pass
        else:
            tk.messagebox.showinfo(title="Device not available", message="please select USB port")

    def list_serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(2,20)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result


if __name__ == '__main__':
    app = MainProgApp()
    app.run()


