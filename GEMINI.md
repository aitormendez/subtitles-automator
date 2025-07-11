# Proyecto: Transcripción de Video con Whisper

Este documento registra los pasos y la configuración para transcribir archivos de video locales y generar subtítulos en formato SRT utilizando tanto la versión de Python de `openai-whisper` como la versión de alto rendimiento `whisper.cpp`.

## Configuración del Entorno

1.  **Gestor de Entorno**: Se utiliza `pyenv` junto con `pyenv-virtualenv` para gestionar las versiones de Python y los entornos virtuales.
2.  **Versión de Python**: Se ha seleccionado Python `3.10.12`.
3.  **Entorno Virtual**: Se creó un entorno virtual específico para este proyecto llamado `transcripciones`.
    - **Comando de creación**: `pyenv virtualenv 3.10.12 transcripciones`
4.  **Activación del Entorno**: El entorno se activa automáticamente al ingresar al directorio del proyecto gracias a la configuración local de `pyenv`.
    - **Comando de activación**: `pyenv local transcripciones`

## Método 1: `openai-whisper` (Basado en Python)

Este método es más sencillo de instalar pero significativamente más lento en hardware de Apple, ya que no aprovecha completamente la aceleración de la GPU.

### Pasos de Ejecución

1.  **Instalación** (dentro del entorno `transcripciones`):
    ```bash
    pip install -U openai-whisper
    ```
2.  **Renombrar Archivo**: Para evitar errores con caracteres especiales, se renombró el video de entrada:
    ```bash
    mv "CC - TOBÍAS - III.03 (3) - La ascensión： La oscuridad busca liberarse (3ª parte) [v4sbm27_FXc].webm" tobias.webm
    ```
3.  **Ejecución (en CPU)**: Se transcribe el video utilizando la CPU. El uso de la GPU (`--device mps`) falló debido a incompatibilidades con el backend de PyTorch para Metal.
    ```bash
    whisper tobias.webm --model small --language es --output_format srt
    ```

---

## Método 2: `whisper.cpp` (Alto Rendimiento en Apple Silicon)

Este método ofrece una velocidad de transcripción drásticamente superior al estar optimizado en C++ para el hardware de Apple (M1/M2/M3).

### Pasos de Ejecución

1.  **Clonar Repositorio**: Se descarga el código fuente desde GitHub.
    ```bash
    git clone https://github.com/ggerganov/whisper.cpp.git
    ```
2.  **Compilar el Código**: Se compilan los ejecutables desde el código fuente. Este comando debe ejecutarse dentro del nuevo directorio `whisper.cpp`.
    ```bash
    cd whisper.cpp
    make
    ```
3.  **Descargar Modelo**: Se descarga el modelo pre-entrenado en el formato `ggml` que utiliza `whisper.cpp`. En este caso, se usó el modelo `medium`.
    ```bash
    ./models/download-ggml-model.sh medium
    ```
4.  **Convertir Video a Audio**: Para evitar problemas de compatibilidad de `ffmpeg` dentro de `whisper.cpp`, se convierte el video a un archivo de audio WAV compatible.
    ```bash
    ffmpeg -i tobias.webm -ar 16000 -ac 1 -c:a pcm_s16le tobias_audio.wav
    ```
5.  **Ejecución Final**: Se ejecuta la transcripción sobre el archivo de audio, especificando el modelo, el idioma y el formato de salida SRT. Este comando se ejecuta desde el directorio `whisper.cpp`.
    ```bash
    ./build/bin/whisper-cli -m models/ggml-medium.bin -l es -osrt -f "../tobias_audio.wav"
    ```

Este método final resultó ser exitoso y notablemente más rápido.

## Traducción de Subtítulos con Ollama (`translate_srt.py`)

Para traducir los subtítulos generados a otros idiomas utilizando modelos de lenguaje grandes (LLMs) de forma local con Ollama, se utiliza el script `translate_srt.py`.

### Requisitos

- **Ollama**: Asegúrate de tener Ollama instalado y los modelos deseados descargados.
  ```bash
  ollama pull llama3
  ollama pull qwen:7b-chat
  ```

### Uso

1.  **Hacer Ejecutable el Script**:

    ```bash
    chmod +x translate_srt.py
    ```

2.  **Ejecutar la Traducción**:
    ```bash
    ./translate_srt.py <archivo_entrada.srt> <archivo_salida.srt> <modelo_ollama_por_defecto> <código_idioma>
    ```
    - **`modelo_ollama_por_defecto`**: Este será el modelo utilizado para todos los idiomas, _excepto_ para el chino.
    - **Selección de Modelo por Idioma**: El script está configurado para usar `qwen:7b-chat` automáticamente para las traducciones al chino (`zh`), independientemente del `modelo_ollama_por_defecto` especificado.
    - **Ejemplo para traducir al francés**:
      ```bash
      ./translate_srt.py tobias.webm.srt tobias.fr.srt llama3 fr
      ```
    - **Ejemplo para traducir al chino**:
      ```bash
      ./translate_srt.py tobias.webm.srt tobias.zh.srt llama3 zh
      ```
    - **Códigos de Idioma Soportados**:
      - `en` (Inglés)
      - `fr` (Francés)
      - `de` (Alemán)
      - `it` (Italiano)
      - `ru` (Ruso)
      - `zh` (Chino Simplificado)

