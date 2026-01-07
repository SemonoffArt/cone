// Глобальные переменные
let canvas, ctx;
let currentImage = null;
let vertices = [];
let draggingVertex = null;
let imageScale = 1.0;
let imageOffset = { x: 0, y: 0 };

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('main-canvas');
    ctx = canvas.getContext('2d');
    
    initializeEventListeners();
    updateStatus('Готов к работе');
});

// Инициализация обработчиков событий
function initializeEventListeners() {
    // Кнопки загрузки
    document.getElementById('load-file-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });
    
    document.getElementById('file-input').addEventListener('change', handleFileUpload);
    document.getElementById('load-zif1-btn').addEventListener('click', () => loadTrassir('ZIF1'));
    document.getElementById('load-zif2-btn').addEventListener('click', () => loadTrassir('ZIF2'));
    
    // Кнопки действий
    document.getElementById('auto-build-btn').addEventListener('click', autoDetectTriangle);
    document.getElementById('clear-btn').addEventListener('click', clearTriangle);
    document.getElementById('calculate-btn').addEventListener('click', calculateVolume);
    
    // Canvas события
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    
    // Настройки
    document.getElementById('settings-btn').addEventListener('click', openSettingsModal);
    document.querySelector('.close').addEventListener('click', closeSettingsModal);
    document.getElementById('save-settings-btn').addEventListener('click', saveSettings);
    document.getElementById('cancel-settings-btn').addEventListener('click', closeSettingsModal);
    
    // Обновление информации при изменении размера пикселя
    document.getElementById('pixel-size').addEventListener('input', function() {
        if (vertices.length === 3) {
            updateTriangleInfo();
        }
    });
    
    // Обновление при изменении коэффициентов
    document.getElementById('k-vol').addEventListener('input', function() {
        if (vertices.length === 3) {
            autoCalculateVolume();
        }
    });
    
    document.getElementById('k-den').addEventListener('input', function() {
        if (vertices.length === 3) {
            autoCalculateVolume();
        }
    });
    
    // Вкладки
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
    
    // Закрытие модального окна при клике вне его
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('settings-modal');
        if (event.target === modal) {
            closeSettingsModal();
        }
    });
}

// Загрузка файла
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    updateStatus('Загрузка изображения...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadImageToCanvas(data.image_data, data.width, data.height);
            updateImageInfo(data.width, data.height, 'Локальный файл');
            updateStatus('Изображение загружено');
            clearTriangle();
        } else {
            updateStatus('Ошибка загрузки: ' + data.error);
        }
    } catch (error) {
        console.error('Upload error:', error);
        updateStatus('Ошибка загрузки изображения');
    }
}

