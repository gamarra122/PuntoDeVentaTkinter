import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import cv2
from pyzbar.pyzbar import decode
from PIL import Image, ImageTk
import random
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import os

# Clase para manejar la base de datos
class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.add_barcode_fields_if_not_exists()
        
    def connect(self):
        """Conecta a la base de datos"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
    def add_barcode_fields_if_not_exists(self):
        """Agrega campos relacionados con códigos de barras si no existen"""
        try:
            self.cursor.execute("PRAGMA table_info(articulos)")
            columns = [info[1] for info in self.cursor.fetchall()]
            
            if "codigo_barras" not in columns:
                self.cursor.execute("ALTER TABLE articulos ADD COLUMN codigo_barras TEXT")
                self.conn.commit()
            
            if "barcode_image_path" not in columns:
                self.cursor.execute("ALTER TABLE articulos ADD COLUMN barcode_image_path TEXT")
                self.conn.commit()
                
            print("Estructura de base de datos verificada correctamente")
        except sqlite3.Error as e:
            print(f"Error al modificar la tabla: {e}")
    
    def get_articulo_by_barcode(self, barcode):
        """Busca un artículo por su código de barras"""
        try:
            self.cursor.execute("SELECT * FROM articulos WHERE codigo_barras = ?", (barcode,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error al buscar por código de barras: {e}")
            return None
    
    def get_articulo_by_id(self, articulo_id):
        """Busca un artículo por su ID"""
        try:
            self.cursor.execute("SELECT * FROM articulos WHERE id = ?", (articulo_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error al buscar artículo: {e}")
            return None
    
    def update_articulo_barcode(self, articulo_id, barcode_data, image_path=None):
        """Actualiza el código de barras de un artículo y su imagen"""
        try:
            if image_path:
                self.cursor.execute("UPDATE articulos SET codigo_barras = ?, barcode_image_path = ? WHERE id = ?", 
                                   (barcode_data, image_path, articulo_id))
            else:
                self.cursor.execute("UPDATE articulos SET codigo_barras = ? WHERE id = ?", 
                                   (barcode_data, articulo_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar código de barras: {e}")
            return False
    
    def get_all_articulos(self):
        """Obtiene todos los artículos de la base de datos"""
        try:
            self.cursor.execute("SELECT * FROM articulos")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener artículos: {e}")
            return []
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()

class BarcodeGenerator:
    @staticmethod
    def generate_ean13():
        """Genera un código EAN-13 válido"""
        # Los primeros 12 dígitos
        digits = [random.randint(0, 9) for _ in range(12)]
        
        # Cálculo del dígito de verificación
        odd_sum = sum(digits[0::2])
        even_sum = sum(digits[1::2]) * 3
        total_sum = odd_sum + even_sum
        check_digit = (10 - (total_sum % 10)) % 10
        
        # Añadir el dígito de verificación
        digits.append(check_digit)
        
        # Convertir a string
        return ''.join(map(str, digits))
    
    @staticmethod
    def create_barcode_image(code, articulo_id=None):
        """Crea una imagen del código de barras"""
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN(code, writer=ImageWriter())
        
        # Crear directorio para códigos de barras si no existe
        if not os.path.exists('barcodes'):
            os.makedirs('barcodes')
        
        # Nombre del archivo basado en el ID del artículo si está disponible
        if articulo_id:
            filename = f"barcodes/articulo_{articulo_id}_{code}"
        else:
            filename = f"barcodes/{code}"
            
        # Guardar y devolver la ruta
        ean.save(filename)
        return f"{filename}.png"

class BarcodeScanner:
    def __init__(self):
        self.cap = None
    
    def start_camera(self):
        """Inicia la cámara para escanear códigos de barras"""
        self.cap = cv2.VideoCapture(0)
        return self.cap.isOpened()
    
    def stop_camera(self):
        """Detiene la cámara"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
    
    def scan_frame(self, frame):
        """Escanea un frame para detectar códigos de barras"""
        if frame is not None:
            barcodes = decode(frame)
            for barcode in barcodes:
                # Extraer y devolver los datos del código de barras
                barcode_data = barcode.data.decode('utf-8')
                return barcode_data
        return None