---

## Traducción de Subtítulos con Google Translate (`translate_srt_google_translator.py`)

Para traducir los subtítulos generados a otros idiomas utilizando la API de Google Translate (a través de la librería `googletrans`), se utiliza el script `translate_srt_google_translator.py`. Este script ha sido optimizado para una traducción eficiente y segura, incluyendo:

- **Traducción por lotes (batching)**: Agrupa los subtítulos en lotes de 5 bloques para reducir el número de peticiones y acelerar el proceso, manteniendo la coherencia de la traducción.
- **Separador seguro**: Utiliza un separador especial (`⸻⸻⸻⸻⸻⸻⸻⸻⸻⸻`) para dividir los bloques dentro de cada lote, diseñado para no ser modificado por Google Translate, garantizando la reconstrucción correcta de los subtítulos.
- **Pausa entre lotes**: Incluye una pausa de 1 segundo entre cada lote para evitar bloqueos o limitaciones del servicio de traducción.
- **Ajuste progresivo**: El tamaño óptimo de lote es de 5 bloques, ya que valores mayores pueden provocar errores o traducciones incompletas.

### Requisitos

- **Librería `googletrans`**: Instala la librería `googletrans`.
  ```bash
  pip install googletrans==4.0.0-rc1
  ```

### Uso

1.  **Hacer Ejecutable el Script**:

    ```bash
    chmod +x translate_srt_google_translator.py
    ```

2.  **Ejecutar la Traducción**:
    ```bash
    ./translate_srt_google_translator.py <archivo_entrada.srt> <archivo_salida.srt> <código_idioma>
    ```
    - **Ejemplo para traducir al francés**:
      ```bash
      ./translate_srt_google_translator.py tobias.srt tobias.fr.srt fr
      ```
    - **Ejemplo para traducir al chino**:
      ```bash
      ./translate_srt_google_translator.py tobias.srt tobias.zh.srt zh
      ```
    - **Códigos de Idioma Soportados**:
      - `en` (Inglés)
      - `fr` (Francés)
      - `de` (Alemán)
      - `it` (Italiano)
      - `ru` (Ruso)
      - `zh` (Chino Simplificado)

---

## Flujo de Trabajo Automatizado con automate_subtitles.py

El script `automate_subtitles.py` implementa un flujo de trabajo automatizado para simplificar y acelerar el proceso completo de generación y traducción de subtítulos a partir de archivos de video locales. Este enfoque integrado combina extracción de audio, transcripción y traducción, optimizando cada etapa para minimizar la intervención manual y mejorar la eficiencia.

### Proceso Técnico

1.  **Extracción de Audio**: A partir del archivo de video original ubicado en un directorio determinado, el script utiliza `ffmpeg` para extraer el audio en formato WAV con parámetros compatibles con `whisper.cpp` (frecuencia de muestreo de 16 kHz y canal mono). El archivo de audio resultante se guarda en el mismo directorio que el video, manteniendo una estructura ordenada y facilitando la gestión de archivos relacionados.

2.  **Generación de Subtítulos en Español**: Utilizando el motor de transcripción de alto rendimiento `whisper.cpp`, el script procesa el archivo de audio para generar subtítulos en español. El nombre del archivo de subtítulos se asigna automáticamente siguiendo el patrón `<nombre_del_video>.es.srt`, asegurando una nomenclatura clara y consistente que facilita su posterior identificación y uso.

3.  **Estrategia Mixta de Traducción**: Para la traducción de los subtítulos generados a otros idiomas, el script implementa una estrategia híbrida basada en las fortalezas de dos herramientas:

    - Para las traducciones al chino (`zh`), se emplea el script optimizado `translate_srt_google_translator.py`, que utiliza la API de Google Translate con procesamiento por lotes y separadores seguros para garantizar traducciones coherentes y precisas.

    - Para los demás idiomas soportados, se utiliza `translate_srt.py`, que aprovecha modelos de lenguaje locales mediante Ollama, permitiendo traducciones más controladas y personalizables sin dependencia directa de servicios externos.

4.  **Reentrancia y Eficiencia**: El diseño del script permite la ejecución repetida sin duplicar trabajo innecesario. Antes de extraer audio o generar subtítulos, verifica la existencia de los archivos correspondientes y omite estas etapas si ya están disponibles. Esto facilita la gestión de grandes volúmenes de archivos o la recuperación de procesos interrumpidos, optimizando recursos y tiempo.

### Diseño y Racional

Este flujo automatizado busca integrar las mejores prácticas y herramientas disponibles para ofrecer una solución robusta y flexible para la transcripción y traducción de videos. La combinación de `whisper.cpp` para transcripción rápida y precisa, junto con una estrategia de traducción adaptativa que aprovecha tanto Google Translate como Ollama, permite manejar múltiples idiomas con alta calidad y eficiencia. Además, la automatización de la extracción de audio y el control de reentrancia simplifican la experiencia del usuario, reduciendo la necesidad de intervención manual y minimizando errores operativos.
