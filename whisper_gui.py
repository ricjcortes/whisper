#!/usr/bin/env python3
"""
Whisper GUI - Interfaz gráfica para transcripción de audio con Whisper
Permite seleccionar archivo, modelo y carpeta destino con opciones avanzadas
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import whisper
import os
import threading
import json
from datetime import datetime
from pathlib import Path

class WhisperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper - Transcriptor de Audio")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.audio_file = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.model_name = tk.StringVar(value="medium")
        self.language = tk.StringVar(value="es")
        self.temperature = tk.DoubleVar(value=0.0)
        self.word_timestamps = tk.BooleanVar(value=True)
        self.task = tk.StringVar(value="transcribe")
        self.output_format = tk.StringVar(value="txt")
        
        # Estado
        self.model = None
        self.is_transcribing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Título
        title_label = ttk.Label(main_frame, text="Whisper - Transcriptor de Audio", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Selección de archivo de audio
        ttk.Label(main_frame, text="Archivo de audio:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.audio_file, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Buscar", command=self.select_audio_file).grid(row=row, column=2, padx=5)
        row += 1
        
        # Selección de carpeta destino
        ttk.Label(main_frame, text="Carpeta destino:").grid(row=row, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="Buscar", command=self.select_output_folder).grid(row=row, column=2, padx=5)
        row += 1
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # Frame para opciones
        options_frame = ttk.LabelFrame(main_frame, text="Opciones de Transcripción", padding="10")
        options_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        options_frame.columnconfigure(3, weight=1)
        row += 1
        
        # Modelo
        ttk.Label(options_frame, text="Modelo:").grid(row=0, column=0, sticky=tk.W, padx=5)
        model_combo = ttk.Combobox(options_frame, textvariable=self.model_name, 
                                  values=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3", "turbo"],
                                  state="readonly")
        model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        # Idioma
        ttk.Label(options_frame, text="Idioma:").grid(row=0, column=2, sticky=tk.W, padx=5)
        language_combo = ttk.Combobox(options_frame, textvariable=self.language,
                                     values=["es", "en", "fr", "de", "it", "pt", "auto"],
                                     state="readonly")
        language_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        
        # Tarea
        ttk.Label(options_frame, text="Tarea:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        task_combo = ttk.Combobox(options_frame, textvariable=self.task,
                                 values=["transcribe", "translate"],
                                 state="readonly")
        task_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Formato de salida
        ttk.Label(options_frame, text="Formato:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        format_combo = ttk.Combobox(options_frame, textvariable=self.output_format,
                                   values=["txt", "json", "srt", "vtt"],
                                   state="readonly")
        format_combo.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Temperatura
        ttk.Label(options_frame, text="Temperatura:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        temp_scale = ttk.Scale(options_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                              variable=self.temperature, length=150)
        temp_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        temp_label = ttk.Label(options_frame, text="0.0")
        temp_label.grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # Actualizar etiqueta de temperatura
        def update_temp_label(*args):
            temp_label.config(text=f"{self.temperature.get():.1f}")
        self.temperature.trace('w', update_temp_label)
        
        # Marcas de tiempo por palabra
        ttk.Checkbutton(options_frame, text="Marcas de tiempo por palabra", 
                       variable=self.word_timestamps).grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1
        
        self.transcribe_btn = ttk.Button(button_frame, text="Iniciar Transcripción", 
                                        command=self.start_transcription, style="Accent.TButton")
        self.transcribe_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = ttk.Button(button_frame, text="Cancelar", 
                                    command=self.cancel_transcription, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Área de resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultado de la Transcripción", padding="10")
        result_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=15, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Estado
        self.status_label = ttk.Label(main_frame, text="Listo para transcribir")
        self.status_label.grid(row=row+1, column=0, columnspan=3, sticky=tk.W, pady=5)
    
    def select_audio_file(self):
        """Selecciona el archivo de audio"""
        filetypes = [
            ("Archivos de audio", "*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.wma"),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("FLAC", "*.flac"),
            ("Todos los archivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de audio",
            filetypes=filetypes
        )
        
        if filename:
            self.audio_file.set(filename)
            # Si no hay carpeta destino, usar la misma carpeta del audio
            if not self.output_folder.get():
                self.output_folder.set(os.path.dirname(filename))
    
    def select_output_folder(self):
        """Selecciona la carpeta de destino"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if folder:
            self.output_folder.set(folder)
    
    def validate_inputs(self):
        """Valida las entradas del usuario"""
        if not self.audio_file.get():
            messagebox.showerror("Error", "Por favor selecciona un archivo de audio")
            return False
        
        if not os.path.exists(self.audio_file.get()):
            messagebox.showerror("Error", "El archivo de audio no existe")
            return False
        
        if not self.output_folder.get():
            messagebox.showerror("Error", "Por favor selecciona una carpeta de destino")
            return False
        
        if not os.path.exists(self.output_folder.get()):
            messagebox.showerror("Error", "La carpeta de destino no existe")
            return False
        
        return True
    
    def load_model(self):
        """Carga el modelo de Whisper"""
        try:
            self.status_label.config(text=f"Cargando modelo {self.model_name.get()}...")
            self.root.update()
            
            if self.model is None or self.model.dims.n_mels != whisper.load_model(self.model_name.get()).dims.n_mels:
                self.model = whisper.load_model(self.model_name.get())
            
            self.status_label.config(text="Modelo cargado correctamente")
            return True
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el modelo: {str(e)}")
            self.status_label.config(text="Error al cargar el modelo")
            return False
    
    def transcribe_audio(self):
        """Realiza la transcripción del audio"""
        try:
            # Preparar opciones
            options = {
                "language": None if self.language.get() == "auto" else self.language.get(),
                "task": self.task.get(),
                "temperature": self.temperature.get(),
                "word_timestamps": self.word_timestamps.get()
            }
            
            # Filtrar opciones None
            options = {k: v for k, v in options.items() if v is not None}
            
            self.status_label.config(text="Transcribiendo audio...")
            self.root.update()
            
            # Transcribir
            result = self.model.transcribe(self.audio_file.get(), **options)
            
            # Mostrar resultado en la interfaz
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result["text"])
            
            # Guardar archivo
            self.save_transcription(result)
            
            self.status_label.config(text="Transcripción completada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la transcripción: {str(e)}")
            self.status_label.config(text="Error en la transcripción")
    
    def save_transcription(self, result):
        """Guarda la transcripción en el formato seleccionado"""
        try:
            # Generar nombre de archivo
            audio_name = Path(self.audio_file.get()).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.output_format.get() == "txt":
                filename = f"{audio_name}_transcription_{timestamp}.txt"
                filepath = os.path.join(self.output_folder.get(), filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result["text"])
            
            elif self.output_format.get() == "json":
                filename = f"{audio_name}_transcription_{timestamp}.json"
                filepath = os.path.join(self.output_folder.get(), filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            
            elif self.output_format.get() == "srt":
                filename = f"{audio_name}_transcription_{timestamp}.srt"
                filepath = os.path.join(self.output_folder.get(), filename)
                self.save_srt(result, filepath)
            
            elif self.output_format.get() == "vtt":
                filename = f"{audio_name}_transcription_{timestamp}.vtt"
                filepath = os.path.join(self.output_folder.get(), filename)
                self.save_vtt(result, filepath)
            
            messagebox.showinfo("Éxito", f"Transcripción guardada en:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar el archivo: {str(e)}")
    
    def save_srt(self, result, filepath):
        """Guarda en formato SRT"""
        with open(filepath, 'w', encoding='utf-8') as f:
            if "segments" in result:
                for i, segment in enumerate(result["segments"], 1):
                    start_time = self.format_time(segment["start"])
                    end_time = self.format_time(segment["end"])
                    f.write(f"{i}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
            else:
                # Si no hay segmentos, crear uno general
                f.write("1\n00:00:00,000 --> 00:10:00,000\n")
                f.write(f"{result['text']}\n\n")
    
    def save_vtt(self, result, filepath):
        """Guarda en formato VTT"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")
            if "segments" in result:
                for segment in result["segments"]:
                    start_time = self.format_time_vtt(segment["start"])
                    end_time = self.format_time_vtt(segment["end"])
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{segment['text'].strip()}\n\n")
            else:
                f.write("00:00:00.000 --> 00:10:00.000\n")
                f.write(f"{result['text']}\n\n")
    
    def format_time(self, seconds):
        """Formatea tiempo para SRT (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def format_time_vtt(self, seconds):
        """Formatea tiempo para VTT (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millisecs:03d}"
    
    def start_transcription(self):
        """Inicia el proceso de transcripción en un hilo separado"""
        if not self.validate_inputs():
            return
        
        self.is_transcribing = True
        self.transcribe_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.progress.start()
        
        # Ejecutar en hilo separado para no bloquear la interfaz
        thread = threading.Thread(target=self.transcription_worker)
        thread.daemon = True
        thread.start()
    
    def transcription_worker(self):
        """Worker para la transcripción en hilo separado"""
        try:
            if self.load_model():
                self.transcribe_audio()
        finally:
            # Actualizar interfaz en el hilo principal
            self.root.after(0, self.transcription_finished)
    
    def transcription_finished(self):
        """Limpia la interfaz después de la transcripción"""
        self.is_transcribing = False
        self.transcribe_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress.stop()
    
    def cancel_transcription(self):
        """Cancela la transcripción (limitado)"""
        self.is_transcribing = False
        self.transcription_finished()
        self.status_label.config(text="Transcripción cancelada")
        messagebox.showinfo("Cancelado", "Transcripción cancelada")

def main():
    """Función principal"""
    root = tk.Tk()
    app = WhisperGUI(root)
    
    # Configurar tema si está disponible
    try:
        style = ttk.Style()
        style.theme_use('clam')  # Tema más moderno
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()