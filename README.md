# Flujo Automatizado de generación Subtítulos en distintos idiomas

Este proyecto proporciona un flujo de trabajo automatizado para la generación y traducción de subtítulos a partir de archivos de video locales. Está diseñado específicamente para funcionar en un entorno macOS, optimizado para equipos Apple Silicon (en particular, Mac Studio M2) utilizando `whisper.cpp` con aceleración por Metal.

El sistema convierte videos en subtítulos en español mediante transcripción automática, y luego traduce esos subtítulos a varios idiomas, combinando modelos locales a través de Ollama y el servicio de Google Translate para garantizar la mejor calidad según el idioma.

# Generación de todos los subtítulos a la vez con un solo comando

En esta sección se describe en detalle el funcionamiento del script `automate_subtitles.py`, que automatiza todo el proceso de generación y traducción de subtítulos a partir de un video.

## Descripción general

## Requisitos Previos

Para que el script funcione correctamente, asegúrate de cumplir con los siguientes requisitos:

- Tener instalado `ffmpeg`.
- Tener `whisper.cpp` compilado y accesible, con el modelo adecuado descargado.
- Tener Ollama instalado y ejecutándose en segundo plano.
- Tener los modelos necesarios cargados en Ollama, como `llama3` y `qwen:7b-chat` si se usa para otros idiomas o pruebas adicionales.
- Tener acceso a internet para las traducciones al chino que usan Google Translate.

Este script automatiza por completo el proceso de generación y traducción de subtítulos para un video local, ejecutando tres fases consecutivas:

### 1. Conversión del video a audio

- Extrae el audio del archivo de video utilizando `ffmpeg`.
- Convierte el audio a formato `.wav` (mono, 16 kHz, PCM), adecuado para la transcripción posterior.
- El archivo de audio generado se guarda con el mismo nombre base que el video, en el mismo directorio, con la extensión `.wav`.

### 2. Generación de subtítulos en español

- Utiliza el programa `whisper.cpp` (una implementación local del modelo Whisper) para generar la transcripción automática en español.
- El subtítulo generado por Whisper se guarda inicialmente con el nombre del audio seguido de `.srt`. El script renombra este archivo automáticamente para seguir una convención clara:
  - Subtítulo en español: `<nombre_del_video>.es.srt`
- Este archivo SRT en español se utiliza como base para las traducciones.

### 3. Traducción de subtítulos a otros idiomas

- Traduce el subtítulo en español a varios idiomas definidos en la variable `LANGUAGE_CODES`.
- Aplica una estrategia adaptada para optimizar la calidad:
  - Para chino (`zh`), utiliza el script `translate_srt_google_translator.py`, que traduce mediante Google Translate para garantizar una mejor calidad.
  - Para el resto de idiomas (inglés, francés, alemán, italiano y ruso), utiliza el script `translate_srt.py` con un modelo de lenguaje local (llama3), logrando traducciones rápidas y razonablemente precisas.
- Todos los subtítulos traducidos se guardan en el mismo directorio del video, con la convención `<nombre_del_video>.<idioma>.srt`.

## Manejo de archivos existentes

- El script es inteligente y reentrante:
  - Si el archivo de audio ya existe, omite la conversión.
  - Si el subtítulo en español ya existe, omite la generación de subtítulos.
  - Siempre sobreescribe los subtítulos traducidos, para garantizar que reflejen la última versión del subtítulo en español.

## Uso

```bash
./automate_subtitles.py <ruta_al_video>
```

Ejemplo:

```bash
./automate_subtitles.py "/path/to/video/tobias.webm"
```

## Resumen

Este script ofrece un flujo de trabajo completo, desde el video hasta los subtítulos traducidos en múltiples idiomas, manteniendo los archivos perfectamente organizados junto al video original.

# Traducción de subtítulos individualmente con Ollama

El script `translate_srt.py` permite traducir un archivo SRT a un idioma específico utilizando modelos locales de Ollama. Este script procesa subtítulos bloque por bloque, enviándolos al modelo configurado (por defecto `llama3`), y guarda el resultado en un nuevo archivo SRT.

Uso:

```bash
./translate_srt.py <archivo_srt_entrada> <archivo_srt_salida> <modelo_ollama> <código_idioma>
```

Ejemplo:

```bash
./translate_srt.py tobias.es.srt tobias.en.srt llama3 en
```

# Traducción de subtítulos individualmente con Google Translate

El script `translate_srt_google_translator.py` traduce subtítulos utilizando Google Translate. Está pensado para casos donde se requiere una mayor calidad de traducción, como ocurre con el chino. Traduce bloque por bloque y genera un nuevo archivo SRT con la traducción.

Uso:

```bash
./translate_srt_google_translator.py <archivo_srt_entrada> <archivo_srt_salida> <código_idioma>
```

Ejemplo:

```bash
./translate_srt_google_translator.py tobias.es.srt tobias.zh.srt zh
```
