// Глобальные переменные
let canvas, ctx;
let currentImage = null;
let vertices = [];
let draggingVertex = null;
let imageScale = 1.0;
let defaultImageScale = 1.0;  // Запоминаем начальный масштаб
let userZoomLevel = 1.0;  // Пользовательский масштаб (zoom)
let imageOffset = { x: 0, y: 0 };

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('main-canvas');
    ctx = canvas.getContext('2d');
    
    // Устанавливаем размер canvas под контейнер
    resizeCanvas();
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', function() {
        resizeCanvas();
        if (currentImage) {
            redrawCanvas();
        }
    });
    
    initializeEventListeners();
    updateStatus('Готов к работе');
});

// Изменение размера canvas под контейнер
function resizeCanvas() {
    const container = canvas.parentElement;
    const rect = container.getBoundingClientRect();
    
    // Устанавливаем размер canvas равным размеру контейнера
    canvas.width = rect.width;
    canvas.height = rect.height;
    
    // Пересчитываем масштаб изображения если оно загружено
    if (currentImage) {
        const scaleX = canvas.width / currentImage.width;
        const scaleY = canvas.height / currentImage.height;
        imageScale = Math.min(scaleX, scaleY, 1.0);
        
        const scaledWidth = currentImage.width * imageScale;
        const scaledHeight = currentImage.height * imageScale;
        imageOffset.x = (canvas.width - scaledWidth) / 2;
        imageOffset.y = (canvas.height - scaledHeight) / 2;
    }
}

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
    
    // Кнопки масштабирования
    document.getElementById('zoom-in-btn').addEventListener('click', zoomIn);
    document.getElementById('zoom-out-btn').addEventListener('click', zoomOut);
    document.getElementById('zoom-reset-btn').addEventListener('click', zoomReset);
    
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
        
        // Вычисляем масштаб для заполнения всего canvas
        const scaleX = canvas.width / img.width;
        const scaleY = canvas.height / img.height;
        imageScale = Math.max(scaleX, scaleY);  // ← Используем max для заполнения
        defaultImageScale = imageScale;  // Сохраняем начальный масштаб
        userZoomLevel = 1.0;  // Сбрасываем zoom
        
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
        
        // Преобразуем координаты canvas в координаты оригинального изображения
        const v1Original = [
            (v1.x - imageOffset.x) / imageScale,
            (v1.y - imageOffset.y) / imageScale
        ];
        const v2Original = [
            (v2.x - imageOffset.x) / imageScale,
            (v2.y - imageOffset.y) / imageScale
        ];
        
        // Вычисляем длину в пикселях оригинального изображения
        const dx = v2Original[0] - v1Original[0];
        const dy = v2Original[1] - v1Original[1];
        const lengthPx = Math.sqrt(dx * dx + dy * dy);
        const lengthM = lengthPx * pixelSize;
        
        // Середина стороны (в координатах canvas для отрисовки)
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
function calculateVolume() {
    if (vertices.length !== 3) {
        alert('Постройте треугольник (3 вершины)');
        return;
    }
    
    updateStatus('Расчёт объёма...');
    
    // Сначала обновляем информацию о сторонах (включает autoCalculateVolume)
    updateTriangleInfo();
    
    updateStatus('Расчёт завершён');
}

// Автоматический расчёт объёма (на стороне браузера)
function autoCalculateVolume() {
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
    
    // Рассчитываем на стороне браузера
    const results = calculateConeParameters(originalVertices, pixelSize, kVol, kDen);
    displayResults(results.sides, results.cone);
}

// ========================
// Геометрические функции
// ========================

// Расстояние между двумя точками
function distanceBetweenPoints(point1, point2) {
    const dx = point2[0] - point1[0];
    const dy = point2[1] - point1[1];
    return Math.sqrt(dx * dx + dy * dy);
}

// Площадь треугольника по трём точкам
function triangleArea(point1, point2, point3) {
    const x1 = point1[0], y1 = point1[1];
    const x2 = point2[0], y2 = point2[1];
    const x3 = point3[0], y3 = point3[1];
    return Math.abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2.0;
}

// Высота треугольника относительно основания
function triangleHeight(basePoint1, basePoint2, oppositePoint) {
    const area = triangleArea(basePoint1, basePoint2, oppositePoint);
    const baseLength = distanceBetweenPoints(basePoint1, basePoint2);
    return baseLength > 0 ? (2 * area) / baseLength : 0;
}

// ========================
// Расчёт параметров конуса
// ========================

