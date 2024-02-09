import sys      #Imports
import os
import threading
from pytube import YouTube
from pytube.cli import on_progress
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as st
from PIL import Image, ImageTk
import base64
import re
import psutil

Me_path = os.path.dirname(os.path.abspath(sys.argv[0]))

# Function to limit CPU usage
def limit_cpu_usage(percent):
    """Limit CPU usage to the given percentage."""
    # Retrieve current process ID
    pid = os.getpid()
    # Retrieve process
    p = psutil.Process(pid)
    # Set CPU affinity to limit to one core
    p.cpu_affinity([0])
    # Limit CPU usage
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

# Call the function to limit CPU usage to 50%
limit_cpu_usage(30)


class StdoutRedirector: ## Terminal redirect
    def __init__(self, data_widget):
        self.data_widget = data_widget
        
    def write(self, message):
        self.data_widget.insert(tk.END, message)
        self.data_widget.see(tk.END)
        
    def flush(self):
        pass

class GUI: ## MAIN
    
    def __init__(self): ## Buttons etc and icon
        
        import icon
        icon_instance = icon.Icon()
        icon_string = icon_instance.IconString
        #base64 code (image encoded in base64)
        
        
        icondata = base64.b64decode(icon_string)
        tempFile = "icon.ico"
        iconfile = open(tempFile,"wb")
        iconfile.write(icondata)
        iconfile.close()
        
        ##FRAME START
        self.frame = tk.Tk()
        self.frame.wm_iconbitmap(tempFile)
        
        os.remove(tempFile)
        
        #ICON END
        
        
        self.frame.geometry("500x300")
        self.frame.title("YouTube Downloader")
        self.frame.configure(bg="gray15")
        self.frame.resizable(False, False)
        
        self.label = tk.Label(self.frame, text="Enter the URL of desired video", 
                              bg="gray15",
                              fg="snow",
                              font=("Fixedsys", 16))
        
        self.inputentry = tk.Entry(self.frame, 
                                   width=60,
                                   font=("Fixedsys", 12),
                                   bg="gray11",
                                   fg="snow",)

        self.var = tk.IntVar()

        self.mp3toggle = tk.Checkbutton(self.frame,
                                        variable=self.var,
                                        onvalue=1,
                                        offvalue=0,
                                        text="",
                                        bg="gray15",
                                        fg="springgreen",
                                        activebackground="gray15",
                                        activeforeground="springgreen",
                                        font=("Fixedsys", 12),
                                        bd=1,
                                        selectcolor="gray20",
                                        command=self.vartoggle
                                        )
        
        self.mp3togglelabel = tk.Label(self.frame,
                                       text="Audio",
                                       bg="gray15",
                                       fg="springgreen",
                                       font=("Fixedsys", 12),
                                       
                                       )
        
        self.keepvidvar = tk.IntVar()
        
        self.keepvideo = tk.Checkbutton(self.frame,
                                        variable=self.keepvidvar,
                                        onvalue=1,
                                        offvalue=0,
                                        text="",
                                        bg="gray15",
                                        fg="springgreen",
                                        activebackground="gray15",
                                        activeforeground="springgreen",
                                        font=("Fixedsys", 12),
                                        bd=1,
                                        selectcolor="gray20",
                                        command=self.keepvideotoggle
                                        )
        
        self.keepvideolabel = tk.Label(self.frame,
                                       text="Audio&Video",
                                       bg="gray15",
                                       fg="springgreen",
                                       font=("Fixedsys", 12),
                                       
                                       )
        
        self.dlbutton = tk.Button(self.frame, 
                                  text="Download Video",
                                  font=("Fixedsys", 14),
                                  bg="gray25",
                                  fg="snow",
                                  command=self.download_video_async)
        
        
        
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("styled.Horizontal.TProgressbar", thickness=20, troughcolor="gray16", troughrelief="flat", troughborderwidth=0, borderwidth=0)
        s.configure("styled.Horizontal.TProgressbar", foreground="purple1", background="purple1")
        self.progressbar = ttk.Progressbar(self.frame, style="styled.Horizontal.TProgressbar", orient="horizontal",


                                           length=490,
                                           mode="determinate")
        
        
        
        self.databox = tk.Text(height=8,
                               bg="gray18",
                               font=("Fixedsys", 10),
                               fg="snow",
                               state=tk.DISABLED
                               )
        
        #for selecting text and copying
        self.databox.bind("<Control-a>", lambda e: self.databox.tag_add(tk.SEL, "1.0", tk.END))
        self.databox.bind("<Control-c>", lambda e: self.databox.event_generate("<<Copy>>"))
        
        
        
        
        sys.stdout = StdoutRedirector(self.databox)
        
        self.label.pack(padx=10, pady=10)
        self.inputentry.pack(padx=10, pady=10)
        self.mp3toggle.place(x=10, y=91)
        self.mp3togglelabel.place (x=32, y=92)
        self.keepvideo.place(x=467, y=91)
        self.keepvideolabel.place(x=374, y=92)
        self.dlbutton.pack(padx=10, pady=10)
        self.progressbar.pack(padx=10, pady=5)
        self.databox.pack(padx=8, pady=5)
        
        
        self.frame.mainloop()
        
    def var(self): ## MP3 Checkbutton variable
            return self.var.get()
    
    def keepvideo(self): ## Audio&Video Checkbutton variable
            return self.keepvideo.get()
        
    def keepvideotoggle(self):
        if self.keepvidvar.get() == 1:
            self.var.set(0)
            self.mp3toggle.deselect()
            
    def vartoggle(self):
        if self.var.get() == 1:
            self.keepvidvar.set(0)
            self.keepvideo.deselect()
        
        
    def download_progress(self, stream, chunk, remaining):
        file_size = stream.filesize
        downloaded = file_size - remaining
        percentage = (downloaded / file_size) * 100
        self.progressbar["value"] = percentage
        self.frame.update_idletasks()  #updates the progressbar
        
    def sanitize_filename(self, filename): #cleans up filenames
        sanitized_filename = re.sub(r'[\\)(/:"*?<>#{.}]', '', filename)
        sanitized_filename = re.sub(r'\s+', ' ', sanitized_filename)  # Replace multiple consecutive spaces with a single space
        return sanitized_filename.strip()
    
    def download_video_async(self):
            def download_task():
                self.download_video()
            download_thread = threading.Thread(target=download_task)
            download_thread.start()
    
    def download_video(self):
        
        self.databox.config(state=tk.NORMAL)
        self.databox.delete('1.0', tk.END)
        self.databox.config(state=tk.DISABLED)
        
        
        url = self.inputentry.get()
        mp3onoff = self.var.get()
        keepvideo = self.keepvidvar.get()
        yt = YouTube(url, on_progress_callback=self.download_progress)
        title = self.sanitize_filename(yt.title)
        yd = yt.streams.get_highest_resolution()
        mp3 = yt.streams.get_by_itag(251)
        file_size = yd.filesize
        audio_file_size = mp3.filesize
        Audio_path = os.path.join(Me_path + f"/Downloads/Audio")
        Convert_path = os.path.join(Me_path + f"/Downloads/Audio/Convert")
        Video_path = os.path.join(Me_path + f"/Downloads/Video")
        
        try:
            
            if mp3onoff == 1:
                # Only activates if Audio Only active
                self.databox.config(state=tk.NORMAL)
                self.databox.insert(tk.END, f"Downloading Video for Conversion \n{title}\n")
                self.databox.insert(tk.END, f"Audio File Size: {audio_file_size / (1024 * 1024):.2f} MB\n")
                self.databox.config(state=tk.DISABLED)
                
                mp3.download(Audio_path, filename=f"{title}.mp4")
                
                self.databox.config(state=tk.NORMAL)
                self.databox.insert(tk.END, f"{Audio_path}\n")
                self.databox.insert(tk.END, "Download Completed!\n")
                self.databox.config(state=tk.DISABLED)
                return
            else: 
                
                if keepvideo == 1:
                    
                    self.databox.config(state=tk.NORMAL)
                    self.databox.insert(tk.END, f"Downloading Video and Audio.\n{title}\n")
                    self.databox.insert(tk.END, f"Video File Size: {file_size / (1024 * 1024):.2f} MB\n")
                    self.databox.insert(tk.END, f"Audio File Size: {audio_file_size / (1024 * 1024):.2f} MB\n")
                    self.databox.config(state=tk.DISABLED)
                    
                    self.databox.insert(tk.END, f"{Video_path}\n")
                    self.databox.insert(tk.END, f"{Audio_path}\n")
                
                    yd.download(f"{Video_path}/", filename=f"{title}.mp4")
                    mp3.download(f"{Audio_path}/", filename=f"{title}.mp4")
                    
                    self.databox.config(state=tk.NORMAL)
                    self.databox.insert(tk.END, "Video and Audio acquired!\n")
                    self.databox.config(state=tk.DISABLED)
                    return
                
                #Just a regular video download
                self.databox.config(state=tk.NORMAL)
                self.databox.insert(tk.END, f"Downloading: \n{title}\n")
                self.databox.insert(tk.END, f"Video File Size: {file_size / (1024 * 1024):.2f} MB\n")
                self.databox.config(state=tk.DISABLED)
                yd.download(Video_path, filename=f"{title}.mp4")
                self.databox.config(state=tk.NORMAL)
                self.databox.insert(tk.END, f"{Video_path}\n")
                self.databox.insert(tk.END, "Download Completed!\n")
                self.databox.config(state=tk.DISABLED)
                return
            
        except Exception as e: #Error handling
            self.databox.config(state=tk.NORMAL)
            if "[WinError 183]" in str(e):
                self.databox.insert(tk.END, "\nThis file already exists,\nPlease remove the previous one before attempting again.\n\n")
            else:
            
                self.databox.insert(tk.END, f"\nSomething went wrong\n")
                self.databox.insert(tk.END, f"Error: {e}\n")
                self.databox.config(state=tk.DISABLED)
    
    
    #USED FOR REFRESHING DATABOX DATA
        
        self.frame.after(100, self.databox_refresh) #TOGGLE TIMER
        
    
    def databox_refresh(self):
        current_state = self.databox["state"]
        new_state = tk.NORMAL if current_state == tk.DISABLED else tk.DISABLED
        self.databox.config(state=new_state)
        
        
        self.frame.after(100, self.databox_refresh) #TOGGLE TIMER
    #USED FOR REFRESHING DATABOX DATA END
            
if __name__ == "__main__":
    GUI().frame.mainloop()