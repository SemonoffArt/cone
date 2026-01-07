"""
Flask Web Application для расчёта объёма конуса
"""
import os
import io
import base64
from flask import Flask, render_template, request, jsonify, session
from PIL import Image
import numpy as np

# Импорты из существующих модулей
from core.vision import auto_detect_triangle
from core.cone_calculator import ConeCalculator
from core.geometry import calculate_side_length
from utils.config import Config
from utils.logger import app_logger
from utils.trassir import Trassir

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Секретный ключ для сессий

# Инициализация конфигурации
config = Config()

# Папка для временных загрузок
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


@app.route('/')
def index():
    """Главная страница"""
    # Загружаем настройки из конфига
    cam_zif1 = config.get("CAM_CONE_ZIF1", {})
    cam_zif2 = config.get("CAM_CONE_ZIF2", {})
    
    return render_template('index.html',
                         cam_zif1=cam_zif1,
                         cam_zif2=cam_zif2)


@app.route('/upload', methods=['POST'])
def upload_image():
    """Загрузка изображения"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Читаем изображение
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))
        
        # Сохраняем на диск
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'current_image.png')
        image.save(image_path, 'PNG')
        
        # Сохраняем только имя файла в сессии
        session['current_image_path'] = image_path
        session['image_size'] = [image.width, image.height]
        
        # Конвертируем в base64 только для отправки
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        app_logger.info(f"Image uploaded: {image.width}x{image.height}")
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{img_base64}',
            'width': image.width,
            'height': image.height
        })
    
    except Exception as e:
        app_logger.error(f"Error uploading image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/load_trassir/<cone_type>', methods=['POST'])
def load_trassir(cone_type):
    """Загрузка изображения с Trassir"""
    try:
        # Получаем настройки камеры
        cam_key = f"CAM_CONE_{cone_type.upper()}"
        cam_config = config.get(cam_key)
        
        if not cam_config:
            return jsonify({'error': f'Camera {cone_type} not configured'}), 400
        
        # Подключаемся к Trassir
        trassir_ip = cam_config.get('trassir_ip')
        channel_name = cam_config.get('chanel_name')
        password = cam_config.get('password', 'master')
        
        app_logger.info(f"Connecting to Trassir at {trassir_ip} for {cone_type}")
        
        trassir = Trassir(ip=trassir_ip, password=password)
        channel = trassir.get_channel_by_name(channel_name)
        
        if not channel:
            app_logger.error(f"Channel {channel_name} not found")
            return jsonify({'error': f'Channel {channel_name} not found'}), 404
        
        # Получаем скриншот
        screenshot = trassir.get_channel_screenshot(channel['guid'])
        
        if not screenshot:
            app_logger.error('Failed to get screenshot')
            return jsonify({'error': 'Failed to get screenshot'}), 500
        
        # Сохраняем на диск
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'current_image.png')
        screenshot.save(image_path, 'PNG')
        
        # Сохраняем только путь в сессии
        session['current_image_path'] = image_path
        session['image_size'] = [screenshot.width, screenshot.height]
        session['current_cone_type'] = cone_type.upper()
        
        # Конвертируем в base64 только для отправки
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        app_logger.info(f"Loaded screenshot from Trassir {cone_type}: {screenshot.width}x{screenshot.height}")
        
        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{img_base64}',
            'width': screenshot.width,
            'height': screenshot.height,
            'cone_type': cone_type.upper()
        })
    
    except ValueError as e:
        # Ошибка аутентификации или подключения
        app_logger.error(f"Trassir connection error: {e}")
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        app_logger.error(f"Error loading from Trassir: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/auto_detect', methods=['POST'])
def auto_detect():
    """Автоматическое определение треугольника"""
    try:
        data = request.json
        threshold = data.get('threshold', 50)
        
        # Получаем изображение с диска
        if 'current_image_path' not in session:
            return jsonify({'error': 'No image loaded'}), 400
        
        image_path = session['current_image_path']
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image file not found'}), 400
        
        image = Image.open(image_path)
        
        # Получаем тип конуса из сессии (если загружено с Trassir)
        cone_type = session.get('current_cone_type', 'ZIF1')  # По умолчанию ZIF1
        
        # Запускаем автоопределение
        vertices = auto_detect_triangle(
            image,
            cone_type=cone_type,
            threshold=threshold
        )
        
        if vertices and len(vertices) == 3:
            app_logger.info(f"Triangle auto-detected: {vertices}")
            return jsonify({
                'success': True,
                'vertices': vertices
            })
        else:
            return jsonify({'error': 'Failed to detect triangle'}), 400
    
    except Exception as e:
        app_logger.error(f"Error in auto-detection: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/calculate', methods=['POST'])
def calculate():
    """Расчёт объёма конуса"""
    try:
        data = request.json
        vertices = data.get('vertices', [])
        pixel_size = data.get('pixel_size', 0.1)
        k_vol = data.get('k_vol', 1.0)
        k_den = data.get('k_den', 1.7)
        
        if len(vertices) != 3:
            return jsonify({'error': 'Need exactly 3 vertices'}), 400
        
        # Вычисляем стороны треугольника
        sides = []
        side_names = ['AB', 'BC', 'CA']
        for i in range(3):
            v1 = vertices[i]
            v2 = vertices[(i + 1) % 3]
            length_px, length_m = calculate_side_length(v1, v2, pixel_size)
            sides.append({
                'name': side_names[i],
                'length_px': length_px,
                'length_m': length_m
            })
        
        # Вычисляем объём конуса
        cone_params = ConeCalculator.get_cone_parameters(
            vertices, 
            pixel_size, 
            scale_factor=1.0,  # Уже в оригинальных координатах
            k_vol=k_vol
        )
        
        # Вычисляем массу
        mass = cone_params['volume'] * k_den
        
        app_logger.info(f"Calculated: Volume={cone_params['volume']:.2f} m³, Mass={mass:.2f} т")
        
        return jsonify({
            'success': True,
            'sides': sides,
            'cone': {
                'volume': cone_params['volume'],
                'radius_m': cone_params['radius_m'],
                'height_m': cone_params['height_m'],
                'mass': mass
            }
        })
    
    except Exception as e:
        app_logger.error(f"Error in calculation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Управление конфигурацией"""
    if request.method == 'GET':
        # Возвращаем текущую конфигурацию
        return jsonify({
            'CAM_CONE_ZIF1': config.get('CAM_CONE_ZIF1', {}),
            'CAM_CONE_ZIF2': config.get('CAM_CONE_ZIF2', {})
        })
    
    elif request.method == 'POST':
        # Обновляем конфигурацию
        try:
            data = request.json
            camera_name = data.get('camera_name')
            camera_config = data.get('config')
            
            if not camera_name or not camera_config:
                return jsonify({'error': 'Invalid data'}), 400
            
            config.set(camera_name, camera_config)
            app_logger.info(f"Configuration updated for {camera_name}")
            
            return jsonify({'success': True})
        
        except Exception as e:
            app_logger.error(f"Error updating config: {e}")
            return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app_logger.info("Starting Flask web application")
    app.run(debug=True, host='0.0.0.0', port=5000)
