
# Sistema de Gestión Comercial
# Requisitos: pip install mysql-connector-python

import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SistemaGestionComercial:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.conectar_bd()
        self.crear_tablas()
        self.iniciar_interfaz()
    
    def conectar_bd(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="gestion_comercial"
            )
            self.cursor = self.conn.cursor()
            # Si la base de datos no existe, la creamos
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS gestion_comercial")
            self.cursor.execute("USE gestion_comercial")
            print("Conexión exitosa a la base de datos")
        except mysql.connector.Error as err:
            print(f"Error de conexión: {err}")
    
    def crear_tablas(self):
        try:
            # Tabla de productos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    precio DECIMAL(10, 2) NOT NULL,
                    stock INT NOT NULL
                )
            """)
            
            # Tabla de clientes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion TEXT
                )
            """)
            
            # Tabla de ventas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cliente_id INT,
                    fecha DATETIME NOT NULL,
                    total DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)
            
            # Tabla de detalles de venta
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalles_venta (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    venta_id INT,
                    producto_id INT,
                    cantidad INT NOT NULL,
                    precio_unitario DECIMAL(10, 2) NOT NULL,
                    subtotal DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            """)
            
            self.conn.commit()
            print("Tablas creadas correctamente")
        except mysql.connector.Error as err:
            print(f"Error al crear tablas: {err}")
    
    def iniciar_interfaz(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Gestión Comercial")
        self.root.geometry("800x600")
        
        # Crear pestañas
        self.tab_control = ttk.Notebook(self.root)
        
        self.tab_productos = ttk.Frame(self.tab_control)
        self.tab_clientes = ttk.Frame(self.tab_control)
        self.tab_ventas = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_productos, text="Productos")
        self.tab_control.add(self.tab_clientes, text="Clientes")
        self.tab_control.add(self.tab_ventas, text="Ventas")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Configurar cada pestaña
        self.configurar_tab_productos()
        self.configurar_tab_clientes()
        self.configurar_tab_ventas()
        
        self.root.mainloop()
    
    def configurar_tab_productos(self):
        # Frame para formulario
        frm_form = ttk.LabelFrame(self.tab_productos, text="Datos del Producto")
        frm_form.pack(padx=10, pady=10, fill="x")
        
        # Campos del formulario
        ttk.Label(frm_form, text="Nombre:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.producto_nombre = ttk.Entry(frm_form, width=40)
        self.producto_nombre.grid(column=1, row=0, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Descripción:").grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
        self.producto_descripcion = ttk.Entry(frm_form, width=40)
        self.producto_descripcion.grid(column=1, row=1, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Precio:").grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
        self.producto_precio = ttk.Entry(frm_form, width=40)
        self.producto_precio.grid(column=1, row=2, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Stock:").grid(column=0, row=3, padx=10, pady=5, sticky=tk.W)
        self.producto_stock = ttk.Entry(frm_form, width=40)
        self.producto_stock.grid(column=1, row=3, padx=10, pady=5)
        
        # Botones
        frm_botones = ttk.Frame(self.tab_productos)
        frm_botones.pack(padx=10, pady=10, fill="x")
        
        ttk.Button(frm_botones, text="Guardar", command=self.guardar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Actualizar", command=self.actualizar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Eliminar", command=self.eliminar_producto).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Limpiar", command=self.limpiar_producto).pack(side=tk.LEFT, padx=5)
        
        # Tabla de productos
        frm_tabla = ttk.LabelFrame(self.tab_productos, text="Lista de Productos")
        frm_tabla.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Crear treeview
        self.tabla_productos = ttk.Treeview(frm_tabla, columns=("id", "nombre", "descripcion", "precio", "stock"))
        self.tabla_productos.heading("#0", text="")
        self.tabla_productos.heading("id", text="ID")
        self.tabla_productos.heading("nombre", text="Nombre")
        self.tabla_productos.heading("descripcion", text="Descripción")
        self.tabla_productos.heading("precio", text="Precio")
        self.tabla_productos.heading("stock", text="Stock")
        
        self.tabla_productos.column("#0", width=0, stretch=tk.NO)
        self.tabla_productos.column("id", width=50, anchor=tk.CENTER)
        self.tabla_productos.column("nombre", width=150, anchor=tk.W)
        self.tabla_productos.column("descripcion", width=200, anchor=tk.W)
        self.tabla_productos.column("precio", width=100, anchor=tk.E)
        self.tabla_productos.column("stock", width=80, anchor=tk.CENTER)
        
        self.tabla_productos.pack(fill="both", expand=True)
        self.tabla_productos.bind("<<TreeviewSelect>>", self.seleccionar_producto)
        
        # Cargar datos
        self.cargar_productos()
    
    def configurar_tab_clientes(self):
        # Frame para formulario
        frm_form = ttk.LabelFrame(self.tab_clientes, text="Datos del Cliente")
        frm_form.pack(padx=10, pady=10, fill="x")
        
        # Campos del formulario
        ttk.Label(frm_form, text="Nombre:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.cliente_nombre = ttk.Entry(frm_form, width=40)
        self.cliente_nombre.grid(column=1, row=0, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Teléfono:").grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
        self.cliente_telefono = ttk.Entry(frm_form, width=40)
        self.cliente_telefono.grid(column=1, row=1, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Email:").grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
        self.cliente_email = ttk.Entry(frm_form, width=40)
        self.cliente_email.grid(column=1, row=2, padx=10, pady=5)
        
        ttk.Label(frm_form, text="Dirección:").grid(column=0, row=3, padx=10, pady=5, sticky=tk.W)
        self.cliente_direccion = ttk.Entry(frm_form, width=40)
        self.cliente_direccion.grid(column=1, row=3, padx=10, pady=5)
        
        # Botones
        frm_botones = ttk.Frame(self.tab_clientes)
        frm_botones.pack(padx=10, pady=10, fill="x")
        
        ttk.Button(frm_botones, text="Guardar", command=self.guardar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Actualizar", command=self.actualizar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Eliminar", command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Limpiar", command=self.limpiar_cliente).pack(side=tk.LEFT, padx=5)
        
        # Tabla de clientes
        frm_tabla = ttk.LabelFrame(self.tab_clientes, text="Lista de Clientes")
        frm_tabla.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Crear treeview
        self.tabla_clientes = ttk.Treeview(frm_tabla, columns=("id", "nombre", "telefono", "email", "direccion"))
        self.tabla_clientes.heading("#0", text="")
        self.tabla_clientes.heading("id", text="ID")
        self.tabla_clientes.heading("nombre", text="Nombre")
        self.tabla_clientes.heading("telefono", text="Teléfono")
        self.tabla_clientes.heading("email", text="Email")
        self.tabla_clientes.heading("direccion", text="Dirección")
        
        self.tabla_clientes.column("#0", width=0, stretch=tk.NO)
        self.tabla_clientes.column("id", width=50, anchor=tk.CENTER)
        self.tabla_clientes.column("nombre", width=150, anchor=tk.W)
        self.tabla_clientes.column("telefono", width=100, anchor=tk.W)
        self.tabla_clientes.column("email", width=150, anchor=tk.W)
        self.tabla_clientes.column("direccion", width=200, anchor=tk.W)
        
        self.tabla_clientes.pack(fill="both", expand=True)
        self.tabla_clientes.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
        
        # Cargar datos
        self.cargar_clientes()
    
    def configurar_tab_ventas(self):
        # Frame para formulario
        frm_form = ttk.LabelFrame(self.tab_ventas, text="Nueva Venta")
        frm_form.pack(padx=10, pady=10, fill="x")
        
        # Cliente
        ttk.Label(frm_form, text="Cliente:").grid(column=0, row=0, padx=10, pady=5, sticky=tk.W)
        self.venta_cliente = ttk.Combobox(frm_form, width=40)
        self.venta_cliente.grid(column=1, row=0, padx=10, pady=5)
        
        # Producto
        ttk.Label(frm_form, text="Producto:").grid(column=0, row=1, padx=10, pady=5, sticky=tk.W)
        self.venta_producto = ttk.Combobox(frm_form, width=40)
        self.venta_producto.grid(column=1, row=1, padx=10, pady=5)
        
        # Cantidad
        ttk.Label(frm_form, text="Cantidad:").grid(column=0, row=2, padx=10, pady=5, sticky=tk.W)
        self.venta_cantidad = ttk.Entry(frm_form, width=40)
        self.venta_cantidad.grid(column=1, row=2, padx=10, pady=5)
        
        # Botones
        frm_botones = ttk.Frame(self.tab_ventas)
        frm_botones.pack(padx=10, pady=10, fill="x")
        
        ttk.Button(frm_botones, text="Agregar a carrito", command=self.agregar_carrito).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Completar venta", command=self.completar_venta).pack(side=tk.LEFT, padx=5)
        ttk.Button(frm_botones, text="Cancelar venta", command=self.cancelar_venta).pack(side=tk.LEFT, padx=5)
        
        # Tabla del carrito
        frm_carrito = ttk.LabelFrame(self.tab_ventas, text="Carrito")
        frm_carrito.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tabla_carrito = ttk.Treeview(frm_carrito, columns=("id", "producto", "cantidad", "precio", "subtotal"))
        self.tabla_carrito.heading("#0", text="")
        self.tabla_carrito.heading("id", text="ID")
        self.tabla_carrito.heading("producto", text="Producto")
        self.tabla_carrito.heading("cantidad", text="Cantidad")
        self.tabla_carrito.heading("precio", text="Precio Unit.")
        self.tabla_carrito.heading("subtotal", text="Subtotal")
        
        self.tabla_carrito.column("#0", width=0, stretch=tk.NO)
        self.tabla_carrito.column("id", width=50, anchor=tk.CENTER)
        self.tabla_carrito.column("producto", width=200, anchor=tk.W)
        self.tabla_carrito.column("cantidad", width=100, anchor=tk.CENTER)
        self.tabla_carrito.column("precio", width=100, anchor=tk.E)
        self.tabla_carrito.column("subtotal", width=100, anchor=tk.E)
        
        self.tabla_carrito.pack(fill="both", expand=True)
        
        # Total
        frm_total = ttk.Frame(self.tab_ventas)
        frm_total.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frm_total, text="TOTAL:").pack(side=tk.LEFT, padx=5)
        self.label_total = ttk.Label(frm_total, text="$0.00")
        self.label_total.pack(side=tk.LEFT, padx=5)
        
        # Inicializar carrito
        self.carrito = []
        self.total_venta = 0.0
        
        # Cargar datos en comboboxes
        self.cargar_combos_venta()
    
    # Métodos para productos
    def cargar_productos(self):
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
        
        # Consultar productos
        try:
            self.cursor.execute("SELECT * FROM productos")
            productos = self.cursor.fetchall()
            
            for producto in productos:
                self.tabla_productos.insert("", tk.END, values=producto)
        except mysql.connector.Error as err:
            print(f"Error al cargar productos: {err}")
    
    def guardar_producto(self):
        try:
            nombre = self.producto_nombre.get()
            descripcion = self.producto_descripcion.get()
            precio = float(self.producto_precio.get())
            stock = int(self.producto_stock.get())
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
            
            self.cursor.execute("""
                INSERT INTO productos (nombre, descripcion, precio, stock)
                VALUES (%s, %s, %s, %s)
            """, (nombre, descripcion, precio, stock))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Producto guardado correctamente")
            self.limpiar_producto()
            self.cargar_productos()
            self.cargar_combos_venta()
        except ValueError:
            messagebox.showerror("Error", "Precio y stock deben ser números")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo guardar el producto: {err}")
    
    def seleccionar_producto(self, event):
        try:
            item_seleccionado = self.tabla_productos.selection()[0]
            valores = self.tabla_productos.item(item_seleccionado, "values")
            
            # Limpiar formulario
            self.limpiar_producto()
            
            # Cargar datos en formulario
            self.producto_id = valores[0]
            self.producto_nombre.insert(0, valores[1])
            self.producto_descripcion.insert(0, valores[2])
            self.producto_precio.insert(0, valores[3])
            self.producto_stock.insert(0, valores[4])
        except IndexError:
            pass
    
    def actualizar_producto(self):
        try:
            if not hasattr(self, "producto_id"):
                messagebox.showerror("Error", "Seleccione un producto para actualizar")
                return
            
            nombre = self.producto_nombre.get()
            descripcion = self.producto_descripcion.get()
            precio = float(self.producto_precio.get())
            stock = int(self.producto_stock.get())
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del producto es obligatorio")
                return
            
            self.cursor.execute("""
                UPDATE productos
                SET nombre = %s, descripcion = %s, precio = %s, stock = %s
                WHERE id = %s
            """, (nombre, descripcion, precio, stock, self.producto_id))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            self.limpiar_producto()
            self.cargar_productos()
            self.cargar_combos_venta()
        except ValueError:
            messagebox.showerror("Error", "Precio y stock deben ser números")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo actualizar el producto: {err}")
    
    def eliminar_producto(self):
        try:
            if not hasattr(self, "producto_id"):
                messagebox.showerror("Error", "Seleccione un producto para eliminar")
                return
            
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
                self.cursor.execute("DELETE FROM productos WHERE id = %s", (self.producto_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                self.limpiar_producto()
                self.cargar_productos()
                self.cargar_combos_venta()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar el producto: {err}")
    
    def limpiar_producto(self):
        self.producto_nombre.delete(0, tk.END)
        self.producto_descripcion.delete(0, tk.END)
        self.producto_precio.delete(0, tk.END)
        self.producto_stock.delete(0, tk.END)
        if hasattr(self, "producto_id"):
            delattr(self, "producto_id")
    
    # Métodos para clientes
    def cargar_clientes(self):
        # Limpiar tabla
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)
        
        # Consultar clientes
        try:
            self.cursor.execute("SELECT * FROM clientes")
            clientes = self.cursor.fetchall()
            
            for cliente in clientes:
                self.tabla_clientes.insert("", tk.END, values=cliente)
        except mysql.connector.Error as err:
            print(f"Error al cargar clientes: {err}")
    
    def guardar_cliente(self):
        try:
            nombre = self.cliente_nombre.get()
            telefono = self.cliente_telefono.get()
            email = self.cliente_email.get()
            direccion = self.cliente_direccion.get()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del cliente es obligatorio")
                return
            
            self.cursor.execute("""
                INSERT INTO clientes (nombre, telefono, email, direccion)
                VALUES (%s, %s, %s, %s)
            """, (nombre, telefono, email, direccion))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            self.limpiar_cliente()
            self.cargar_clientes()
            self.cargar_combos_venta()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo guardar el cliente: {err}")
    
    def seleccionar_cliente(self, event):
        try:
            item_seleccionado = self.tabla_clientes.selection()[0]
            valores = self.tabla_clientes.item(item_seleccionado, "values")
            
            # Limpiar formulario
            self.limpiar_cliente()
            
            # Cargar datos en formulario
            self.cliente_id = valores[0]
            self.cliente_nombre.insert(0, valores[1])
            self.cliente_telefono.insert(0, valores[2])
            self.cliente_email.insert(0, valores[3])
            self.cliente_direccion.insert(0, valores[4])
        except IndexError:
            pass
    
    def actualizar_cliente(self):
        try:
            if not hasattr(self, "cliente_id"):
                messagebox.showerror("Error", "Seleccione un cliente para actualizar")
                return
            
            nombre = self.cliente_nombre.get()
            telefono = self.cliente_telefono.get()
            email = self.cliente_email.get()
            direccion = self.cliente_direccion.get()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre del cliente es obligatorio")
                return
            
            self.cursor.execute("""
                UPDATE clientes
                SET nombre = %s, telefono = %s, email = %s, direccion = %s
                WHERE id = %s
            """, (nombre, telefono, email, direccion, self.cliente_id))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.limpiar_cliente()
            self.cargar_clientes()
            self.cargar_combos_venta()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {err}")
    
    def eliminar_cliente(self):
        try:
            if not hasattr(self, "cliente_id"):
                messagebox.showerror("Error", "Seleccione un cliente para eliminar")
                return
            
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?"):
                self.cursor.execute("DELETE FROM clientes WHERE id = %s", (self.cliente_id,))
                self.conn.commit()
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self.limpiar_cliente()
                self.cargar_clientes()
                self.cargar_combos_venta()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"No se pudo eliminar el cliente: {err}")
    
    def limpiar_cliente(self):
        self.cliente_nombre.delete(0, tk.END)
        self.cliente_telefono.delete(0, tk.END)
        self.cliente_email.delete(0, tk.END)
        self.cliente_direccion.delete(0, tk.END)
        if hasattr(self, "cliente_id"):
            delattr(self, "cliente_id")
    
    # Métodos para ventas
    def cargar_combos_venta(self):
        # Cargar clientes en combobox
        self.clientes_data = {}
        try:
            self.cursor.execute("SELECT id, nombre FROM clientes")
            clientes = self.cursor.fetchall()
            
            clientes_nombres = []
            for cliente in clientes:
                self.clientes_data[cliente[1]] = cliente[0]
                clientes_nombres.append(cliente[1])
            
            self.venta_cliente["values"] = clientes_nombres
        except mysql.connector.Error as err:
            print(f"Error al cargar clientes en combobox: {err}")
        
        # Cargar productos en combobox
        self.productos_data = {}
        try:
            self.cursor.execute("SELECT id, nombre, precio, stock FROM productos")
            productos = self.cursor.fetchall()
            
            productos_nombres = []
            for producto in productos:
                self.productos_data[producto[1]] = {
                    "id": producto[0],
                    "precio": producto[2],
                    "stock": producto[3]
                }
                productos_nombres.append(producto[1])
            
            self.venta_producto["values"] = productos_nombres
        except mysql.connector.Error as err:
            print(f"Error al cargar productos en combobox: {err}")
    
    def agregar_carrito(self):
        try:
            producto_nombre = self.venta_producto.get()
            cantidad = int(self.venta_cantidad.get())
            
            if not producto_nombre:
                messagebox.showerror("Error", "Seleccione un producto")
                return
            
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            producto_data = self.productos_data[producto_nombre]
            producto_id = producto_data["id"]
            precio = producto_data["precio"]
            stock = producto_data["stock"]
            
            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {stock}")
                return
            
            subtotal = precio * cantidad
            
            # Agregar al carrito
            item = {
                "id": producto_id,
                "nombre": producto_nombre,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal
            }
            
            self.carrito.append(item)
            self.total_venta += subtotal
            
            # Actualizar tabla
            self.tabla_carrito.insert("", tk.END, values=(producto_id, producto_nombre, cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))
            
            # Actualizar total
            self.label_total.config(text=f"${self.total_venta:.2f}")
            
            # Limpiar campo cantidad
            self.venta_cantidad.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero")
        except KeyError:
            messagebox.showerror("Error", "Producto no encontrado")
    
    def completar_venta(self):
        try:
            if not self.carrito:
                messagebox.showerror("Error", "El carrito está vacío")
                return
            
            cliente_nombre = self.venta_cliente.get()
            if not cliente_nombre:
                messagebox.showerror("Error", "Seleccione un cliente")
                return
            
            cliente_id = self.clientes_data[cliente_nombre]
            fecha = datetime.now()
            
            # Crear venta
            self.cursor.execute("""
                INSERT INTO ventas (cliente_id, fecha, total)
                VALUES (%s, %s, %s)
            """, (cliente_id, fecha, self.total_venta))
            
            venta_id = self.cursor.lastrowid
            
            # Agregar detalles de venta
            for item in self.carrito:
                self.cursor.execute("""
                    INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                """, (venta_id, item["id"], item["cantidad"], item["precio"], item["subtotal"]))
                
                # Actualizar stock
                self.cursor.execute("""
                    UPDATE productos
                    SET stock = stock - %s
                    WHERE id = %s
                """, (item["cantidad"], item["id"]))
            
            self.conn.commit()
            messagebox.showinfo("Éxito", f"Venta #{venta_id} completada correctamente")
            self.cancelar_venta()
            self.cargar_productos()
            self.cargar_combos_venta()
        except KeyError:
            messagebox.showerror("Error", "Cliente no encontrado")
    