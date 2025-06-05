# CRM Nutrición

Sistema de gestión de relaciones con clientes (CRM) especializado para empresas de nutrición.

## 🚀 Stack Tecnológico

- **Backend**: Django 4.2.22
- **Base de Datos**: PostgreSQL 14+
- **Frontend**: SCSS + Bootstrap
- **Servidor**: Gunicorn (producción)
- **Archivos Estáticos**: WhiteNoise

## 📋 Requisitos Previos

- Python 3.9+
- PostgreSQL 14+
- pip

## 🔧 Configuración de Desarrollo

### 1. Clonar y configurar entorno

```bash
git clone <repository-url>
cd GLOW
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de base de datos
```

### 4. Configurar base de datos

```bash
# Crear base de datos en PostgreSQL
createdb crm_nutricion_dev

# Ejecutar migraciones
python manage.py migrate
python manage.py createsuperuser
```

### 5. Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

## 🏗️ Estructura del Proyecto

```
GLOW/
├── config/                 # Configuración Django
│   ├── settings/          # Settings por entorno
│   │   ├── base.py        # Configuración base
│   │   ├── development.py # Desarrollo
│   │   └── production.py  # Producción
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                  # Aplicaciones Django
├── templates/             # Templates HTML
├── static/               # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── scss/             # Archivos SCSS
├── media/                # Archivos subidos
├── requirements/         # Dependencias por entorno
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── manage.py
```

## 🌍 Entornos

### Desarrollo
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py runserver
```

### Producción
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
pip install -r requirements/production.txt
python manage.py collectstatic
gunicorn config.wsgi:application
```

## 🎨 Frontend (SCSS + Bootstrap)

Los archivos SCSS se compilan automáticamente:
- Variables del proyecto: `static/scss/_variables.scss`
- Estilos principales: `static/scss/main.scss`

## 🔒 Seguridad

- Variables sensibles en archivos `.env` (nunca en git)
- Configuración de seguridad específica por entorno
- Validación de credenciales de base de datos

## 📦 Despliegue

### Preparar para producción

1. Configurar variables de entorno de producción
2. Instalar dependencias de producción: `pip install -r requirements/production.txt`
3. Configurar dominio en `config/settings/production.py`
4. Ejecutar: `python manage.py collectstatic`
5. Usar Gunicorn como servidor WSGI

## 🧪 Testing

```bash
pytest
```

## 📝 Notas del Desarrollador

- El proyecto usa configuración por entornos para facilitar el despliegue
- SCSS se compila automáticamente en desarrollo
- PostgreSQL es obligatorio (no usar SQLite en producción)
- Todas las credenciales deben estar en archivos `.env`