class CarritoVenta:
    def __init__(self):
        self.items = []  # Lista de tuplas (articulo_id, nombre, precio, cantidad)
        self.total = 0
    
    def agregar_item(self, articulo, cantidad):
        """Agrega un artículo al carrito"""
        articulo_id = articulo[0]
        nombre = articulo[1]
        precio = float(articulo[2])
        
        # Verificar si el artículo ya está en el carrito
        for i, item in enumerate(self.items):
            if item[0] == articulo_id:
                # Actualizar cantidad si ya existe
                self.items[i] = (articulo_id, nombre, precio, item[3] + cantidad)
                self.calcular_total()
                return True
        
        # Agregar nuevo artículo al carrito
        self.items.append((articulo_id, nombre, precio, cantidad))
        self.calcular_total()
        return True
    
    def eliminar_item(self, item_index):
        """Elimina un artículo del carrito por su índice"""
        if 0 <= item_index < len(self.items):
            del self.items[item_index]
            self.calcular_total()
            return True
        return False
    
    def calcular_total(self):
        """Calcula el total de la venta"""
        self.total = sum(item[2] * item[3] for item in self.items)
        return self.total
    
    def vaciar_carrito(self):
        """Vacía el carrito"""
        self.items = []
        self.total = 0

class Pedidos(tk.Frame):
    def __init__(self, padre):
        super().__init__(padre)
        self.padre = padre
        self.db_manager = DatabaseManager("database.db")
        self.barcode_scanner = BarcodeScanner()
        self.camera_active = False
        self.video_frame = None
        self.carrito = CarritoVenta()
        self.articulo_actual = None
        self.widgets()
    
    def widgets(self):
        """Crea los widgets de la interfaz"""
        # Título
        label = tk.Label(self, text="Sistema de Pedidos", font=("Arial", 16, "bold"))
        label.pack(pady=5)
        
        # Panel principal con pestañas
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pestaña de ventas
        ventas_frame = ttk.Frame(notebook)
        notebook.add(ventas_frame, text="Ventas")
        
        # Panel de escáner
        self.setup_scanner_panel(ventas_frame)
        
        # Panel de artículos y carrito
        self.setup_tables_panel(ventas_frame)
        
        # Pestaña de gestión de códigos
        barcode_mgmt_frame = ttk.Frame(notebook)
        notebook.add(barcode_mgmt_frame, text="Gestión de Códigos")
        self.setup_barcode_mgmt(barcode_mgmt_frame)
    
    def setup_scanner_panel(self, parent):
        scanner_frame = tk.LabelFrame(parent, text="Escáner de Códigos")
        scanner_frame.pack(fill=tk.X, padx=5, pady=5)
        
        btn_frame = tk.Frame(scanner_frame)
        btn_frame.pack(fill=tk.X)
        
        btn_scan = tk.Button(btn_frame, text="Iniciar Escaneo", command=self.start_scanning)
        btn_scan.pack(side=tk.LEFT, padx=5, pady=5)
        
        btn_stop = tk.Button(btn_frame, text="Detener Escaneo", command=self.stop_scanning)
        btn_stop.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.video_frame = tk.Label(scanner_frame)
        self.video_frame.pack(pady=5)
        
        cantidad_frame = tk.Frame(scanner_frame)
        cantidad_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cantidad_frame, text="Cantidad:").pack(side=tk.LEFT, padx=5)
        self.cantidad_var = tk.StringVar(value="1")
        self.entrada_cantidad = tk.Entry(cantidad_frame, textvariable=self.cantidad_var, width=5)
        self.entrada_cantidad.pack(side=tk.LEFT)
        
        self.btn_agregar_carrito = tk.Button(cantidad_frame, text="Agregar al Carrito", 
                                         command=self.agregar_a_carrito, state=tk.DISABLED)
        self.btn_agregar_carrito.pack(side=tk.LEFT, padx=5)
    
    def setup_tables_panel(self, parent):
        tablas_frame = tk.Frame(parent)
        tablas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    # Tabla de artículos
        articulos_frame = tk.LabelFrame(tablas_frame, text="Artículos Disponibles")
        articulos_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
        columns = ("ID", "Nombre", "Precio", "Stock", "Código")
        self.articulos_table = ttk.Treeview(articulos_frame, columns=columns, show="headings")
    
    # Configurar encabezados y anchos personalizados
        self.articulos_table.heading("ID", text="ID")
        self.articulos_table.column("ID", width=40, anchor=tk.CENTER)
    
        self.articulos_table.heading("Nombre", text="Nombre")
        self.articulos_table.column("Nombre", width=150, anchor=tk.W)
    
        self.articulos_table.heading("Precio", text="Precio")
        self.articulos_table.column("Precio", width=80, anchor=tk.E)
    
        self.articulos_table.heading("Stock", text="Stock")
        self.articulos_table.column("Stock", width=80, anchor=tk.E)
    
        self.articulos_table.heading("Código", text="Código")
        self.articulos_table.column("Código", width=80, anchor=tk.CENTER)
    
        scrollbar = ttk.Scrollbar(articulos_frame, orient=tk.VERTICAL, command=self.articulos_table.yview)
        self.articulos_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.articulos_table.pack(fill=tk.BOTH, expand=True)
        self.articulos_table.bind("<Double-1>", self.seleccionar_articulo)
    
    # Tabla del carrito
        carrito_frame = tk.LabelFrame(tablas_frame, text="Carrito de Compras")
        carrito_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
    
        columns = ("ID", "Nombre", "Precio", "Cant", "Subtotal")
        self.carrito_table = ttk.Treeview(carrito_frame, columns=columns, show="headings")
    
    # Configurar encabezados y anchos para la tabla del carrito
        self.carrito_table.heading("ID", text="ID")
        self.carrito_table.column("ID", width=40, anchor=tk.CENTER)
    
        self.carrito_table.heading("Nombre", text="Nombre")
        self.carrito_table.column("Nombre", width=150, anchor=tk.W)
    
        self.carrito_table.heading("Precio", text="Precio")
        self.carrito_table.column("Precio", width=80, anchor=tk.E)
    
        self.carrito_table.heading("Cant", text="Cant")
        self.carrito_table.column("Cant", width=60, anchor=tk.CENTER)
    
        self.carrito_table.heading("Subtotal", text="Subtotal")
        self.carrito_table.column("Subtotal", width=100, anchor=tk.E)
    
        scrollbar = ttk.Scrollbar(carrito_frame, orient=tk.VERTICAL, command=self.carrito_table.yview)
        self.carrito_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.carrito_table.pack(fill=tk.BOTH, expand=True)
    
    # Botones y total
        buttons_frame = tk.Frame(carrito_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
    
        tk.Button(buttons_frame, text="Eliminar Item", command=self.eliminar_del_carrito).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Finalizar Venta", command=self.procesar_venta).pack(side=tk.LEFT, padx=5)
    
        self.total_label = tk.Label(buttons_frame, text="Total: $0.00", font=("Arial", 12, "bold"))
        self.total_label.pack(side=tk.RIGHT, padx=10)
    
    # Cargar artículos
        self.load_articulos()
    
    
    def setup_barcode_mgmt(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel para buscar artículos
        search_frame = tk.LabelFrame(frame, text="Buscar Artículo")
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(search_frame, text="ID o Nombre:").grid(row=0, column=0, padx=5, pady=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(search_frame, text="Buscar", 
                  command=lambda: self.load_articulos()).grid(row=0, column=2, padx=5, pady=5)
        
        # Panel para generar códigos
        gen_frame = tk.LabelFrame(frame, text="Generar Código de Barras (EAN-13)")
        gen_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(gen_frame, text="Artículo ID:").grid(row=0, column=0, padx=5, pady=5)
        self.articulo_id_var = tk.StringVar()
        tk.Entry(gen_frame, textvariable=self.articulo_id_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(gen_frame, text="Generar y Guardar", 
                  command=self.generate_barcode).grid(row=0, column=2, padx=5, pady=5)
        
        # Panel de instrucciones
        instr_frame = tk.LabelFrame(frame, text="Instrucciones")
        instr_frame.pack(fill=tk.X, pady=10)
        
        instrucciones = """
1. Los códigos EAN-13 generados son estándar y escaneables
2. Las imágenes se guardan en la carpeta 'barcodes'
3. Puede imprimir las imágenes para usarlas en sus productos
4. Si desea usar un código específico, use el panel inferior
        """
        tk.Label(instr_frame, text=instrucciones, justify=tk.LEFT).pack(padx=5, pady=5)
        
        # Panel para asignar código manualmente
        assign_frame = tk.LabelFrame(frame, text="Asignar Código Manualmente")
        assign_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(assign_frame, text="Artículo ID:").grid(row=0, column=0, padx=5, pady=5)
        self.manual_id_var = tk.StringVar()
        tk.Entry(assign_frame, textvariable=self.manual_id_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(assign_frame, text="Código:").grid(row=0, column=2, padx=5, pady=5)
        self.manual_code_var = tk.StringVar()
        tk.Entry(assign_frame, textvariable=self.manual_code_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        tk.Button(assign_frame, text="Asignar y Guardar", 
                  command=self.assign_barcode_manually).grid(row=0, column=4, padx=5, pady=5)
    
    def load_articulos(self):
        """Carga los artículos en la tabla"""
        for item in self.articulos_table.get_children():
            self.articulos_table.delete(item)
    
        articulos = self.db_manager.get_all_articulos()
        for articulo in articulos:
            articulo_id = articulo[0]
            nombre = articulo[1] if len(articulo) > 1 else ""
            precio = articulo[2] if len(articulo) > 2 else ""  # Precio de venta al cliente
            stock = articulo[3] if len(articulo) > 3 else ""
            codigo_barras = articulo[4] if len(articulo) > 4 else ""
        
        # Insertar artículo en la tabla con el orden correcto de las columnas:
        # ID, Nombre, Precio, Stock, Código
            self.articulos_table.insert("", tk.END, values=(articulo_id, nombre, precio, stock, codigo_barras))
        
    # Mostrar número total de artículos en el sistema
        total_articulos = len(articulos)
        print(f"Se cargaron {total_articulos} artículos en la tabla")
    
    def generate_barcode(self):
        """Genera un código de barras para un artículo"""
        try:
            articulo_id = int(self.articulo_id_var.get())
            
            # Verificar que el artículo existe
            articulo = self.db_manager.get_articulo_by_id(articulo_id)
            if not articulo:
                messagebox.showerror("Error", f"No existe artículo con ID {articulo_id}")
                return
            
            # Generar código EAN-13
            barcode_data = BarcodeGenerator.generate_ean13()
            
            # Crear imagen del código de barras
            image_path = BarcodeGenerator.create_barcode_image(barcode_data, articulo_id)
            
            # Guardar en la base de datos
            if self.db_manager.update_articulo_barcode(articulo_id, barcode_data, image_path):
                messagebox.showinfo("Éxito", 
                                   f"Código generado: {barcode_data}\n"
                                   f"Para artículo: {articulo[1]}\n"
                                   f"Imagen guardada: {image_path}")
                self.load_articulos()
                self.articulo_id_var.set("")
            else:
                messagebox.showerror("Error", "No se pudo asignar el código de barras")
                
        except ValueError:
            messagebox.showerror("Error", "ID de artículo inválido")
    
    def start_scanning(self):
        """Inicia el escaneo de códigos de barras"""
        if self.camera_active:
            return
        
        if self.barcode_scanner.start_camera():
            self.camera_active = True
            self.update_camera()
        else:
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
    
    def update_camera(self):
        """Actualiza el frame de la cámara y busca códigos de barras"""
        if self.camera_active:
            ret, frame = self.barcode_scanner.cap.read()
            if ret:
                # Convertir el frame para tkinter
                cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2_img)
                img = img.resize((400, 300), Image.LANCZOS)  
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_frame.imgtk = imgtk
                self.video_frame.config(image=imgtk)
                
                # Buscar códigos de barras
                barcode_data = self.barcode_scanner.scan_frame(frame)
                if barcode_data:
                    self.process_barcode(barcode_data)
                
                self.after(10, self.update_camera)
            else:
                self.stop_scanning()
    
    def stop_scanning(self):
        """Detiene el escaneo"""
        self.camera_active = False
        self.barcode_scanner.stop_camera()
        self.video_frame.config(image="")
    
    def process_barcode(self, barcode_data):
        """Procesa el código escaneado"""
        self.stop_scanning()
        
        articulo = self.db_manager.get_articulo_by_barcode(barcode_data)
        
        if articulo:
            self.articulo_actual = articulo
            messagebox.showinfo("Artículo Encontrado", 
                              f"Código: {barcode_data}\nNombre: {articulo[1]}\nPrecio: ${articulo[2]}")
            self.btn_agregar_carrito.config(state=tk.NORMAL)
            self.entrada_cantidad.focus_set()
        else:
            response = messagebox.askyesno("Código No Registrado", 
                                        f"¿Asignar código {barcode_data} a un artículo?")
            if response:
                self.assign_barcode_to_article(barcode_data)
            self.btn_agregar_carrito.config(state=tk.DISABLED)
    
    def assign_barcode_to_article(self, barcode_data):
        """Asigna un código a un artículo"""
        articulo_id = simpledialog.askinteger("Asignar Código", "ID del artículo:")
        
        if articulo_id:
            # Verificar que el artículo existe
            articulo = self.db_manager.get_articulo_by_id(articulo_id)
            if not articulo:
                messagebox.showerror("Error", f"No existe artículo con ID {articulo_id}")
                return
                
            # Crear imagen del código de barras
            image_path = BarcodeGenerator.create_barcode_image(barcode_data, articulo_id)
            
            # Guardar en la base de datos
            if self.db_manager.update_articulo_barcode(articulo_id, barcode_data, image_path):
                messagebox.showinfo("Éxito", 
                                  f"Código {barcode_data} asignado al artículo: {articulo[1]}\n"
                                  f"Imagen guardada en: {image_path}")
                self.load_articulos()
            else:
                messagebox.showerror("Error", "No se pudo asignar el código")
    
    def assign_barcode_manually(self):
        """Asigna un código manualmente"""
        try:
            articulo_id = int(self.manual_id_var.get())
            codigo = self.manual_code_var.get().strip()
            
            # Validaciones
            if not codigo:
                messagebox.showerror("Error", "Ingrese un código válido")
                return
            
            # Verificar que el artículo existe
            articulo = self.db_manager.get_articulo_by_id(articulo_id)
            if not articulo:
                messagebox.showerror("Error", f"No existe artículo con ID {articulo_id}")
                return
            
            # Crear imagen del código de barras
            try:
                image_path = BarcodeGenerator.create_barcode_image(codigo, articulo_id)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar la imagen: {str(e)}")
                return
                
            # Guardar en la base de datos
            if self.db_manager.update_articulo_barcode(articulo_id, codigo, image_path):
                messagebox.showinfo("Éxito", 
                                  f"Código {codigo} asignado al artículo: {articulo[1]}\n"
                                  f"Imagen guardada en: {image_path}")
                self.load_articulos()
                self.manual_id_var.set("")
                self.manual_code_var.set("")
            else:
                messagebox.showerror("Error", "No se pudo asignar el código")
                
        except ValueError:
            messagebox.showerror("Error", "ID de artículo inválido")
    
    def seleccionar_articulo(self, event):
        """Selecciona un artículo de la tabla"""
        seleccion = self.articulos_table.selection()
        if seleccion:
            valores = self.articulos_table.item(seleccion[0], "values")
            articulo_id = valores[0]
            
            self.cursor = self.db_manager.conn.cursor()
            self.cursor.execute("SELECT * FROM articulos WHERE id = ?", (articulo_id,))
            articulo = self.cursor.fetchone()
            
            if articulo:
                self.articulo_actual = articulo
                self.btn_agregar_carrito.config(state=tk.NORMAL)
                self.entrada_cantidad.focus_set()
    
    def agregar_a_carrito(self):
        """Agrega artículo al carrito"""
        if self.articulo_actual:
            try:
                cantidad = int(self.cantidad_var.get())
                if cantidad <= 0:
                    messagebox.showerror("Error", "Cantidad inválida")
                    return
                
                stock_disponible = int(self.articulo_actual[3])
                if cantidad > stock_disponible:
                    messagebox.showerror("Error", f"Stock insuficiente ({stock_disponible})")
                    return
                
                self.carrito.agregar_item(self.articulo_actual, cantidad)
                self.actualizar_tabla_carrito()
                
                self.cantidad_var.set("1")
                self.btn_agregar_carrito.config(state=tk.DISABLED)
                self.articulo_actual = None
                
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")
    
    def actualizar_tabla_carrito(self):
        """Actualiza la tabla del carrito"""
        for item in self.carrito_table.get_children():
            self.carrito_table.delete(item)
        
        for item in self.carrito.items:
            articulo_id, nombre, precio, cantidad = item
            subtotal = precio * cantidad
            
            self.carrito_table.insert("", tk.END, 
                                    values=(articulo_id, nombre, f"${precio:.2f}", 
                                            cantidad, f"${subtotal:.2f}"))
        
        self.total_label.config(text=f"Total: ${self.carrito.total:.2f}")
    
    def eliminar_del_carrito(self):
        """Elimina artículo del carrito"""
        seleccion = self.carrito_table.selection()
        if seleccion:
            index = self.carrito_table.index(seleccion[0])
            
            if self.carrito.eliminar_item(index):
                self.actualizar_tabla_carrito()
    
    def procesar_venta(self):
        """Procesa la venta"""
        if not self.carrito.items:
            messagebox.showinfo("Carrito Vacío", "No hay artículos en el carrito")
            return
        
        # Aquí implementar registro de venta, actualización de inventario, etc.
        messagebox.showinfo("Venta Procesada", f"Venta por ${self.carrito.total:.2f} completada!")
        
        self.carrito.vaciar_carrito()
        self.actualizar_tabla_carrito()


if __name__ == "__main__":
    # Crear ventana principal
    root = tk.Tk()
    root.title("Sistema de Gestión de Ventas")
    root.geometry("1024x768")
    
    app = Pedidos(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()