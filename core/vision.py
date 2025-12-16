"""
Модуль компьютерного зрения для автоматического построения треугольника конуса
"""
import cv2
import numpy as np
from PIL import Image
from utils.logger import app_logger


def detect_cone_zif1(image: Image.Image) -> list[tuple[float, float]] | None:
    """
    Заглушка для алгоритма распознавания конуса ЗИФ1.
    Будет реализована позже.
    
    Args:
        image: PIL изображение
    
    Returns:
        Список из 3 точек [(x1, y1), (x2, y2), (x3, y3)] или None
    """
    app_logger.warning("Algorithm for ZIF1 cone detection is not implemented yet")
    return None


def detect_cone_zif2(image: Image.Image) -> list[tuple[float, float]] | None:
    """
    Заглушка для алгоритма распознавания конуса ЗИФ1.
    Будет реализована позже.
    
    Args:
        image: PIL изображение
    
    Returns:
        Список из 3 точек [(x1, y1), (x2, y2), (x3, y3)] или None
    """
    app_logger.warning("Algorithm for ZIF1 cone detection is not implemented yet")
    return None


def detect_cone_zif(image: Image.Image, roi_config: tuple[int, int, int, int] | list[int], cone_center: list[int], threshold: int = 80) -> list[tuple[float, float]] | None:
    """
    Автоматическое распознавание конуса ЗИФ2 и построение треугольника.
    Использует алгоритм на основе контурного анализа.
    
    Args:
        image: PIL изображение
        roi_config: ROI координаты в формате [x1, x2, y1, y2]
    
    Returns:
        Список из 3 точек [(x1, y1), (x2, y2), (x3, y3)] или None если не удалось
    """
    try:
        app_logger.info("Starting automatic cone detection for ZIF2")
        
        # Преобразуем PIL Image в OpenCV формат
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Проверяем наличие ROI координат
        if roi_config is None:
            app_logger.error("ROI configuration not provided")
            return None
        
        x1, x2, y1, y2 = roi_config
        app_logger.debug(f"ROI coordinates: x1={x1}, x2={x2}, y1={y1}, y2={y2}")
        
        # Проверяем границы
        h, w = img_cv.shape[:2]
        x2 = min(x2, w)
        y2 = min(y2, h)
        
        # Извлекаем ROI
        roi = img_cv[y1:y2, x1:x2].copy()
        app_logger.debug(f"ROI extracted: size={roi.shape}")
        
        # Преобразование в оттенки серого
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Бинаризация
        _, thresh_roi = cv2.threshold(gray_roi, threshold, 255, cv2.THRESH_BINARY_INV)
        
        # Морфологическая очистка
        kernel = np.ones((5, 5), np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        thresh_clean_roi = cv2.morphologyEx(thresh_roi, cv2.MORPH_OPEN, kernel)

        
        # Поиск контуров в ROI
        contours, _ = cv2.findContours(
            thresh_clean_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            app_logger.warning("No contours found in ROI")
            return None
        
        # Находим самый большой контур
        largest_contour = max(contours, key=cv2.contourArea)
        app_logger.debug(f"Largest contour area: {cv2.contourArea(largest_contour)}")
        
        # Получаем все точки контура
        points = largest_contour.reshape(-1, 2)
        
        # Получаем параметры центральной зоны из конфигурации
        # cone_center = CAM_CONE_ZIF2.get("cone_center", [40, 60])
        center_x_min_pct, center_x_max_pct = cone_center
        
        # Ищем вершину пирамиды в центральной зоне
        roi_width = x2 - x1
        center_x_min = int(roi_width * center_x_min_pct / 100)
        center_x_max = int(roi_width * center_x_max_pct / 100)
        
        # Фильтруем точки в центральной зоне
        central_points = points[
            (points[:, 0] >= center_x_min) & (points[:, 0] <= center_x_max)
        ]
        
        if len(central_points) > 0:
            # Берём самую высокую точку среди центральных
            peak_point = central_points[np.argmin(central_points[:, 1])]
            app_logger.debug(f"Peak point found in central zone: {peak_point}")
        else:
            # Если нет центральных точек — берём общую самую высокую
            peak_point = points[np.argmin(points[:, 1])]
            app_logger.warning(f"No central points, using highest point: {peak_point}")
        
        # Левая и правая точки — самые крайние по X в нижних 20% ROI
        roi_height = y2 - y1
        bottom_threshold = roi_height * 0.6 #0.8  # Точки должны быть в нижних 20% (выше 80% высоты)
        
        # Фильтруем точки в нижней части ROI
        bottom_points = points[points[:, 1] >= bottom_threshold]
        
        if len(bottom_points) == 0:
            app_logger.warning("No points found in bottom 20% of ROI, using all points")
            bottom_points = points
        
        # Находим самые крайние точки по X среди нижних точек
        left_point = bottom_points[np.argmin(bottom_points[:, 0])]
        right_point = bottom_points[np.argmax(bottom_points[:, 0])]
        
        app_logger.debug(f"Triangle points - Left: {left_point}, Right: {right_point}, Peak: {peak_point}")
        app_logger.debug(f"Bottom threshold: {bottom_threshold}, ROI height: {roi_height}")
        
        # Преобразуем координаты из ROI в глобальную систему координат
        left_global = (float(left_point[0] + x1), float(left_point[1] + y1))
        right_global = (float(right_point[0] + x1), float(right_point[1] + y1))
        peak_global = (float(peak_point[0] + x1), float(peak_point[1] + y1))
        
        # Возвращаем треугольник: [левая, правая, вершина]
        triangle_points = [left_global, right_global, peak_global]
        
        app_logger.info(f"Triangle detected successfully: {triangle_points}")
        return triangle_points
        
    except Exception as e:
        app_logger.error(f"Error in cone detection: {e}", exc_info=True)
        return None



def auto_detect_triangle(image: Image.Image, cone_type: str, threshold: int | None = None, cam_config: dict | None = None) -> list[tuple[float, float]] | None:
    """
    Автоматическое построение треугольника на основе типа конуса.
    
    Args:
        image: PIL изображение
        cone_type: Тип конуса ("ZIF1" или "ZIF2")
        threshold: Порог бинаризации (если None, используется значение из конфигурации)
        cam_config: Конфигурация камеры (если None, используются значения по умолчанию)
    
    Returns:
        Список из 3 точек [(x1, y1), (x2, y2), (x3, y3)] или None
    """
    app_logger.info(f"Auto-detecting triangle for cone type: {cone_type}")
    
    # Значения по умолчанию
    default_configs = {
        "ZIF1": {
            "roi": [1125, 1545, 345, 615],
            "cone_center": [45, 65],
            "threshold": 50
        },
        "ZIF2": {
            "roi": [716, 1180, 170, 360],
            "cone_center": [40, 60],
            "threshold": 85
        }
    }
    
    if cone_type not in default_configs:
        app_logger.error(f"Unknown cone type: {cone_type}")
        return None
    
    # Используем переданную конфигурацию или значения по умолчанию
    if cam_config is None:
        cam_config = default_configs[cone_type]
    
    roi = cam_config.get("roi", default_configs[cone_type]["roi"])
    cone_center = cam_config.get("cone_center", default_configs[cone_type]["cone_center"])
    thresh = threshold if threshold is not None else cam_config.get("threshold", default_configs[cone_type]["threshold"])
    
    return detect_cone_zif(image, roi, cone_center, thresh)
