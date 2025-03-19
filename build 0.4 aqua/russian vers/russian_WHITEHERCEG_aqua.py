import sys
import platform
from tkinter import ttk, messagebox
import tkinter as tk
import os
import psutil
import GPUtil

# Функция для получения списка дисков
def list_drives():
    partitions = psutil.disk_partitions()
    drives = [partition.device for partition in partitions]
    return drives

# Функция для проверки дисков
def check_disk_for_errors():
    # Получение списка дисков
    drives = list_drives()
    if not drives:
        messagebox.showerror("Ошибка", "Диски не найдены.")
        return

    # Окно для выбора дисков
    disk_window = tk.Toplevel(root)
    disk_window.title("Выбор диска")
    disk_window.geometry("400x300")

    tk.Label(disk_window, text="Выберите диск для проверки:", font=("Helvetica", 12)).pack(pady=10)

    # Выпадающий список с дисками
    drive_var = tk.StringVar()
    drive_dropdown = ttk.Combobox(disk_window, textvariable=drive_var, values=drives, state="readonly")
    drive_dropdown.pack(pady=5)

    # Функция для запуска проверки выбранного диска
    def start_check():
        selected_drive = drive_var.get()
        if not selected_drive:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите диск.")
            return
        
        # Окно прогресса проверки
        progress_window = tk.Toplevel(disk_window)
        progress_window.title("Проверка диска")
        progress_window.geometry("300x100")
        tk.Label(progress_window, text=f"Проверяется диск: {selected_drive}", font=("Helvetica", 12)).pack(pady=10)

        try:
            command = f'chkdsk {selected_drive}'
            result = os.system(command)
            if result == 0:
                message = f"Диск {selected_drive} проверен, ошибок не обнаружено."
            else:
                message = f"На диске {selected_drive} обнаружены ошибки."
            messagebox.showinfo("Результат проверки", message)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка проверки диска: {e}")
        finally:
            progress_window.destroy()
            disk_window.destroy()

    # Кнопка для запуска проверки
    tk.Button(disk_window, text="Проверить диск", command=start_check, font=("Helvetica", 12)).pack(pady=10)

known_suspicious_processes = [
    "xmrig", "minered", "ccminer", "trojan", "keylogger", "malware-inject", "pws","winlock","exploit.blackhole","ddos.hacknuke","ddos.rincux.616","adware.adshot","ddos.attack","ddos"
]

