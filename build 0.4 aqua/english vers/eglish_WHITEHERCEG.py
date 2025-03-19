import sys
import platform
from tkinter import ttk, messagebox
import tkinter as tk
import os
import psutil
import GPUtil

# Function to get a list of drives
def list_drives():
    partitions = psutil.disk_partitions()
    drives = [partition.device for partition in partitions]
    return drives

# Function to check disks for errors
def check_disk_for_errors():
    # Get the list of drives
    drives = list_drives()
    if not drives:
        messagebox.showerror("Error", "No drives found.")
        return

    # Window for drive selection
    disk_window = tk.Toplevel(root)
    disk_window.title("Select Drive")
    disk_window.geometry("400x300")

    tk.Label(disk_window, text="Select a drive to check:", font=("Helvetica", 12)).pack(pady=10)

    # Dropdown list with drives
    drive_var = tk.StringVar()
    drive_dropdown = ttk.Combobox(disk_window, textvariable=drive_var, values=drives, state="readonly")
    drive_dropdown.pack(pady=5)

    # Function to start the check for the selected drive
    def start_check():
        selected_drive = drive_var.get()
        if not selected_drive:
            messagebox.showerror("Error", "Please select a drive.")
            return
        
        # Progress window for checking
        progress_window = tk.Toplevel(disk_window)
        progress_window.title("Checking Drive")
        progress_window.geometry("300x100")
        tk.Label(progress_window, text=f"Checking drive: {selected_drive}", font=("Helvetica", 12)).pack(pady=10)

        try:
            command = f'chkdsk {selected_drive}'
            result = os.system(command)
            if result == 0:
                message = f"Drive {selected_drive} checked, no errors found."
            else:
                message = f"Errors found on drive {selected_drive}."
            messagebox.showinfo("Check Result", message)
        except Exception as e:
            messagebox.showerror("Error", f"Error checking drive: {e}")
        finally:
            progress_window.destroy()
            disk_window.destroy()

    # Button to start the check
    tk.Button(disk_window, text="Check Drive", command=start_check, font=("Helvetica", 12)).pack(pady=10)

known_suspicious_processes = [
    "xmrig", "minered", "ccminer", "trojan", "keylogger", "malware-inject", "pws", "winlock", "exploit.blackhole", "ddos.hacknuke", "ddos.rincux.616", "adware.adshot", "ddos.attack", "ddos"
]

