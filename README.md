# Maruz Distribuciones 🚀

Sistema web para la gestión de productos y chatbot de Maruz Distribuciones.

## Requisitos 📋

- Python 3.10+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

## Instalación 🔧

1. Clonar el repositorio:
```bash
git clone https://github.com/mgcomputacion2009/Maruzdistribuciones.git
cd Maruzdistribuciones
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

## Estructura del Proyecto 📁

```
maruz/
├── app/                    # Código principal de la aplicación
│   └── maruz_distribuciones/
│       ├── api/           # Endpoints de la API
│       ├── models/        # Modelos de datos
│       └── storage/       # Almacenamiento de archivos
├── config/                # Configuraciones
├── public/               # Archivos públicos
├── paginas/              # Páginas web
└── venv/                 # Entorno virtual
```

## Uso 🚀

1. Activar el entorno virtual:
```bash
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

2. Ejecutar la aplicación:
```bash
python run.py
```

## Endpoints API 🛠️

### Productos

- `GET /api/productos/status` - Estado de la tabla productos
- `POST /api/productos/cargar` - Cargar productos desde CSV

## Contribuir 🤝

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia 📄

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto 📧

Miguel Gutiérrez - mgcomputacion2009@gmail.com