#Проверка пк на подозрительные процессы
def check_pc_on_process():
    # Окно прогресса проверки
    progress_window = tk.Toplevel(root)
    progress_window.title("Проверка")
    progress_window.geometry("300x100")
    tk.Label(progress_window, text="Идёт проверка компьютера на процессы...", font=("Helvetica", 12)).pack(pady=20)
    progress_window.update()  # Обновление окна прогресса

    # Поиск подозрительных процессов
    suspicious_processes = []
    for process in psutil.process_iter(['pid', 'name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in known_suspicious_processes:
                suspicious_processes.append((process.info['name'], process.info['pid']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Закрытие окна прогресса
    progress_window.destroy()

    # Отображение результатов проверки
    if suspicious_processes:
        result_message = "Обнаружены подозрительные процессы:\n"
        for name, pid in suspicious_processes:
            result_message += f"  {name} (PID: {pid})\n"
        
        # Запрос на завершение процессов
        user_choice = messagebox.askyesno("Подозрительные процессы", result_message + "\nЗавершить эти процессы?")
        if user_choice:
            for name, pid in suspicious_processes:
                try:
                    process = psutil.Process(pid)
                    process.terminate()  # Завершение процесса
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    messagebox.showerror("Ошибка", f"Не удалось завершить процесс {name} (PID: {pid}): {e}")
            messagebox.showinfo("Результат", "Процессы завершены.")
        else:
            messagebox.showinfo("Результат", "Завершение процессов отменено.")
    else:
        messagebox.showinfo("Результат", "Подозрительные процессы не обнаружены.")

#Информация о компьютере
def display_pc_info():
    # Создание основного окна
    root = tk.Tk()
    root.title("Информация о ПК")
    root.geometry("600x500")

    # Рамка для информации
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    # Сбор данных о системе
    info = {}

    # Система
    info["OS"] = f"{platform.system()} {platform.release()} ({platform.version()})"

    # Процессор
    info["CPU"] = platform.processor()
    info["CPU Cores"] = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    info["CPU Frequency"] = f"{cpu_freq.current:.2f} MHz" if cpu_freq else "Неизвестно"

    # Оперативная память
    virtual_mem = psutil.virtual_memory()
    info["RAM"] = f"{virtual_mem.total / (1024 ** 3):.2f} GB"
    info["RAM Available"] = f"{virtual_mem.available / (1024 ** 3):.2f} GB"

    # Видеокарта
    gpus = GPUtil.getGPUs()
    info["GPUs"] = [gpu.name for gpu in gpus] if gpus else ["Видеокарта не обнаружена"]

    # Диски
    info["Disks"] = [
        {
            "device": partition.device,
            "total": psutil.disk_usage(partition.mountpoint).total / (1024 ** 3),
            "used": psutil.disk_usage(partition.mountpoint).used / (1024 ** 3),
            "free": psutil.disk_usage(partition.mountpoint).free / (1024 ** 3),
        }
        for partition in psutil.disk_partitions()
    ]

    # Батарея
    battery = psutil.sensors_battery()
    if battery:
        info["Battery"] = f"{battery.percent}% (Время: {battery.secsleft // 60} минут)" if battery.secsleft != psutil.POWER_TIME_UNLIMITED else "Подключена зарядка"
    else:
        info["Battery"] = "Батарея не обнаружена"

    # Отображение данных в Tkinter
    ttk.Label(frame, text="Информация о ПК", font=("Helvetica", 16, "bold")).pack(pady=10)

    ttk.Label(frame, text=f"Операционная система: {info['OS']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Процессор: {info['CPU']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Количество ядер: {info['CPU Cores']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Частота процессора: {info['CPU Frequency']}").pack(anchor="w", padx=10)
    ttk.Label(frame, text=f"Оперативная память: {info['RAM']} (доступно: {info['RAM Available']})").pack(anchor="w", padx=10)

    ttk.Label(frame, text="Видеокарты:").pack(anchor="w", padx=10)
    for gpu in info["GPUs"]:
        ttk.Label(frame, text=f" - {gpu}").pack(anchor="w", padx=20)

    ttk.Label(frame, text="Диски:").pack(anchor="w", padx=10)
    for disk in info["Disks"]:
        ttk.Label(frame, text=f" - {disk['device']}: {disk['total']:.2f} GB (использовано: {disk['used']:.2f} GB, свободно: {disk['free']:.2f} GB)").pack(anchor="w", padx=20)

    ttk.Label(frame, text=f"Батарея: {info['Battery']}").pack(anchor="w", padx=10)

    # Кнопка "Обновить"
    ttk.Button(root, text="Обновить", command=lambda: [widget.destroy() for widget in frame.winfo_children()] or display_pc_info()).pack(pady=10)

#Информация от разработчика
def information():
    messagebox.showinfo(title="Информация!",message="Программа находится в бета тестировании и проходит всегда проверку на ошибки. Чтобы связаться со мной в плане находок ошибок или еще чего-то, напишите в telegram: @dark_herceg_exe")
#Поддержать разработчиков
def support():
    messagebox.showinfo(title="Ошибка", message="Функция пока не доступна")


# Главная программа
root = tk.Tk()
root.title("WHITE HERCEG")
root.geometry("500x300")

frame = ttk.Frame(root)
frame.pack()

label = ttk.Label(text="WHITE HERCEG", font=("Helvetica", 15))
label.pack()

side_frame = tk.Frame(root)
side_frame.pack(side="left", fill="y")

#Кнопки
button1 = ttk.Button(root, text="Проверить диски", command=check_disk_for_errors)
button1.pack(padx=5, pady=5, anchor="w")

button2=ttk.Button(root, text="Сканировать компьютер", command=check_pc_on_process)
button2.pack(padx=5, pady=5, anchor="w")

button3=ttk.Button(root, text="Информация", command=information)
button3.pack(padx=5, pady=5, anchor="w")

button4=ttk.Button(root, text="Информация о копмьютере", command=display_pc_info)
button4.pack(padx=5, pady=5, anchor="w")

button5=ttk.Button(root,text="Поддержать разработчиков", command=support)
button5.pack(padx=5, pady=50, anchor="w")



root.mainloop()