// Загрузка с Trassir
async function loadTrassir(coneType) {
    updateStatus(`Загрузка с Trassir ${coneType}...`);
    
    try {
        const response = await fetch(`/load_trassir/${coneType}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            loadImageToCanvas(data.image_data, data.width, data.height);
            updateImageInfo(data.width, data.height, `Trassir ${coneType}`);
            updateStatus(`Изображение загружено с ${coneType}`);
            clearTriangle();
            
            // Загружаем настройки для этой камеры
            loadCameraSettings(coneType);
        } else {
            updateStatus('Ошибка: ' + data.error);
            alert('Ошибка подключения к Trassir:\n' + data.error);
        }
    } catch (error) {
        console.error('Trassir load error:', error);
        updateStatus('Ошибка подключения к Trassir');
        alert('Ошибка подключения к Trassir');
    }
}

// Загрузка настроек камеры
async function loadCameraSettings(coneType) {
    try {
        const response = await fetch('/config');
        const config = await response.json();
        const camConfig = config[`CAM_CONE_${coneType}`];
        
        if (camConfig) {
            document.getElementById('pixel-size').value = camConfig.pixel_size_m;
            document.getElementById('k-vol').value = camConfig.k_vol;
            document.getElementById('k-den').value = camConfig.k_den;
            document.getElementById('threshold').value = camConfig.threshold;
        }
    } catch (error) {
        console.error('Error loading camera settings:', error);
    }
}

// Отображение изображения на canvas
function loadImageToCanvas(imageSrc, originalWidth, originalHeight) {
    const img = new Image();
    img.onload = function() {
        currentImage = img;
        
        // Вычисляем масштаб для вмещения изображения
        const scaleX = canvas.width / img.width;
        const scaleY = canvas.height / img.height;
        imageScale = Math.min(scaleX, scaleY, 1.0);
        
        // Вычисляем смещение для центрирования
        const scaledWidth = img.width * imageScale;
        const scaledHeight = img.height * imageScale;
        imageOffset.x = (canvas.width - scaledWidth) / 2;
        imageOffset.y = (canvas.height - scaledHeight) / 2;
        
        redrawCanvas();
    };
    img.src = imageSrc;
}

// Перерисовка canvas
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (currentImage) {
        const scaledWidth = currentImage.width * imageScale;
        const scaledHeight = currentImage.height * imageScale;
        ctx.drawImage(currentImage, imageOffset.x, imageOffset.y, scaledWidth, scaledHeight);
    }
    
    // Рисуем треугольник
    if (vertices.length > 0) {
        drawTriangle();
    }
}

// Отрисовка треугольника
function drawTriangle() {
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.fillStyle = 'rgba(0, 255, 0, 0.1)';
    
    // Рисуем линии
    if (vertices.length >= 2) {
        ctx.beginPath();
        ctx.moveTo(vertices[0].x, vertices[0].y);
        for (let i = 1; i < vertices.length; i++) {
            ctx.lineTo(vertices[i].x, vertices[i].y);
        }
        if (vertices.length === 3) {
            ctx.closePath();
            ctx.fill();
        }
        ctx.stroke();
    }
    
    // Рисуем вершины
    vertices.forEach((vertex, index) => {
        ctx.fillStyle = '#ff0000';
        ctx.beginPath();
        ctx.arc(vertex.x, vertex.y, 5, 0, 2 * Math.PI);
        ctx.fill();
        
        // Подписи вершин
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 3;
        ctx.font = 'bold 14px Arial';
        const label = ['A', 'B', 'C'][index];
        ctx.strokeText(label, vertex.x + 10, vertex.y - 10);
        ctx.fillText(label, vertex.x + 10, vertex.y - 10);
    });
    
    // Рисуем длины сторон
    if (vertices.length === 3) {
        drawSideLabels();
    }
    
    // Обновляем информационную панель
    if (vertices.length === 3) {
        updateTriangleInfo();
    } else if (vertices.length === 0) {
        clearTriangleInfo();
    }
}

// Отрисовка подписей длин сторон
function drawSideLabels() {
    const pixelSize = parseFloat(document.getElementById('pixel-size').value) || 0.1;
    const sideNames = ['AB', 'BC', 'CA'];
    
    for (let i = 0; i < 3; i++) {
        const v1 = vertices[i];
        const v2 = vertices[(i + 1) % 3];
        
        // Вычисляем длину в пикселях (на оригинальном изображении)
        const dx = (v2.x - v1.x) / imageScale;
        const dy = (v2.y - v1.y) / imageScale;
        const lengthPx = Math.sqrt(dx * dx + dy * dy);
        const lengthM = lengthPx * pixelSize;
        
        // Середина стороны
        const midX = (v1.x + v2.x) / 2;
        const midY = (v1.y + v2.y) / 2;
        
        // Текст
        const label = `${sideNames[i]}: ${lengthPx.toFixed(0)}px (${lengthM.toFixed(2)}м)`;
        
        // Рисуем с фоном
        ctx.font = 'bold 12px Arial';
        const metrics = ctx.measureText(label);
        const textWidth = metrics.width;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(midX - textWidth / 2 - 4, midY - 18, textWidth + 8, 20);
        
        ctx.fillStyle = '#ffff00';
        ctx.fillText(label, midX - textWidth / 2, midY - 4);
    }
}

// Обработка клика на canvas
function handleCanvasClick(event) {
    if (vertices.length >= 3) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    vertices.push({ x, y });
    redrawCanvas();
    
    if (vertices.length === 3) {
        updateStatus('Треугольник построен. Нажмите "Рассчитать"');
    } else {
        updateStatus(`Установлена вершина ${vertices.length}/3`);
    }
}

// Обработка нажатия мыши (для перетаскивания)
function handleMouseDown(event) {
    if (vertices.length !== 3) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Ищем ближайшую вершину
    for (let i = 0; i < vertices.length; i++) {
        const dx = x - vertices[i].x;
        const dy = y - vertices[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < 10) {
            draggingVertex = i;
            canvas.style.cursor = 'move';
            break;
        }
    }
}

// Обработка движения мыши
function handleMouseMove(event) {
    if (draggingVertex === null) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    vertices[draggingVertex] = { x, y };
    redrawCanvas();
}

// Обработка отпускания мыши
function handleMouseUp() {
    if (draggingVertex !== null) {
        draggingVertex = null;
        canvas.style.cursor = 'crosshair';
        updateStatus('Вершина перемещена. Нажмите "Рассчитать"');
        // Обновляем информацию о сторонах
        updateTriangleInfo();
    }
}

// Автоматическое определение треугольника
async function autoDetectTriangle() {
    if (!currentImage) {
        alert('Сначала загрузите изображение');
        return;
    }
    
    updateStatus('Автоопределение треугольника...');
    
    const threshold = parseInt(document.getElementById('threshold').value) || 50;
    
    try {
        const response = await fetch('/auto_detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ threshold })
        });
        
        const data = await response.json();
        
        if (data.success && data.vertices) {
            // Конвертируем координаты в canvas координаты
            vertices = data.vertices.map(v => ({
                x: v[0] * imageScale + imageOffset.x,
                y: v[1] * imageScale + imageOffset.y
            }));
            
            redrawCanvas();
            updateStatus('Треугольник найден автоматически');
        } else {
            updateStatus('Не удалось найти треугольник');
            alert('Автоопределение не удалось. Постройте треугольник вручную.');
        }
    } catch (error) {
        console.error('Auto-detect error:', error);
        updateStatus('Ошибка автоопределения');
    }
}

// Очистка треугольника
function clearTriangle() {
    vertices = [];
    redrawCanvas();
    clearConeInfo();
    updateStatus('Треугольник очищен');
}

// Расчёт объёма
async function calculateVolume() {
    if (vertices.length !== 3) {
        alert('Постройте треугольник (3 вершины)');
        return;
    }
    
    updateStatus('Расчёт объёма...');
    
    const pixelSize = parseFloat(document.getElementById('pixel-size').value) || 0.1;
    const kVol = parseFloat(document.getElementById('k-vol').value) || 1.0;
    const kDen = parseFloat(document.getElementById('k-den').value) || 1.7;
    
    // Конвертируем координаты обратно в координаты оригинального изображения
    const originalVertices = vertices.map(v => [
        (v.x - imageOffset.x) / imageScale,
        (v.y - imageOffset.y) / imageScale
    ]);
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vertices: originalVertices,
                pixel_size: pixelSize,
                k_vol: kVol,
                k_den: kDen
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.sides, data.cone);
            updateStatus('Расчёт завершён');
        } else {
            updateStatus('Ошибка расчёта: ' + data.error);
        }
    } catch (error) {
        console.error('Calculate error:', error);
        updateStatus('Ошибка расчёта');
    }
}

// Автоматический расчёт объёма (без alert и обновления статуса)
async function autoCalculateVolume() {
    if (vertices.length !== 3) {
        return;
    }
    
    const pixelSize = parseFloat(document.getElementById('pixel-size').value) || 0.1;
    const kVol = parseFloat(document.getElementById('k-vol').value) || 1.0;
    const kDen = parseFloat(document.getElementById('k-den').value) || 1.7;
    
    // Конвертируем координаты обратно в координаты оригинального изображения
    const originalVertices = vertices.map(v => [
        (v.x - imageOffset.x) / imageScale,
        (v.y - imageOffset.y) / imageScale
    ]);
    
    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vertices: originalVertices,
                pixel_size: pixelSize,
                k_vol: kVol,
                k_den: kDen
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data.sides, data.cone);
        }
    } catch (error) {
        console.error('Auto-calculate error:', error);
    }
}

// Отображение результатов
function displayResults(sides, cone) {
    // Стороны треугольника
    const sideNames = ['AB', 'BC', 'CA'];
    sides.forEach((side, index) => {
        const elem = document.getElementById(`side-${sideNames[index].toLowerCase()}`);
        elem.textContent = `Сторона ${sideNames[index]}: ${side.length_px.toFixed(1)} px (${side.length_m.toFixed(2)} m)`;
    });
    
    // Параметры конуса
    document.getElementById('volume-value').textContent = `Объем: ${cone.volume.toFixed(2)} m³`;
    document.getElementById('mass-value').textContent = `Масса: ${cone.mass.toFixed(2)} т`;
    document.getElementById('params-value').textContent = 
        `Радиус: ${cone.radius_m.toFixed(2)} m, Высота: ${cone.height_m.toFixed(2)} m`;
}

// Очистка информации о конусе
function clearConeInfo() {
    document.getElementById('volume-value').textContent = 'Объем: -';
    document.getElementById('mass-value').textContent = 'Масса: -';
    document.getElementById('params-value').textContent = 'Параметры конуса: -';
    document.getElementById('side-ab').textContent = 'Сторона AB: -';
    document.getElementById('side-bc').textContent = 'Сторона BC: -';
    document.getElementById('side-ca').textContent = 'Сторона CA: -';
}

// Очистка только информации о треугольнике
function clearTriangleInfo() {
    document.getElementById('side-ab').textContent = 'Сторона AB: -';
    document.getElementById('side-bc').textContent = 'Сторона BC: -';
    document.getElementById('side-ca').textContent = 'Сторона CA: -';
}

// Обновление информации о треугольнике
function updateTriangleInfo() {
    if (vertices.length !== 3) {
        clearTriangleInfo();
        return;
    }
    
    const pixelSize = parseFloat(document.getElementById('pixel-size').value) || 0.1;
    const sideNames = ['AB', 'BC', 'CA'];
    
    for (let i = 0; i < 3; i++) {
        const v1 = vertices[i];
        const v2 = vertices[(i + 1) % 3];
        
        // Вычисляем длину в пикселях (на оригинальном изображении)
        const dx = (v2.x - v1.x) / imageScale;
        const dy = (v2.y - v1.y) / imageScale;
        const lengthPx = Math.sqrt(dx * dx + dy * dy);
        const lengthM = lengthPx * pixelSize;
        
        // Обновляем панель
        const sideId = `side-${sideNames[i].toLowerCase()}`;
        document.getElementById(sideId).textContent = 
            `Сторона ${sideNames[i]}: ${lengthPx.toFixed(1)} px (${lengthM.toFixed(2)} m)`;
    }
    
    // Автоматически рассчитываем объём и массу
    autoCalculateVolume();
}

// Обновление информации об изображении
function updateImageInfo(width, height, source) {
    document.getElementById('image-size').textContent = `Размер: ${width} x ${height} px`;
    document.getElementById('image-source').textContent = `Источник: ${source}`;
    document.getElementById('image-display').textContent = 
        `Отображение: ${Math.round(width * imageScale)} x ${Math.round(height * imageScale)} px`;
}

// Обновление статуса
function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

// Модальное окно настроек
function openSettingsModal() {
    document.getElementById('settings-modal').style.display = 'block';
}

function closeSettingsModal() {
    document.getElementById('settings-modal').style.display = 'none';
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

async function saveSettings() {
    // Сохранение настроек для обеих камер
    const cameras = ['zif1', 'zif2'];
    
    for (const cam of cameras) {
        const config = {
            trassir_ip: document.getElementById(`${cam}-ip`).value,
            chanel_name: document.getElementById(`${cam}-channel`).value,
            password: document.getElementById(`${cam}-password`).value,
            pixel_size_m: parseFloat(document.getElementById(`${cam}-pixel-size`).value),
            k_vol: parseFloat(document.getElementById(`${cam}-k-vol`).value),
            k_den: parseFloat(document.getElementById(`${cam}-k-den`).value),
            threshold: parseInt(document.getElementById(`${cam}-threshold`).value)
        };
        
        try {
            await fetch('/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    camera_name: `CAM_CONE_${cam.toUpperCase()}`,
                    config: config
                })
            });
        } catch (error) {
            console.error('Error saving config:', error);
        }
    }
    
    alert('Настройки сохранены');
    closeSettingsModal();
}