# Check PC for suspicious processes
def check_pc_on_process():
    # Progress window for checking
    progress_window = tk.Toplevel(root)
    progress_window.title("Check")
    progress_window.geometry("300x100")
    tk.Label(progress_window, text="Checking computer for processes...", font=("Helvetica", 12)).pack(pady=20)
    progress_window.update()  # Update the progress window

    # Find suspicious processes
    suspicious_processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in known_suspicious_processes:
                suspicious_processes.append((process.info['name'], process.info['pid']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Close the progress window
    progress_window.destroy()

    # Display check results
    if suspicious_processes:
        result_message = "Suspicious processes detected:\n"
        for name, pid in suspicious_processes:
            result_message += f"  {name} (PID: {pid})\n"
        
        # Prompt to terminate processes
        user_choice = messagebox.askyesno("Suspicious Processes", result_message + "\nTerminate these processes?")
        if user_choice:
            for name, pid in suspicious_processes:
                try:
                    process = psutil.Process(pid)
                    process.terminate()  # Terminate process
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    messagebox.showerror("Error", f"Failed to terminate process {name} (PID: {pid}): {e}")
            messagebox.showinfo("Result", "Processes terminated.")
        else:
            messagebox.showinfo("Result", "Process termination canceled.")
    else:
        messagebox.showinfo("Result", "No suspicious processes detected.")

# Display PC information
def display_pc_info():
    # Create the main window
    root = tk.Tk()
    root.title("PC Information")
    root.geometry("600x500")

    # Frame for information
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # Gather system information
    info = {}

    # System
    info["OS"] = f"{platform.system()} {platform.release()} ({platform.version()})"

    # Processor
    info["CPU"] = platform.processor()
    info["CPU Cores"] = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    info["CPU Frequency"] = f"{cpu_freq.current:.2f} MHz" if cpu_freq else "Unknown"

    # RAM
    virtual_mem = psutil.virtual_memory()
    info["RAM"] = f"{virtual_mem.total / (1024 ** 3):.2f} GB"
    info["RAM Available"] = f"{virtual_mem.available / (1024 ** 3):.2f} GB"

    # GPU
    gpus = GPUtil.getGPUs()
    info["GPUs"] = [gpu.name for gpu in gpus] if gpus else ["GPU not detected"]

    # Disks
    info["Disks"] = [
        {
            "device": partition.device,
            "total": psutil.disk_usage(partition.mountpoint).total / (1024 ** 3),
            "used": psutil.disk_usage(partition.mountpoint).used / (1024 ** 3),
            "free": psutil.disk_usage(partition.mountpoint).free / (1024 ** 3),
        }
        for partition in psutil.disk_partitions()
    ]

    # Battery
    battery = psutil.sensors_battery()
    if battery:
        info["Battery"] = f"{battery.percent}% (Time: {battery.secsleft // 60} minutes)" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Charging connected"
    else:
        info["Battery"] = "Battery not detected"

    # Display data in Tkinter
    ttk.Label(frame, text="PC Information", font=("Helvetica", 16, "bold")).pack(pady=10)

    ttk.Label(frame, text=f"Operating System: {info['OS']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Processor: {info['CPU']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Cores: {info['CPU Cores']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"CPU Frequency: {info['CPU Frequency']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"RAM: {info['RAM']} (Available: {info['RAM Available']})").pack(anchor="w", padx=10)

    ttk.Label(frame, text="GPUs:").pack(anchor="w", padx=10)
    for gpu in info["GPUs"]:
        ttk.Label(frame, text=f" - {gpu}").pack(anchor="w", padx=20)

    ttk.Label(frame, text="Disks:").pack(anchor="w", padx=10)
    for disk in info["Disks"]:
        ttk.Label(frame, text=f" - {disk['device']}: {disk['total']:.2f} GB (used: {disk['used']:.2f} GB, free: {disk['free']:.2f} GB)").pack(anchor="w", padx=20)

    ttk.Label(frame, text=f"Battery: {info['Battery']}").pack(anchor="w", padx=10)

    # "Refresh" button
    ttk.Button(root, text="Refresh", command=lambda: [widget.destroy() for widget in frame.winfo_children()] or display_pc_info()).pack(pady=10)

# Developer information
def information():
    messagebox.showinfo(title="Information!", message="The program is in beta testing and is always being checked for bugs. To contact me about bugs or anything else, write to Telegram: @dark_herceg_exe")
# Support developers
def support():
    messagebox.showinfo(title="Error", message="This feature is not yet available.")


# Main program
root = tk.Tk()
root.title("WHITE HERCEG")
root.geometry("500x300")

frame = ttk.Frame(root)
frame.pack()

label = ttk.Label(text="WHITE HERCEG", font=("Helvetica", 15))
label.pack()

side_frame = tk.Frame(root)
side_frame.pack(side="left", fill="y")

# Buttons
button1 = ttk.Button(root, text="Check Disks", command=check_disk_for_errors)
button1.pack(padx=5, pady=5, anchor="w")

button2 = ttk.Button(root, text="Scan Computer", command=check_pc_on_process)
button2.pack(padx=5, pady=5, anchor="w")

button3 = ttk.Button(root, text="Information", command=information)
button3.pack(padx=5, pady=5, anchor="w")

button4 = ttk.Button(root, text="Computer Information", command=display_pc_info)
button4.pack(padx=5, pady=5, anchor="w")

button5 = ttk.Button(root, text="Support Developers", command=support)
button5.pack(padx=5, pady=50, anchor="w")

root.mainloop()