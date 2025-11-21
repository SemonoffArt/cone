"""
Главный файл приложения Cone
"""
from ui.main_window import MainWindow
from utils.logger import app_logger

def main():
    """Основная функция приложения"""
    app_logger.info("Starting Cone application")
    try:
        app = MainWindow()
        app.run()
        app_logger.info("Application finished successfully")
    except Exception as e:
        app_logger.error(f"Application failed with error: {e}")
        raise

if __name__ == "__main__":
    main()