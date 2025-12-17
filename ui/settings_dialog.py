"""
Диалоговое окно настроек приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox
from utils.logger import app_logger


class SettingsDialog:
    """Диалоговое окно для редактирования настроек камер"""
    
    def __init__(self, parent, config):
        """
        Инициализация диалога настроек.
        
        Args:
            parent: Родительское окно
            config: Объект конфигурации
        """
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()
        
        # Словари для хранения переменных полей ввода
        self.zif1_vars = {}
        self.zif2_vars = {}
        
        self._create_widgets()
        self._load_current_config()
        
        # Центрируем окно относительно родителя
        self.window.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.window.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
        
        app_logger.info("Settings dialog opened")
    
    def _create_widgets(self):
        """Создание виджетов окна настроек"""
        # Основной фрейм с прокруткой
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Создаём Notebook для вкладок
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        # Вкладка для ЗИФ1
        zif1_frame = ttk.Frame(notebook, padding=10)
        notebook.add(zif1_frame, text="Конус ЗИФ-1")
        self._create_camera_settings(zif1_frame, "ZIF1")
        
        # Вкладка для ЗИФ2
        zif2_frame = ttk.Frame(notebook, padding=10)
        notebook.add(zif2_frame, text="Конус ЗИФ-2")
        self._create_camera_settings(zif2_frame, "ZIF2")
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(5, 0))
        
        # Кнопка "По умолчанию"
        default_btn = ttk.Button(
            button_frame,
            text="По умолчанию",
            command=self._restore_defaults
        )
        default_btn.pack(side='left', padx=5)
        
        # Кнопка "Сохранить"
        save_btn = ttk.Button(
            button_frame,
            text="Сохранить",
            command=self._save_settings
        )
        save_btn.pack(side='right', padx=5)
        
        # Кнопка "Отмена"
        cancel_btn = ttk.Button(
            button_frame,
            text="Отмена",
            command=self.window.destroy
        )
        cancel_btn.pack(side='right', padx=5)
    
    def _create_camera_settings(self, parent, camera_type):
        """
        Создание полей настроек для камеры.
        
        Args:
            parent: Родительский фрейм
            camera_type: "ZIF1" или "ZIF2"
        """
        # Определяем словарь переменных для текущей камеры
        vars_dict = self.zif1_vars if camera_type == "ZIF1" else self.zif2_vars
        
        row = 0
        
        # IP адрес Trassir
        ttk.Label(parent, text="IP адрес Trassir:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['trassir_ip'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['trassir_ip'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Имя канала
        ttk.Label(parent, text="Имя канала:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['chanel_name'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['chanel_name'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Пароль
        ttk.Label(parent, text="Пароль Trassir:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['password'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['password'], width=40, show='*').grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Размер пикселя
        ttk.Label(parent, text="Размер пикселя (м):").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['pixel_size_m'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['pixel_size_m'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Коэффициент объёма
        ttk.Label(parent, text="Коэффициент объёма:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['k_vol'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['k_vol'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Коэффициент плотности
        ttk.Label(parent, text="Плотность (т/м³):").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['k_den'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['k_den'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Порог бинаризации
        ttk.Label(parent, text="Порог бинаризации:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['threshold'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['threshold'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # ROI (Region of Interest)
        ttk.Label(parent, text="ROI [x1, x2, y1, y2]:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['roi'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['roi'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Центр конуса
        ttk.Label(parent, text="Центр конуса [min%, max%]:").grid(
            row=row, column=0, sticky='w', pady=5, padx=5)
        vars_dict['cone_center'] = tk.StringVar()
        ttk.Entry(parent, textvariable=vars_dict['cone_center'], width=40).grid(
            row=row, column=1, sticky='ew', pady=5, padx=5)
        row += 1
        
        # Настраиваем растягивание столбца
        parent.columnconfigure(1, weight=1)
    
    def _load_current_config(self):
        """Загрузка текущих значений из конфигурации"""
        # Загружаем настройки ZIF1
        zif1_config = self.config.get("CAM_CONE_ZIF1", {})
        self.zif1_vars['trassir_ip'].set(zif1_config.get('trassir_ip', ''))
        self.zif1_vars['chanel_name'].set(zif1_config.get('chanel_name', ''))
        self.zif1_vars['password'].set(zif1_config.get('password', 'master'))
        self.zif1_vars['pixel_size_m'].set(str(zif1_config.get('pixel_size_m', '')))
        self.zif1_vars['k_vol'].set(str(zif1_config.get('k_vol', '')))
        self.zif1_vars['k_den'].set(str(zif1_config.get('k_den', '')))
        self.zif1_vars['threshold'].set(str(zif1_config.get('threshold', '')))
        self.zif1_vars['roi'].set(str(zif1_config.get('roi', [])))
        self.zif1_vars['cone_center'].set(str(zif1_config.get('cone_center', [])))
        
        # Загружаем настройки ZIF2
        zif2_config = self.config.get("CAM_CONE_ZIF2", {})
        self.zif2_vars['trassir_ip'].set(zif2_config.get('trassir_ip', ''))
        self.zif2_vars['chanel_name'].set(zif2_config.get('chanel_name', ''))
        self.zif2_vars['password'].set(zif2_config.get('password', 'master'))
        self.zif2_vars['pixel_size_m'].set(str(zif2_config.get('pixel_size_m', '')))
        self.zif2_vars['k_vol'].set(str(zif2_config.get('k_vol', '')))
        self.zif2_vars['k_den'].set(str(zif2_config.get('k_den', '')))
        self.zif2_vars['threshold'].set(str(zif2_config.get('threshold', '')))
        self.zif2_vars['roi'].set(str(zif2_config.get('roi', [])))
        self.zif2_vars['cone_center'].set(str(zif2_config.get('cone_center', [])))
        
        app_logger.debug("Current config loaded into settings dialog")
    
    def _parse_list_field(self, value_str):
        """
        Парсинг строки в список.
        
        Args:
            value_str: Строка вида "[1, 2, 3, 4]"
        
        Returns:
            Список чисел или None при ошибке
        """
        try:
            # Убираем пробелы и скобки
            cleaned = value_str.strip().strip('[]')
            if not cleaned:
                return []
            # Разделяем по запятой и конвертируем в числа
            return [int(x.strip()) for x in cleaned.split(',')]
        except (ValueError, AttributeError) as e:
            app_logger.error(f"Failed to parse list field: {value_str}, error: {e}")
            return None
    
    def _save_settings(self):
        """Сохранение настроек в config.json"""
        try:
            # Собираем данные для ZIF1
            zif1_data = {
                'trassir_ip': self.zif1_vars['trassir_ip'].get().strip(),
                'chanel_name': self.zif1_vars['chanel_name'].get().strip(),
                'password': self.zif1_vars['password'].get().strip() or 'master',
                'pixel_size_m': float(self.zif1_vars['pixel_size_m'].get()),
                'k_vol': float(self.zif1_vars['k_vol'].get()),
                'k_den': float(self.zif1_vars['k_den'].get()),
                'threshold': int(self.zif1_vars['threshold'].get()),
                'roi': self._parse_list_field(self.zif1_vars['roi'].get()),
                'cone_center': self._parse_list_field(self.zif1_vars['cone_center'].get())
            }
            
            # Собираем данные для ZIF2
            zif2_data = {
                'trassir_ip': self.zif2_vars['trassir_ip'].get().strip(),
                'chanel_name': self.zif2_vars['chanel_name'].get().strip(),
                'password': self.zif2_vars['password'].get().strip() or 'master',
                'pixel_size_m': float(self.zif2_vars['pixel_size_m'].get()),
                'k_vol': float(self.zif2_vars['k_vol'].get()),
                'k_den': float(self.zif2_vars['k_den'].get()),
                'threshold': int(self.zif2_vars['threshold'].get()),
                'roi': self._parse_list_field(self.zif2_vars['roi'].get()),
                'cone_center': self._parse_list_field(self.zif2_vars['cone_center'].get())
            }
            
            # Проверяем корректность списков
            if zif1_data['roi'] is None or zif1_data['cone_center'] is None:
                raise ValueError("Некорректный формат списков для ZIF1")
            if zif2_data['roi'] is None or zif2_data['cone_center'] is None:
                raise ValueError("Некорректный формат списков для ZIF2")
            
            # Сохраняем в конфигурацию
            self.config.set("CAM_CONE_ZIF1", zif1_data)
            self.config.set("CAM_CONE_ZIF2", zif2_data)
            
            app_logger.info("Settings saved successfully")
            messagebox.showinfo("Успех", "Настройки сохранены успешно!")
            self.window.destroy()
            
        except ValueError as e:
            app_logger.error(f"Invalid input in settings: {e}")
            messagebox.showerror(
                "Ошибка", 
                f"Некорректные данные:\n{str(e)}\n\nПроверьте правильность введённых значений."
            )
        except Exception as e:
            app_logger.error(f"Error saving settings: {e}")
            messagebox.showerror(
                "Ошибка", 
                f"Ошибка при сохранении настроек:\n{str(e)}"
            )
    
    def _restore_defaults(self):
        """Восстановление значений по умолчанию из constants.py"""
        try:
            from utils.constants import CAM_CONE_ZIF1, CAM_CONE_ZIF2
            
            # Восстанавливаем ZIF1
            self.zif1_vars['trassir_ip'].set(CAM_CONE_ZIF1.get('trassir_ip', ''))
            self.zif1_vars['chanel_name'].set(CAM_CONE_ZIF1.get('chanel_name', ''))
            self.zif1_vars['password'].set(CAM_CONE_ZIF1.get('password', 'master'))
            self.zif1_vars['pixel_size_m'].set(str(CAM_CONE_ZIF1.get('pixel_size_m', '')))
            self.zif1_vars['k_vol'].set(str(CAM_CONE_ZIF1.get('k_vol', '')))
            self.zif1_vars['k_den'].set(str(CAM_CONE_ZIF1.get('k_den', '')))
            self.zif1_vars['threshold'].set(str(CAM_CONE_ZIF1.get('threshold', '')))
            self.zif1_vars['roi'].set(str(CAM_CONE_ZIF1.get('roi', [])))
            self.zif1_vars['cone_center'].set(str(CAM_CONE_ZIF1.get('cone_center', [])))
            
            # Восстанавливаем ZIF2
            self.zif2_vars['trassir_ip'].set(CAM_CONE_ZIF2.get('trassir_ip', ''))
            self.zif2_vars['chanel_name'].set(CAM_CONE_ZIF2.get('chanel_name', ''))
            self.zif2_vars['password'].set(CAM_CONE_ZIF2.get('password', 'master'))
            self.zif2_vars['pixel_size_m'].set(str(CAM_CONE_ZIF2.get('pixel_size_m', '')))
            self.zif2_vars['k_vol'].set(str(CAM_CONE_ZIF2.get('k_vol', '')))
            self.zif2_vars['k_den'].set(str(CAM_CONE_ZIF2.get('k_den', '')))
            self.zif2_vars['threshold'].set(str(CAM_CONE_ZIF2.get('threshold', '')))
            self.zif2_vars['roi'].set(str(CAM_CONE_ZIF2.get('roi', [])))
            self.zif2_vars['cone_center'].set(str(CAM_CONE_ZIF2.get('cone_center', [])))
            
            app_logger.info("Settings restored to defaults from constants.py")
            messagebox.showinfo("Успех", "Настройки восстановлены по умолчанию из constants.py")
            
        except Exception as e:
            app_logger.error(f"Error restoring defaults: {e}")
            messagebox.showerror(
                "Ошибка", 
                f"Ошибка при восстановлении настроек:\n{str(e)}"
            )
