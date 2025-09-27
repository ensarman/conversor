# Convertidor XLS a XLSX

Una aplicación web Django que convierte archivos de Excel del formato XLS legacy al formato XLSX moderno. Soporta tanto archivos XLS nativos como reportes HTML exportados con extensión .xls.

## Características

- **Conversión XLS → XLSX**: Convierte archivos XLS tradicionales manteniendo datos, fórmulas y formato
- **Conversión HTML → XLSX**: Detecta y convierte reportes HTML disfrazados como archivos .xls
- **Detección automática**: Identifica automáticamente el formato real del archivo
- **Interfaz moderna**: Bootstrap 5 con drag & drop, sin dependencias de jQuery
- **Responsive**: Compatible con dispositivos móviles
- **Progreso en tiempo real**: Barras de progreso y feedback visual
- **Descarga segura**: Sistema de descarga con validación

## Tecnologías Utilizadas

- **Backend**: Django 5.2.6
- **Frontend**: Bootstrap 5, JavaScript ES6+
- **Procesamiento**: openpyxl, xlrd, BeautifulSoup4
- **Gestión de dependencias**: pipenv

## Instalación

### Prerrequisitos

- Python 3.8+
- pipenv

### Configuración

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd conversiones
```

2. Instalar dependencias:
```bash
pipenv install
```

3. Aplicar migraciones:
```bash
pipenv run python manage.py migrate
```

4. Ejecutar servidor de desarrollo:
```bash
pipenv run python manage.py runserver
```

5. Acceder a la aplicación:
```
http://127.0.0.1:8000/
```

## Uso

1. **Subir archivo**: Arrastra y suelta un archivo .xls o usa el botón de selección
2. **Conversión automática**: El sistema detecta automáticamente si es XLS nativo o HTML
3. **Descarga**: Una vez convertido, descarga el archivo XLSX resultante

### Tipos de archivo soportados

- **Archivos XLS nativos**: Formato binario tradicional de Microsoft Excel
- **Reportes HTML**: Archivos HTML exportados desde sistemas web con extensión .xls

## Estructura del Proyecto

```
conversiones/
├── conversiones/           # Configuración principal del proyecto
│   ├── settings.py        # Configuración Django
│   ├── urls.py           # URLs principales
│   └── ...
├── xlstoxlsx/            # Aplicación de conversión
│   ├── models.py         # Modelo ConversionRecord
│   ├── views.py          # Lógica de conversión y vistas
│   ├── urls.py           # URLs de la aplicación
│   ├── templates/        # Templates HTML
│   └── ...
├── static/               # Archivos estáticos
├── media/               # Archivos subidos y convertidos
├── manage.py
├── Pipfile
└── .gitignore
```

## Funcionalidades Técnicas

### Detección de Formato
```python
def detect_format(self, conversion_record):
    # Analiza los primeros bytes del archivo
    # Busca indicadores HTML: <html, <meta, <table
    # Verifica signatura OLE para XLS real
```

### Conversión HTML
```python
def convert_html_xls_to_xlsx(self, conversion_record):
    # Parsea HTML con BeautifulSoup
    # Extrae tablas y aplica formato
    # Maneja colspan/rowspan
    # Preserva estilos y colores
```

### Conversión XLS
```python
def convert_xls_to_xlsx(self, conversion_record):
    # Lee archivo XLS con xlrd
    # Convierte a XLSX con openpyxl
    # Maneja tipos de datos y fechas
    # Preserva múltiples hojas
```

## Configuración de Desarrollo

### Variables de Entorno
El proyecto usa configuración estándar de Django. Para producción, configurar:
- `DEBUG = False`
- `ALLOWED_HOSTS`
- Base de datos externa
- Servidor de archivos estáticos

### Dependencias
```
Django==5.2.6
openpyxl==3.1.5
xlrd==2.0.2
beautifulsoup4==4.13.5
```

## Límites y Restricciones

- **Tamaño máximo**: 50MB por archivo
- **Formatos**: Solo archivos con extensión .xls
- **Almacenamiento**: Los archivos se eliminan automáticamente (configurable)

## Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## Soporte

Para reportar problemas o solicitar características, crear un issue en el repositorio.

---

Desarrollado con ❤️ usando Django y Python