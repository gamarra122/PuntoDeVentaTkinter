from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import os
import socket
import shutil
import datetime

class Informacion(tk.Frame):

    def __init__(self, padre, titulo="Información del Sistema"):
        super().__init__(padre)
        self.titulo = titulo
        self.configure(padx=10, pady=10, bd=2, relief=tk.GROOVE)
        self.datos = self.obtener_datos()
        self.widgets()

    def obtener_datos(self):
        try:
            usuario = os.getlogin()
        except:
            usuario = "Desconocido"
        
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            ip = "No disponible"

        try:
            espacio = f"{shutil.disk_usage('/').free // (1024**3)} GB"
        except:
            espacio = "Desconocido"

        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "👤 Usuario": usuario,
            "💻 Sistema operativo": platform.system() + " " + platform.release(),
            "🧱 Versión": platform.version(),
            "🧠 CPU": platform.processor(),
            "💾 RAM": "16 GB",  # Podés mejorarlo con psutil si querés mostrar real
            "📦 Espacio libre": espacio,
            "🌐 IP local": ip,
            "🖥️ Resolución": f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}",
            "📅 Fecha y hora": ahora,
            "📡 Estado": "En línea"
        }

    def widgets(self):
        # Título principal
        titulo_label = Label(self, text=self.titulo, font=("Arial", 12, "bold"))
        titulo_label.pack(pady=(0, 10))

        # Frame para los datos
        datos_frame = tk.LabelFrame(self, text="Detalles", font=("Arial", 10, "bold"))
        datos_frame.pack(fill=tk.BOTH, expand=True)

        row = 0
        for i, (clave, valor) in enumerate(self.datos.items()):
            bg_color = "#f9f9f9" if i % 2 == 0 else "#e0e0e0"

            tk.Label(datos_frame, text=clave, font=("Arial", 10, "bold"),
                    anchor='w', bg=bg_color).grid(row=row, column=0, sticky='w', padx=5, pady=4, ipadx=5, ipady=2)
            
            valor_label = tk.Label(datos_frame, text=str(valor), bg=bg_color,
                                anchor='w', padx=5)
            valor_label.grid(row=row, column=1, sticky='w', padx=5, pady=4, ipadx=5, ipady=2)

            row += 1

        # Botones de acción
        botones_frame = tk.Frame(self)
        botones_frame.pack(fill=tk.X, pady=(15, 0))

        actualizar_btn = tk.Button(botones_frame, text="🔄 Actualizar", command=self.actualizar_info)
        actualizar_btn.pack(side=tk.LEFT, padx=(0, 5))

        copiar_btn = tk.Button(botones_frame, text="📋 Copiar Datos", command=self.copiar_datos)
        copiar_btn.pack(side=tk.LEFT, padx=5)

        ayuda_btn = tk.Button(botones_frame, text="❓ Ayuda", command=self.mostrar_ayuda)
        ayuda_btn.pack(side=tk.LEFT, padx=5)

    def actualizar_info(self):
        self.datos = self.obtener_datos()
        self.refresh()

    def copiar_datos(self):
        texto = "\n".join([f"{clave}: {valor}" for clave, valor in self.datos.items()])
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Copiado", "Los datos fueron copiados al portapapeles.")

    def mostrar_ayuda(self):
        ventana_ayuda = tk.Toplevel(self)
        ventana_ayuda.title("Ayuda")
        ventana_ayuda.geometry("350x200")
        ventana_ayuda.resizable(False, False)

        mensaje = ("📋 Este panel muestra información del sistema.\n\n"
                "🔄 'Actualizar': refresca los datos.\n"
                "📋 'Copiar Datos': copia los datos al portapapeles.\n"
                "❓ 'Ayuda': abre esta ventana.")
        
        tk.Label(ventana_ayuda, text=mensaje, wraplength=320,
                justify=tk.LEFT, padx=10, pady=10).pack(fill=tk.BOTH, expand=True)

        tk.Button(ventana_ayuda, text="Cerrar", command=ventana_ayuda.destroy).pack(pady=10)

    def refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.widgets()


# Ejemplo de uso
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Mini Market - Información del Sistema")
    root.geometry("480x450")
    info = Informacion(root)
    info.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    root.mainloop()