function calculateConeParameters(triangleVertices, pixelSizeM, kVol, kDen) {
    if (triangleVertices.length !== 3) {
        return {
            sides: [],
            cone: { volume: 0, mass: 0, radius_m: 0, height_m: 0 }
        };
    }
    
    const [pointA, pointB, pointC] = triangleVertices;
    
    // Рассчитываем стороны треугольника
    const sides = [
        {
            name: 'AB',
            length_px: distanceBetweenPoints(pointA, pointB),
            length_m: distanceBetweenPoints(pointA, pointB) * pixelSizeM
        },
        {
            name: 'BC',
            length_px: distanceBetweenPoints(pointB, pointC),
            length_m: distanceBetweenPoints(pointB, pointC) * pixelSizeM
        },
        {
            name: 'CA',
            length_px: distanceBetweenPoints(pointC, pointA),
            length_m: distanceBetweenPoints(pointC, pointA) * pixelSizeM
        }
    ];
    
    // Находим наиболее горизонтальную сторону (минимальная разница по Y)
    const sideCandidates = [
        { base1: pointA, base2: pointB, opposite: pointC },
        { base1: pointB, base2: pointC, opposite: pointA },
        { base1: pointC, base2: pointA, opposite: pointB }
    ];
    
    let minYDiff = Infinity;
    let bestBase1 = null;
    let bestBase2 = null;
    let bestOpposite = null;
    
    for (const candidate of sideCandidates) {
        const yDiff = Math.abs(candidate.base2[1] - candidate.base1[1]);
        if (yDiff < minYDiff) {
            minYDiff = yDiff;
            bestBase1 = candidate.base1;
            bestBase2 = candidate.base2;
            bestOpposite = candidate.opposite;
        }
    }
    
    // Длина основания конуса
    const baseLengthPx = distanceBetweenPoints(bestBase1, bestBase2);
    const baseLengthM = baseLengthPx * pixelSizeM;
    const radiusM = baseLengthM / 2;
    
    // Высота конуса
    const heightPx = triangleHeight(bestBase1, bestBase2, bestOpposite);
    const heightM = heightPx * pixelSizeM;
    
    // Объём конуса: V = (1/3) * π * r² * h * k_vol
    let volume = 0;
    if (heightM > 0 && radiusM > 0) {
        volume = (1 / 3) * Math.PI * radiusM * radiusM * heightM * kVol;
    }
    
    // Масса: m = V * k_den
    const mass = volume * kDen;
    
    return {
        sides: sides,
        cone: {
            volume: volume,
            mass: mass,
            radius_m: radiusM,
            height_m: heightM
        }
    };
}

// Отображение результатов
function displayResults(sides, cone) {
    // Параметры конуса (без обновления сторон треугольника)
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
        
        // Преобразуем координаты canvas в координаты оригинального изображения
        const v1Original = [
            (v1.x - imageOffset.x) / imageScale,
            (v1.y - imageOffset.y) / imageScale
        ];
        const v2Original = [
            (v2.x - imageOffset.x) / imageScale,
            (v2.y - imageOffset.y) / imageScale
        ];
        
        // Вычисляем длину в пикселях оригинального изображения
        const dx = v2Original[0] - v1Original[0];
        const dy = v2Original[1] - v1Original[1];
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

// ========================
// Управление масштабом
// ========================

// Увеличение масштаба
function zoomIn() {
    if (!currentImage) {
        updateStatus('Сначала загрузите изображение');
        return;
    }
    
    userZoomLevel = Math.min(userZoomLevel * 1.2, 5.0);  // Макс. 5x zoom
    applyZoom();
    updateStatus(`Масштаб: ${(userZoomLevel * 100).toFixed(0)}%`);
}

// Уменьшение масштаба
function zoomOut() {
    if (!currentImage) {
        updateStatus('Сначала загрузите изображение');
        return;
    }
    
    userZoomLevel = Math.max(userZoomLevel / 1.2, 0.5);  // Мин. 0.5x zoom
    applyZoom();
    updateStatus(`Масштаб: ${(userZoomLevel * 100).toFixed(0)}%`);
}

// Сброс масштаба
function zoomReset() {
    if (!currentImage) {
        updateStatus('Сначала загрузите изображение');
        return;
    }
    
    userZoomLevel = 1.0;
    applyZoom();
    updateStatus('Масштаб сброшен к 100%');
}

// Применение масштаба
function applyZoom() {
    if (!currentImage) return;
    
    // Сохраняем старый масштаб и смещение
    const oldImageScale = imageScale;
    const oldImageOffset = { x: imageOffset.x, y: imageOffset.y };
    
    // Преобразуем вершины треугольника в координаты оригинального изображения
    const originalVertices = vertices.map(v => ({
        x: (v.x - oldImageOffset.x) / oldImageScale,
        y: (v.y - oldImageOffset.y) / oldImageScale
    }));
    
    // Сохраняем центр canvas в координатах изображения
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const oldImageX = (centerX - imageOffset.x) / imageScale;
    const oldImageY = (centerY - imageOffset.y) / imageScale;
    
    // Применяем новый масштаб
    imageScale = defaultImageScale * userZoomLevel;
    
    // Пересчитываем смещение чтобы центр остался на месте
    const scaledWidth = currentImage.width * imageScale;
    const scaledHeight = currentImage.height * imageScale;
    imageOffset.x = centerX - (oldImageX * imageScale);
    imageOffset.y = centerY - (oldImageY * imageScale);
    
    // Ограничиваем смещение чтобы изображение не уходило за границы
    const maxOffsetX = scaledWidth - canvas.width;
    const maxOffsetY = scaledHeight - canvas.height;
    
    if (maxOffsetX > 0) {
        imageOffset.x = Math.max(-maxOffsetX, Math.min(0, imageOffset.x));
    } else {
        imageOffset.x = (canvas.width - scaledWidth) / 2;
    }
    
    if (maxOffsetY > 0) {
        imageOffset.y = Math.max(-maxOffsetY, Math.min(0, imageOffset.y));
    } else {
        imageOffset.y = (canvas.height - scaledHeight) / 2;
    }
    
    // Преобразуем вершины обратно в новые координаты canvas
    vertices = originalVertices.map(v => ({
        x: v.x * imageScale + imageOffset.x,
        y: v.y * imageScale + imageOffset.y
    }));
    
    redrawCanvas();
}
