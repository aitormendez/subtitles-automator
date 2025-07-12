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

# Generación de subtítulos en formato VTT

Esta sección describe el flujo y uso de los scripts para generar subtítulos en formato VTT (WebVTT), ampliamente utilizado en plataformas web y compatible con servicios como Bunny.net. Los scripts permiten automatizar la generación y traducción de archivos VTT a partir de un video original.

## Descripción general

- Los scripts VTT siguen el mismo flujo que los de SRT, pero generan archivos en formato `.vtt` en lugar de `.srt`.
- Permiten automatizar la transcripción, traducción y organización de los subtítulos en distintos idiomas para integrarlos fácilmente en plataformas web.

## Generar todos los subtítulos VTT automáticamente

El script `automate_subtitles_vtt.py` automatiza la generación de subtítulos VTT en español y su traducción a varios idiomas, siguiendo la misma lógica que el flujo principal.

Uso:

```bash
./automate_subtitles_vtt.py <ruta_al_video>
```

Ejemplo:

```bash
./automate_subtitles_vtt.py "/path/to/video/tobias.webm"
```

Esto generará archivos VTT en español y en los idiomas definidos, usando la convención `<nombre_del_video>.<idioma>.vtt`.

## Traducir subtítulos VTT individualmente con Ollama

El script `translate_vtt.py` permite traducir un archivo VTT a otro idioma utilizando modelos locales de Ollama.

Uso:

```bash
./translate_vtt.py <archivo_vtt_entrada> <archivo_vtt_salida> <modelo_ollama> <código_idioma>
```

Ejemplo:

```bash
./translate_vtt.py tobias.es.vtt tobias.en.vtt llama3 en
```

## Traducir subtítulos VTT individualmente con Google Translate

El script `translate_vtt_google_translator.py` traduce archivos VTT utilizando Google Translate, ideal para idiomas en los que la traducción automática local no es óptima (por ejemplo, chino).

Uso:

```bash
./translate_vtt_google_translator.py <archivo_vtt_entrada> <archivo_vtt_salida> <código_idioma>
```

Ejemplo:

```bash
./translate_vtt_google_translator.py tobias.es.vtt tobias.zh.vtt zh
```

# Códigos de idioma para etiquetas y Bunny.net

La siguiente tabla muestra los códigos de idioma y etiquetas recomendados para usar en las plataformas y para la correcta carga en Bunny.net:

| Idioma               | Label común  | Language Code |
| -------------------- | ------------ | ------------- |
| Español              | Español      | es            |
| Inglés               | English      | en            |
| Francés              | Français     | fr            |
| Alemán               | Deutsch      | de            |
| Italiano             | Italiano     | it            |
| Chino (simplificado) | 中文（简体） | zh            |
| Chino (tradicional)  | 中文（繁體） | zh            |
| Portugués            | Português    | pt            |
| Ruso                 | Русский      | ru            |
