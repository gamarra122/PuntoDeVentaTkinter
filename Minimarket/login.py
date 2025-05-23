import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from container import Container
from PIL import Image, ImageTk
import os

class Login(tk.Frame):
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    db_name = os.path.join(carpeta_actual, "database.db")  # Corregido de database_db a database.db

    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()

    def validacion(self, user, pas):
        return len(user) > 0 and len(pas) > 0
    
    def login(self):
        user = self.username.get()
        pas = self.password.get()

        if self.validacion(user, pas):
            consulta = "SELECT * FROM usuarios WHERE username = ? AND password = ?"
            parametros = (user, pas)

            try:
                with sqlite3.connect(self.db_name) as conn:
                    print("Base de datos usada:", os.path.abspath(self.db_name))
                    cursor = conn.cursor()
                    # Verificar si la tabla 'usuarios' existe
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
                    if not cursor.fetchone():
                        messagebox.showerror(title="Error", message="La tabla 'usuarios' no existe en la base de datos")
                        return
                        
                    cursor.execute(consulta, parametros)
                    result = cursor.fetchall()

                    if result:
                        # Si el controlador existe, muestra el Container
                        if self.controlador:
                            self.control1()
                        else:
                            messagebox.showinfo(title="Éxito", message="Login exitoso, pero el controlador no está disponible en modo standalone")
                    else:
                        self.username.delete(0, 'end')
                        self.password.delete(0, 'end')
                        messagebox.showerror(title="Error", message="Usuario y/o contraseña incorrecta")
            except sqlite3.Error as e:
                messagebox.showerror(title="Error de Base de Datos", message=f"Error de conexión: {e}")
                # Intentemos crear la tabla usuarios si no existe
                try:
                    with sqlite3.connect(self.db_name) as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        )''')
                        conn.commit()
                        messagebox.showinfo(title="Base de Datos", message="Se ha creado la tabla 'usuarios'. Intente registrarse primero.")
                except sqlite3.Error as e2:
                    messagebox.showerror(title="Error Fatal", message=f"No se pudo crear la tabla: {e2}")
        else:
            messagebox.showerror(title="Error", message="Llene todas las casillas")

    def control1(self):
        self.controlador.show_frame(Container)

    def control2(self):
        self.controlador.show_frame(Registro)

    def widgets(self):
        fondo = tk.Frame(self, bg="#C6D9E3")
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)

        # Ruta absoluta a la imagen
        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(carpeta_actual, "imagenes", "fondo.png")

        # Verificar si la imagen existe
        if os.path.exists(ruta_imagen):
            self.bg_image = Image.open(ruta_imagen)
            self.bg_image = self.bg_image.resize((1100, 650))
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = ttk.Label(fondo, image=self.bg_image)
            self.bg_label.place(x=0, y=0, width=1100, height=650)
        else:
            print(f"No se encontró la imagen en: {ruta_imagen}")
            # Crear un fondo alternativo si no se encuentra la imagen
            self.bg_label = ttk.Label(fondo, background="#C6D9E3")
            self.bg_label.place(x=0, y=0, width=1100, height=650)

        frame1 = tk.Frame(self, bg="#FFFFFF", highlightbackground="black", highlightthickness=1)
        frame1.place(x=350, y=70, width=400, height=560)

        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(carpeta_actual, "imagenes", "logo1.png")

        # Verificar si la imagen del logo existe
        if os.path.exists(ruta_imagen):
            self.logo_image = Image.open(ruta_imagen)
            self.logo_image = self.logo_image.resize((200, 200))
            self.logo_image = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = ttk.Label(frame1, image=self.logo_image, background="#FFFFFF")
            self.logo_label.place(x=100, y=20)
        else:
            print(f"No se encontró la imagen del logo en: {ruta_imagen}")
            # Crear un espacio para el logo si no se encuentra la imagen
            self.logo_label = ttk.Label(frame1, text="LOGO", font="arial 24 bold", background="#FFFFFF")
            self.logo_label.place(x=100, y=20, width=200, height=200)

        user = ttk.Label(frame1, text="Nombre de usuario", font="arial 16 bold", background="#FFFFFF")
        user.place(x=100, y=250)
        self.username = ttk.Entry(frame1, font="arial 16 bold")
        self.username.place(x=80, y=290, width=240, height=40)
        
        pas = ttk.Label(frame1, text="Contraseña", font="arial 16 bold", background="#FFFFFF")
        pas.place(x=100, y=340)
        self.password = ttk.Entry(frame1, show="*", font="Arial 16 bold")
        self.password.place(x=80, y=380, width=240, height=40)

        btn1 = tk.Button(frame1, text="Iniciar", font="arial 16 bold", command=self.login)
        btn1.place(x=80, y=440, width=240, height=40)

        btn2 = tk.Button(frame1, text="Registrar", font="arial 16 bold", command=self.control2)
        btn2.place(x=80, y=500, width=240, height=40)


class Registro(tk.Frame):
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    db_name = os.path.join(carpeta_actual, "database.db")

    def __init__(self, padre, controlador):
        super().__init__(padre)
        self.pack()
        self.place(x=0, y=0, width=1100, height=650)
        self.controlador = controlador
        self.widgets()

    def validacion(self, user, pas):
        return len(user) > 0 and len(pas) > 0

    def eje_consulta(self, consulta, parametros=()):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(consulta, parametros)
                conn.commit()  # Corregido: faltaba los paréntesis en commit
        except sqlite3.Error as e:
            messagebox.showerror(title="Error", message=f"Error al ejecutar la consulta: {e}")

    def registro(self):
        user = self.username.get()
        pas = self.password.get()
        key = self.key.get()
        if self.validacion(user, pas):
            if len(pas) < 6:
                messagebox.showinfo(title="Error", message="Contraseña demasiado corta")
                self.username.delete(0, 'end')
                self.password.delete(0, 'end')
            else:
                if key == "1234":
                    try:
                        # Verificar si la tabla usuarios existe
                        with sqlite3.connect(self.db_name) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
                            if not cursor.fetchone():
                                # Crear la tabla si no existe
                                cursor.execute('''
                                CREATE TABLE IF NOT EXISTS usuarios (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    username TEXT NOT NULL UNIQUE,
                                    password TEXT NOT NULL
                                )''')
                                conn.commit()
                    
                            # Verificar si el usuario ya existe
                            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (user,))
                            if cursor.fetchone():
                                messagebox.showerror(title="Error", message="El nombre de usuario ya existe")
                                return
                    
                            # Insertar el nuevo usuario
                            consulta = "INSERT INTO usuarios (username, password) VALUES (?, ?)"
                            parametros = (user, pas)
                            cursor.execute(consulta, parametros)
                            conn.commit()
                            messagebox.showinfo(title="Éxito", message="Usuario registrado correctamente")
                            
                            # Si el controlador existe, mostrar el Container
                            if self.controlador:
                                self.control1()
                            else:
                                self.username.delete(0, 'end')
                                self.password.delete(0, 'end')
                                self.key.delete(0, 'end')
                    except sqlite3.Error as e:
                        messagebox.showerror(title="Error de Base de Datos", message=f"Error al registrar: {e}")
                else:
                    messagebox.showerror(title="Registro", message="Error al ingresar el código de registro")
        else:
            messagebox.showerror(title="Error", message="Llene sus datos")

    def control1(self):
        self.controlador.show_frame(Container)

    def control2(self):
        self.controlador.show_frame(Login)
    
    def widgets(self):
        fondo = tk.Frame(self, bg="#C6D9E3")
        fondo.pack()
        fondo.place(x=0, y=0, width=1100, height=650)

        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(carpeta_actual, "imagenes", "fondo.png")

        # Verificar si la imagen existe
        if os.path.exists(ruta_imagen):
            self.bg_image = Image.open(ruta_imagen)
            self.bg_image = self.bg_image.resize((1100, 650))
            self.bg_image = ImageTk.PhotoImage(self.bg_image)
            self.bg_label = ttk.Label(fondo, image=self.bg_image)
            self.bg_label.place(x=0, y=0, width=1100, height=650)
        else:
            print(f"No se encontró la imagen en: {ruta_imagen}")
            # Crear un fondo alternativo si no se encuentra la imagen
            self.bg_label = ttk.Label(fondo, background="#C6D9E3")
            self.bg_label.place(x=0, y=0, width=1100, height=650)

        frame1 = tk.Frame(self, bg="#FFFFFF", highlightbackground="black", highlightthickness=1)
        frame1.place(x=350, y=10, width=400, height=630)

        carpeta_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_imagen = os.path.join(carpeta_actual, "imagenes", "logo1.png")

        # Verificar si la imagen del logo existe
        if os.path.exists(ruta_imagen):
            self.logo_image = Image.open(ruta_imagen)
            self.logo_image = self.logo_image.resize((200, 200))
            self.logo_image = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = ttk.Label(frame1, image=self.logo_image, background="#FFFFFF")
            self.logo_label.place(x=100, y=20)
        else:
            print(f"No se encontró la imagen del logo en: {ruta_imagen}")
            # Crear un espacio para el logo si no se encuentra la imagen
            self.logo_label = ttk.Label(frame1, text="LOGO", font="arial 24 bold", background="#FFFFFF")
            self.logo_label.place(x=100, y=20, width=200, height=200)

        user = ttk.Label(frame1, text="Nombre de usuario", font="arial 16 bold", background="#FFFFFF")
        user.place(x=100, y=250)
        self.username = ttk.Entry(frame1, font="arial 16 bold")
        self.username.place(x=80, y=290, width=240, height=40)
        
        pas = ttk.Label(frame1, text="Contraseña", font="arial 16 bold", background="#FFFFFF")
        pas.place(x=100, y=340)
        self.password = ttk.Entry(frame1, show="*", font="Arial 16 bold")
        self.password.place(x=80, y=380, width=240, height=40)

        key = ttk.Label(frame1, text="Código de registro", font="arial 16 bold", background="#FFFFFF")
        key.place(x=100, y=430)
        self.key = ttk.Entry(frame1, show="*", font="Arial 16 bold")
        self.key.place(x=80, y=470, width=240, height=40)

        btn3 = tk.Button(frame1, text="Registrarse", font="arial 16 bold", command=self.registro)
        btn3.place(x=80, y=520, width=240, height=40)

        btn4 = tk.Button(frame1, text="Regresar", font="arial 16 bold", command=self.control2)
        btn4.place(x=80, y=570, width=240, height=40)


class AppPrincipal(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Sistema de Gestión")
        self.geometry("1100x650+120+30")
        self.resizable(False, False)
        
        self.contenedor = tk.Frame(self)
        self.contenedor.pack(side="top", fill="both", expand=True)
        
        self.frames = {}
        
        for F in (Login, Registro, Container):
            frame = F(self.contenedor, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Login)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


# Función para verificar y crear la base de datos si no existe
def crear_base_de_datos():
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(carpeta_actual, "database.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla usuarios si no existe
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )''')
        
        # Verificar si hay usuarios, si no hay ninguno, crear uno por defecto
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ("admin", "admin123"))
            print("Usuario admin creado con contraseña: admin123")
        
        conn.commit()
        conn.close()
        print(f"Base de datos verificada en: {db_path}")
        return True
    except sqlite3.Error as e:
        print(f"Error al crear/verificar la base de datos: {e}")
        return False


if __name__ == "__main__":
    # Verificar y crear la base de datos antes de iniciar la aplicación
    if crear_base_de_datos():
        try:
            # Intentar importar Container
            from container import Container
            app = AppPrincipal()
            app.mainloop()
        except ImportError:
            # Si Container no está disponible, ejecutar solo el Login
            root = tk.Tk()
            root.title("Pantalla de Login")
            root.geometry("1100x650+120+30")
            root.resizable(False, False)
            app = Login(root, None)
            app.pack(expand=True, fill="both")
            root.mainloop()
    else:
        print("No se pudo iniciar la aplicación debido a problemas con la base de datos.")