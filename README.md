# Pipeline

**Pipeline** es una herramienta que automatiza tu flujo de trabajo musical. Obtiene y organiza tus listas de Spotify, Suno y SoundCloud, coteja que todas las canciones estén completas y alineadas, detecta faltantes, genera reportes y mantiene todo en orden. Además funciona como dashboard de metadata, remasterización y preparación para distribución.

## Características

- 🎵 **Gestión de Playlists Multi-plataforma**: Conecta con Spotify, Suno y SoundCloud
- 🔄 **Sincronización**: Compara y alinea canciones entre plataformas
- 🔍 **Detección de Faltantes**: Identifica canciones que faltan en alguna plataforma
- 📊 **Reportes**: Genera reportes detallados en múltiples formatos (JSON, Markdown, HTML, texto)
- ✅ **Verificación de Completitud**: Revisa que todas las canciones tengan metadata completa
- 📦 **Preparación para Distribución**: Valida que las canciones cumplan requisitos de distribución (ISRC, álbum, duración, etc.)
- 🎛️ **Dashboard**: Interfaz para gestión de metadata y estado de la librería

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/Pipelineee.git
cd Pipelineee

# Instalar en modo desarrollo
pip install -e .

# O instalar con dependencias de desarrollo
pip install -e ".[dev]"
```

## Uso

### Línea de Comandos (CLI)

```bash
# Ver estado de la librería
pipeline status

# Ejecutar sincronización
pipeline sync

# Generar reporte
pipeline report --format markdown --output reporte.md

# Importar datos
pipeline import datos.json

# Exportar estado
pipeline export --output estado.json
```

### Como Librería Python

```python
from pipeline.dashboard import Dashboard
from pipeline.models import Track, Playlist
from pipeline.models.track import Platform

# Crear dashboard
dashboard = Dashboard()

# Crear y añadir playlist
playlist = Playlist(
    name="Mi Playlist",
    platform=Platform.SPOTIFY,
    platform_id="playlist123"
)

# Añadir canciones
track = Track(
    title="Mi Canción",
    artist="Mi Artista",
    platform=Platform.SPOTIFY,
    platform_id="track123",
    duration_ms=180000,
    album="Mi Álbum",
    isrc="USRC12345678"
)
playlist.add_track(track)
dashboard.add_playlist(playlist)

# Obtener vistas del dashboard
library_view = dashboard.get_library_view()
distribution_view = dashboard.get_distribution_view()

# Generar reporte
report = dashboard.generate_report(format="markdown")
print(report)
```

### Conectores de Plataforma

```python
from pipeline.connectors import SpotifyConnector, SunoConnector, SoundCloudConnector
from pipeline.models.track import Platform

# Conectar con Spotify
spotify = SpotifyConnector()
spotify.authenticate({
    "client_id": "tu_client_id",
    "client_secret": "tu_client_secret",
    "access_token": "tu_access_token"  # opcional
})

# Obtener playlists
playlists = spotify.get_playlists()
```

## Estructura del Proyecto

```
pipeline/
├── __init__.py           # Punto de entrada del paquete
├── cli.py                # Interfaz de línea de comandos
├── sync.py               # Servicio de sincronización
├── connectors/           # Conectores de plataformas
│   ├── base.py          # Clase base abstracta
│   ├── spotify.py       # Conector de Spotify
│   ├── suno.py          # Conector de Suno
│   └── soundcloud.py    # Conector de SoundCloud
├── models/               # Modelos de datos
│   ├── track.py         # Modelo de canción
│   └── playlist.py      # Modelo de playlist
├── reports/              # Generación de reportes
│   ├── generator.py     # Generador de reportes
│   └── formatter.py     # Formateador de reportes
└── dashboard/            # Dashboard de gestión
    ├── app.py           # Aplicación principal
    └── views.py         # Vistas del dashboard
```

## Modelos de Datos

### Track (Canción)

```python
@dataclass
class Track:
    title: str              # Título de la canción
    artist: str             # Nombre del artista
    platform: Platform      # Plataforma (spotify, suno, soundcloud)
    platform_id: str        # ID en la plataforma
    duration_ms: int        # Duración en milisegundos
    album: str             # Álbum (opcional)
    isrc: str              # Código ISRC (opcional)
    status: TrackStatus    # Estado de verificación
    metadata: dict         # Metadata adicional
```

### Playlist

```python
@dataclass
class Playlist:
    name: str              # Nombre de la playlist
    platform: Platform     # Plataforma origen
    platform_id: str       # ID en la plataforma
    tracks: List[Track]    # Lista de canciones
    description: str       # Descripción (opcional)
```

## Reportes

Pipeline genera reportes con:

- **Resumen de Librería**: Total de canciones, playlists y duración
- **Estado de Sincronización**: Canciones sincronizadas, faltantes e incompletas
- **Preparación para Distribución**: Canciones listas vs. con problemas
- **Canciones Faltantes por Plataforma**: Detalle de qué falta en cada lugar

## Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -e ".[dev]"

# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=pipeline
```

## Licencia

MIT License
