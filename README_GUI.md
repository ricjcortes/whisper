# Whisper GUI - Transcriptor de Audio con Interfaz Gráfica

Una aplicación con interfaz gráfica para transcribir archivos de audio usando OpenAI Whisper.

## Características

- **Interfaz gráfica intuitiva** con tkinter
- **Selección fácil** de archivos de audio y carpeta destino
- **Múltiples modelos** de Whisper (tiny, base, small, medium, large, large-v2, large-v3, turbo)
- **Soporte multiidioma** con detección automática
- **Múltiples formatos de salida**: TXT, JSON, SRT, VTT
- **Opciones avanzadas**: temperatura, marcas de tiempo por palabra
- **Transcripción en segundo plano** sin bloquear la interfaz
- **Soporte para múltiples formatos** de audio (MP3, WAV, FLAC, M4A, etc.)

## Instalación

1. Clona el repositorio o descarga el archivo `whisper_gui.py`

2. Instala las dependencias:
```bash
pip install -r requirements_gui.txt
```

O instala manualmente:
```bash
pip install openai-whisper torch torchaudio
```

## Uso

### Ejecutar la aplicación
```bash
python whisper_gui.py
```

### Pasos para transcribir:

1. **Seleccionar archivo de audio**: Haz clic en "Buscar" junto a "Archivo de audio"
2. **Elegir carpeta destino**: Selecciona donde guardar la transcripción
3. **Configurar opciones**:
   - **Modelo**: tiny (más rápido) a large-v3 (más preciso)
   - **Idioma**: es (español), en (inglés), auto (detección automática)
   - **Tarea**: transcribe (transcribir) o translate (traducir al inglés)
   - **Formato**: txt, json, srt (subtítulos), vtt (subtítulos web)
   - **Temperatura**: 0.0 (más determinista) a 1.0 (más creativo)
   - **Marcas de tiempo**: para obtener tiempos por palabra
4. **Iniciar transcripción**: Haz clic en "Iniciar Transcripción"

## Opciones Avanzadas

### Modelos disponibles
- **tiny**: Más rápido, menos preciso (~39 MB)
- **base**: Equilibrio entre velocidad y precisión (~74 MB)
- **small**: Buena precisión (~244 MB)
- **medium**: Muy buena precisión (~769 MB) - **Recomendado**
- **large/large-v2/large-v3**: Máxima precisión (~1550 MB)
- **turbo**: Rápido con buena precisión (~809 MB)

### Formatos de salida
- **TXT**: Texto plano
- **JSON**: Incluye metadatos, segmentos, confianza
- **SRT**: Subtítulos para videos (formato estándar)
- **VTT**: Subtítulos web (HTML5)

### Configuración de temperatura
- **0.0**: Resultados más consistentes y deterministas
- **0.1-0.3**: Ligera variación, bueno para la mayoría de casos
- **0.5-1.0**: Más creativo pero menos predecible

## Formatos de audio soportados

- MP3, WAV, FLAC, M4A, AAC, OGG, WMA
- Cualquier formato que soporte FFmpeg

## Ejemplo de uso en código

Si prefieres usar el script directamente:

```python
from whisper_gui import WhisperGUI
import tkinter as tk

root = tk.Tk()
app = WhisperGUI(root)
root.mainloop()
```

## Requisitos del sistema

- Python 3.8+
- 4GB+ RAM recomendado
- GPU opcional (CUDA) para mejor rendimiento
- ffmpeg instalado para soporte completo de formatos

## Solución de problemas

### Error al cargar el modelo
- Verifica que tienes suficiente RAM
- Prueba con un modelo más pequeño (tiny, base, small)

### Audio no soportado
- Instala ffmpeg: `pip install ffmpeg-python`
- Convierte el audio a MP3 o WAV

### Transcripción lenta
- Usa un modelo más pequeño
- Considera usar GPU si está disponible
- Cierra otras aplicaciones que consuman memoria

### Transcripción inexacta
- Usa un modelo más grande (medium, large)
- Ajusta la temperatura a 0.0
- Verifica que el idioma esté configurado correctamente
- Asegúrate de que el audio tenga buena calidad

## Licencia

Este proyecto utiliza OpenAI Whisper y está sujeto a sus términos de licencia.