import psutil
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Интервал обновления в секундах (можно изменить для частоты обновления)
UPDATE_INTERVAL = 5

class SystemMonitorApp:
    """
    Класс приложения для мониторинга системных ресурсов с графическим интерфейсом.
    
    Отображает в реальном времени: CPU, RAM, диск, сеть и графики загрузки.
    Использует tkinter для GUI и matplotlib для визуализации данных.
    """
    
    def __init__(self, root):
        """
        Инициализирует основное окно приложения и запускает сбор данных.

        Args:
            root (tk.Tk): Корневое окно tkinter.
        """
        
        self.root = root
        self.root.title("Мониторинг Ресурсов Системы")
        self.root.geometry("1024x920")
        
        # История данных для построения графиков (последние значения)
        self.cpu_history = []
        self.ram_history = []
        
        # Настройка интерфейса и запуск обновления данных
        self.setup_ui()
        self.update_data()
        
    def setup_ui(self):
        """
        Создаёт и размещает все элементы графического интерфейса:
        * метки времени;
        * блоки метрик (CPU, RAM, диск, сеть);
        * график загрузки CPU и RAM.
        """
        
        # Основной фрейм с отступами для аккуратного расположения элементов
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Метка для отображения текущего времени обновления
        self.time_label = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.time_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Фрейм для отображения метрик системы с заголовком и отступами
        metrics_frame = ttk.LabelFrame(main_frame, text="Метрики системы", padding="10")
        metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Блок отображения информации о CPU
        ttk.Label(metrics_frame, text="CPU:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.cpu_current_label = ttk.Label(metrics_frame, text="")
        self.cpu_current_label.grid(row=1, column=0, sticky=tk.W)
        self.cpu_loadavg_label = ttk.Label(metrics_frame, text="")
        self.cpu_loadavg_label.grid(row=2, column=0, sticky=tk.W)

        # Блок отображения информации о памяти (RAM)
        ttk.Label(metrics_frame, text="Память (RAM):", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        self.ram_total_label = ttk.Label(metrics_frame, text="")
        self.ram_total_label.grid(row=4, column=0, sticky=tk.W)
        self.ram_used_label = ttk.Label(metrics_frame, text="")
        self.ram_used_label.grid(row=5, column=0, sticky=tk.W)
        self.ram_percent_label = ttk.Label(metrics_frame, text="")
        self.ram_percent_label.grid(row=6, column=0, sticky=tk.W)

        # Блок отображения информации о диске
        ttk.Label(metrics_frame, text="Диск:", font=("Arial", 12, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(10, 0))
        self.disk_total_label = ttk.Label(metrics_frame, text="")
        self.disk_total_label.grid(row=8, column=0, sticky=tk.W)
        self.disk_used_label = ttk.Label(metrics_frame, text="")
        self.disk_used_label.grid(row=9, column=0, sticky=tk.W)
        self.disk_percent_label = ttk.Label(metrics_frame, text="")
        self.disk_percent_label.grid(row=10, column=0, sticky=tk.W)

        # Блок отображения информации о сети
        ttk.Label(metrics_frame, text="Сеть:", font=("Arial", 12, "bold")).grid(row=11, column=0, sticky=tk.W, pady=(10, 0))
        self.network_recv_label = ttk.Label(metrics_frame, text="")
        self.network_recv_label.grid(row=12, column=0, sticky=tk.W)
        self.network_sent_label = ttk.Label(metrics_frame, text="")
        self.network_sent_label.grid(row=13, column=0, sticky=tk.W)

        # Фрейм для графика с заголовком и отступами
        graph_frame = ttk.LabelFrame(main_frame, text="Графики загрузки", padding="10")
        graph_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Создание фигуры matplotlib для отображения графика
        self.figure = Figure(figsize=(6, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, graph_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        
    def get_cpu_info(self):
        """
        Собирает информацию о загрузке центрального процессора.
        
        Returns:
            dict: Словарь с текущей загрузкой CPU и средней загрузкой за 1/5/15 минут.
                Поля:
                * current_usage (float): текущая загрузка CPU за 1 секунду, %.
                * load_avg (tuple): средняя загрузка за 1, 5, 15 минут (или "N/A" для Unix-систем).
        """
        current_usage = psutil.cpu_percent(interval=1)
        
        try:
            load_avg = psutil.getloadavg()
            avg1, avg5, avg15 = load_avg
        except AttributeError:
            avg1 = avg5 = avg15 = "N/A"
            
        return {
            "current_usage": current_usage,
            "load_avg": (avg1, avg5, avg15)
        }
        
    def get_memory_info(self):
        """
        Собирает информацию об использовании оперативной памяти (RAM).
        
        Returns:
            dict: Словарь с метриками памяти в гигабайтах и процентах.
                Поля:
                * total (float): общий объём RAM, ГБ.
                * available (float): доступная память, ГБ.
                * used (float): использованная память, ГБ.
                * percent (float): процент использования памяти.
        """
        
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024 ** 3)
        available_gb = memory.available / (1024 ** 3)
        used_gb = memory.used / (1024 ** 3)
        percent_used = memory.percent
        
        return {
            "total": round(total_gb, 2),
            "available": round(available_gb, 2),
            "used": round(used_gb, 2),
            "percent": round(percent_used, 1)
        }
        
    def get_disk_info(self, path="/"):
        """
        Собирает информацию об использовании дискового пространства.

        Args:
            path (str): Путь к разделу диска (по умолчанию корневой раздел).

        Returns:
            dict: Словарь с метриками диска в гигабайтах и процентах.
                  При ошибке возвращает словарь с ключом 'error' и сообщением.
                Поля:
                * path (str): путь к разделу;
                * total (float): общий объём диска, ГБ;
                * free (float): свободное место, ГБ;
                * used (float): занятое место, ГБ;
                * percent (float): процент использования диска.
        """
        try:
            disk_usage = psutil.disk_usage(path)
            total_gb = disk_usage.total / (1024 ** 3)
            free_gb = disk_usage.free / (1024 ** 3)
            used_gb = disk_usage.used / (1024 ** 3)
            percent_used = disk_usage.percent
        except FileNotFoundError:
            return {"error": f"Диск {path} не найден"}
        
        return {
            "path": path,
            "total": round(total_gb, 2),
            "free": round(free_gb, 2),
            "used": round(used_gb, 2),
            "percent": round(percent_used, 1)
        }
        
    def get_network_info(self):
        """
        Собирает информацию об использовании сети (объём переданных/полученных данных).

        Returns:
            dict: Словарь с объёмом данных в гигабайтах.
                  Поля:
                  * bytes_sent (float): объём отправленных данных с загрузки системы, ГБ;
                  * bytes_recv (float): объём полученных данных с загрузки системы, ГБ.
        """
        
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv
        
        def bytes_to_gb(bytes_value):
            """
            Конвертирует байты в гигабайты и округляет до 2 знаков после запятой.

            Args:
                bytes_value (int): Объём данных в байтах.

            Returns:
                float: Объём данных в гигабайтах.
            """
            return round(bytes_value / (1024 ** 3), 2)
        
        return {
            "bytes_sent": bytes_to_gb(bytes_sent),
            "bytes_recv": bytes_to_gb(bytes_recv)
        }
        
    def update_data(self):
        """
        Основной метод обновления данных:
        * получает актуальные метрики системы;
        * обновляет текстовые метки интерфейса;
        * добавляет новые значения в историю для графиков;
        * запускает обновление графика;
        * планирует следующее обновление через UPDATE_INTERVAL секунд.
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Время: {timestamp}")
        
        # Получаем актуальные данные системы
        cpu_data = self.get_cpu_info()
        mem_data = self.get_memory_info()
        disk_path_to_monitor = "/" if psutil.LINUX else "C:\\"
        disk_data = self.get_disk_info(disk_path_to_monitor)
        net_data = self.get_network_info()
        
        # Обновляем метки CPU
        self.cpu_current_label.config(
            text=f"Текущая загрузка: {cpu_data['current_usage']}%"
        )

        if cpu_data["load_avg"] != "N/A":
            avg1, avg5, avg15 = cpu_data["load_avg"]
            self.cpu_loadavg_label.config(
                text=f"Загрузка (1/5/15 мин): {avg1}%, {avg5}%, {avg15}%"
            )
        else:
            self.cpu_loadavg_label.config(
                text="Загрузка (1/5/15 мин): N/A, N/A, N/A"
            )

        # Обновляем метки памяти
        self.ram_total_label.config(
            text=f"Всего: {mem_data['total']} GB"
        )
        self.ram_used_label.config(
            text=f"Использовано: {mem_data['used']} GB"
        )
        self.ram_percent_label.config(
            text=f"Использование: {mem_data['percent']}%"
        )

        # Обновляем метки диска
        if "error" in disk_data:
            self.disk_total_label.config(text=f"Ошибка: {disk_data['error']}")
            self.disk_used_label.config(text="")
            self.disk_percent_label.config(text="")
        else:
            self.disk_total_label.config(
                text=f"Всего: {disk_data['total']} GB"
            )
            self.disk_used_label.config(
                text=f"Занято: {disk_data['used']} GB"
            )
            self.disk_percent_label.config(
                text=f"Использование: {disk_data['percent']}%"
            )

        # Обновляем метки сети
        self.network_recv_label.config(
            text=f"Получено: {net_data['bytes_recv']} GB"
        )
        self.network_sent_label.config(
            text=f"Отправлено: {net_data['bytes_sent']} GB"
        )

        # Добавляем текущие значения в историю для построения графиков
        self.cpu_history.append(cpu_data["current_usage"])
        self.ram_history.append(mem_data["percent"])

        # Ограничиваем историю последними 50 значениями (чтобы не перегружать память)
        if len(self.cpu_history) > 50:
            self.cpu_history.pop(0)
        if len(self.ram_history) > 50:
            self.ram_history.pop(0)
            
        # Обновляем график на основе накопленной истории
        self.update_graph()
        
        # Планируем следующее обновление данных через UPDATE_INTERVAL * 1000 мс
        self.root.after(UPDATE_INTERVAL * 1000, self.update_data)
        
    def update_graph(self):
        """
        Обновляет график загрузки CPU и RAM на основе накопленной истории данных.

        Очищает предыдущий график, строит новые линии для CPU (красный) и RAM (синий),
        добавляет подписи, сетку и настраивает оси.
        """
        
        self.ax.clear()
        
        x = list(range(len(self.cpu_history)))
        
        # Строим график CPU (красная линия)
        self.ax.plot(x, self.cpu_history, label='CPU %', color='red', linewidth=2)
        # Строим график RAM (синяя линия)
        self.ax.plot(x, self.ram_history, label='RAM %', color='blue', linewidth=2)

        # Настраиваем подписи осей и заголовок
        self.ax.set_xlabel('Время (обновления)')
        self.ax.set_ylabel('Загрузка (%)')
        self.ax.set_title('Мониторинг загрузки CPU и RAM')
        # Добавляем легенду и сетку для лучшей читаемости
        self.ax.legend()
        self.ax.grid(True)
        
        # Автоматическое масштабирование осей
        if x:
            self.ax.set_xlim(0, max(x))
        self.ax.set_ylim(0, 100) # Загрузка не может превышать 100 %
        
        # Перерисовываем холст с обновлённым графиком
        self.canvas.draw()
        
# --- Основная часть программы ---

if __name__ == "__main__":
    """
    Точка входа в программу.
    Создаёт коневое окно tkinter, инициализирует приложение мониторинга
    и запускает главный цикл обработки событий.
    """
        
    root = tk.Tk()
    app = SystemMonitorApp(root)
    root.mainloop()