import socket
import threading
import tkinter
import tkinter.scrolledtext
import en
from tkinter import simpledialog
import random

HOST = '192.168.152.218'  # Replace with your IP
PORT = 9090

class Client:
    colours = ["#EEEE00", "#F5DEB3", "#EE82EE", "#FFE1FF", "#EE9A49", "#00EE00", "#8EE5EE",
               "#FF9912", "#E3CF57", "#FF4040", "#98F5FF", "#7FFF00", "#FF1493", "#1C86EE", "#9F79EE", "#7D26CD"]

    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))

        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.title(self.nickname)
        backg = random.choice(Client.colours)
        self.win.configure(bg=backg)

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg=backg, font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg=backg, font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True
        self.win.protocol("WM_DELETE_WINDOW", self.stop)
        self.win.mainloop()

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end').strip()}"  # Remove extra newline
        message = en.enc(message, 2)
        self.s.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.win.quit()
        self.win.destroy()
        self.s.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.s.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.s.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', en.dec(message, 2) + "\n")  # Add newline for readability
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionResetError:
                print("Server connection lost.")
                self.s.close()
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                self.s.close()
                break

client = Client(HOST, PORT)
