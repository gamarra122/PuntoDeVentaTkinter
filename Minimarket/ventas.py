import sqlite3
import datetime
import threading
import tkinter as tk
from tkinter import RIGHT, LEFT, TOP, BOTTOM, X, Y, BOTH, HORIZONTAL, VERTICAL
from tkinter import ttk, messagebox, simpledialog
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import sys
import os

class Ventas(tk.Frame):
    db_name = "database.db"

    def __init__(self, padre):
        super().__init__(padre)
        self.numero_factura = self.obtener_numero_factura_actual()
        self.productos_seleccionados = []
        self.widgets()
        self.cargar_productos()
        self.cargar_clientes()
        self.timer_producto = None
        self.timer_cliente = None

    def obtener_numero_factura_actual(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT MAX(factura) FROM ventas")
            last_invoice_number = c.fetchone()[0]
            conn.close()
            return last_invoice_number + 1 if last_invoice_number is not None else 1
        except sqlite3.Error as e:
            print("Error obteniendo el número de factura:", e)
            return 1

    def cargar_clientes(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT nombre FROM clientes")
            clientes_data = c.fetchall()
            self.clientes = [cliente[0] for cliente in clientes_data]
            self.entry_cliente["values"] = self.clientes
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando clientes:", e)
            self.clientes = []

    def filtrar_clientes(self, event):
        if self.timer_cliente:
            self.timer_cliente.cancel()
        self.timer_cliente = threading.Timer(0.5, self._filter_clientes)
        self.timer_cliente.start()

    def _filter_clientes(self):
        typed = self.entry_cliente.get()

        if typed == '':
            data = self.clientes
        else:
            data = [item for item in self.clientes if typed.lower() in item.lower()]

        if data:
            self.entry_cliente['values'] = data
            self.entry_cliente.event_generate('<Down>')
        else:
            self.entry_cliente['values'] = ['No se encontraron resultados']
            self.entry_cliente.event_generate('<Down>')

    def cargar_productos(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT articulo FROM articulos")
            productos_data = c.fetchall()
            self.products = [producto[0] for producto in productos_data]
            self.entry_producto["values"] = self.products
            conn.close()
        except sqlite3.Error as e:
            print("Error cargando productos:", e)
            self.products = []

    def filtrar_productos(self, event):
        if self.timer_producto:
            self.timer_producto.cancel()
        self.timer_producto = threading.Timer(0.5, self._filter_products)
        self.timer_producto.start()

    def _filter_products(self):
        typed = self.entry_producto.get()

        if typed == '':
            data = self.products
        else:
            data = [item for item in self.products if typed.lower() in item.lower()]

        if data:
            self.entry_producto['values'] = data
            self.entry_producto.event_generate('<Down>')
        else:
            self.entry_producto['values'] = ['No se encontraron resultados']
            self.entry_producto.event_generate('<Down>')

    def agregar_articulo(self):
        cliente = self.entry_cliente.get()
        producto = self.entry_producto.get()
        cantidad = self.entry_cantidad.get()

        if not cliente:
            messagebox.showerror("Error", "Por favor seleccione un cliente.")
            return
        if not producto:
            messagebox.showerror("Error", "Por favor seleccione un producto.")
            return
        if not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", "Por favor ingrese una cantidad válida.")
            return

        cantidad = int(cantidad)

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (producto,))
            resultado = c.fetchone()
            conn.close()

            if resultado is None:
                messagebox.showerror("Error", "Producto no encontrado.")
                return

            precio, costo, stock = resultado

            if cantidad > stock:
                messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                return

            total = precio * cantidad
            total_cop = "{:,.0f}".format(total)

            self.tre.insert("", "end", values=(self.numero_factura, cliente, producto, "{:,.0f}".format(precio), cantidad, total_cop))
            self.productos_seleccionados.append((self.numero_factura, cliente, producto, precio, cantidad, total_cop, costo))

            self.entry_producto.set('')
            self.entry_cantidad.delete(0, 'end')

            self.calcular_precio_total()

        except sqlite3.Error as e:
            print("Error al agregar artículo:", e)

    def calcular_precio_total(self):
        total_pagar = 0
        for item in self.tre.get_children():
            valores = self.tre.item(item)["values"]
            if valores:
                total_item = float(str(valores[5]).replace(",", ""))
                total_pagar += total_item

        total_pagar_cop = "{:,.0f}".format(total_pagar)
        self.label_precio_total.config(text=f"Precio a pagar: $ {total_pagar_cop}")

    def actualizar_stock(self, event=None):
        producto_seleccionado = self.entry_producto.get()
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT stock FROM articulos WHERE articulo=?", (producto_seleccionado,))
            stock = c.fetchone()
            conn.close()

            if stock:
                self.label_stock.config(text=f"Stock: {stock[0]}")
            else:
                self.label_stock.config(text="Stock: -")
        except sqlite3.Error as e:
            print("Error al obtener el stock:", e)

    def realizar_pago(self):
        if not self.tre.get_children():
            messagebox.showerror("Error", "No hay productos para realizar el pago.")
            return

        total_venta = sum(float(item[5].replace(",", "")) for item in self.productos_seleccionados)

        ventana_pago = tk.Toplevel(self)
        ventana_pago.title("Realizar Pago")
        ventana_pago.geometry("400x400+450+80")
        ventana_pago.config(bg="#C0D9E7")
        ventana_pago.resizable(False, False)
        ventana_pago.transient(self.master)
        ventana_pago.grab_set()

        tk.Label(ventana_pago, text="Realizar Pago", font="sans 30 bold", bg="#C0D9E7").place(x=70, y=10)
        tk.Label(ventana_pago, text=f"Total a pagar: {total_venta:,.2f}", font="sans 14 bold", bg="#C0D9E7").place(x=80, y=100)
        tk.Label(ventana_pago, text="Ingrese el monto pagado:", font="sans 14 bold", bg="#C0D9E7").place(x=80, y=160)

        entry_monto = ttk.Entry(ventana_pago, font="sans 14 bold")
        entry_monto.place(x=80, y=210, width=240, height=40)

        def confirmar_pago():
            self.procesar_pago(entry_monto.get(), ventana_pago, total_venta)

        tk.Button(ventana_pago, text="Confirmar pago", font="sans 14 bold", command=confirmar_pago).place(x=80, y=270, width=240, height=40)

    def procesar_pago(self, cantidad_pagada, ventana_pago, total_venta):
        try:
            cantidad_pagada = float(cantidad_pagada)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido.")
            return

        if cantidad_pagada < total_venta:
            messagebox.showerror("Error", "La cantidad pagada es insuficiente.")
            return

        cambio = cantidad_pagada - total_venta
        
        # Cerramos la ventana de pago
        ventana_pago.destroy()
        
        # Crear la ventana de confirmación de pago con mayor tamaño
        ventana_confirmacion = tk.Toplevel(self)
        ventana_confirmacion.title("Pago realizado")
        ventana_confirmacion.geometry("500x400+400+80")
        ventana_confirmacion.config(bg="#E0F0FF")
        ventana_confirmacion.resizable(False, False)
        ventana_confirmacion.transient(self.master)
        ventana_confirmacion.grab_set()
        
        # Icono de información
        icono_frame = tk.Frame(ventana_confirmacion, bg="#E0F0FF", width=80, height=80)
        icono_frame.place(x=210, y=20)
        
        # Dibujar un círculo azul con "i" para el icono de información
        canvas = tk.Canvas(icono_frame, width=80, height=80, bg="#E0F0FF", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 75, 75, fill="#0078D7", outline="")
        canvas.create_text(40, 40, text="i", fill="white", font=("Arial", 36, "bold"))
        
        # Título
        tk.Label(ventana_confirmacion, text="Pago realizado", font=("Arial", 22, "bold"), bg="#E0F0FF").place(x=150, y=110)
        
        # Marco para la información del pago
        info_frame = tk.Frame(ventana_confirmacion, bg="white", bd=1, relief=tk.SOLID)
        info_frame.place(x=75, y=160, width=350, height=140)
        
        # Información del pago con mejor formato
        tk.Label(info_frame, text=f"Total:", font=("Arial", 16), bg="white", anchor="w").place(x=30, y=20, width=150)
        tk.Label(info_frame, text=f"${total_venta:,.0f}", font=("Arial", 16, "bold"), bg="white", anchor="e").place(x=170, y=20, width=150)
        
        tk.Label(info_frame, text=f"Pagado:", font=("Arial", 16), bg="white", anchor="w").place(x=30, y=60, width=150)
        tk.Label(info_frame, text=f"${cantidad_pagada:,.0f}", font=("Arial", 16, "bold"), bg="white", anchor="e").place(x=170, y=60, width=150)
        
        # Línea divisoria
        canvas_line = tk.Canvas(info_frame, width=300, height=2, bg="white", highlightthickness=0)
        canvas_line.place(x=25, y=95)
        canvas_line.create_line(0, 1, 300, 1, fill="#CCCCCC", width=2)
        
        tk.Label(info_frame, text=f"Cambio:", font=("Arial", 16), bg="white", anchor="w").place(x=30, y=100, width=150)
        tk.Label(info_frame, text=f"${cambio:,.0f}", font=("Arial", 16, "bold"), bg="white", anchor="e").place(x=170, y=100, width=150)
        
        # Botón Aceptar
        btn_aceptar = tk.Button(ventana_confirmacion, text="Aceptar", font=("Arial", 14), 
                               bg="#0078D7", fg="white",
                               command=ventana_confirmacion.destroy)
        btn_aceptar.place(x=200, y=320, width=100, height=40)

        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            fecha = datetime.datetime.now().strftime("%Y-%m-%d")
            hora = datetime.datetime.now().strftime("%H:%M:%S")

            for item in self.productos_seleccionados:
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.execute("""
                    INSERT INTO ventas (factura, cliente, articulo, precio, cantidad, total, costo, fecha, hora)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                          (factura, cliente, producto, precio, cantidad, float(total.replace(",", "")), costo * cantidad, fecha, hora))
                c.execute("UPDATE articulos SET stock = stock - ? WHERE articulo=?", (cantidad, producto))

            conn.commit()
            conn.close()

            self.generar_factura_pdf(total_venta, cliente)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al registrar la venta: {e}")

        self.numero_factura += 1
        self.label_numero_factura.config(text=str(self.numero_factura))

        self.productos_seleccionados.clear()
        self.limpiar_campos()

    def limpiar_campos(self):
        for item in self.tre.get_children():
            self.tre.delete(item)
        self.label_precio_total.config(text="Precio a pagar: $ 0")
        self.entry_producto.set('')
        self.entry_cantidad.delete(0, 'end')

    def limpiar_lista(self):
        self.tre.delete(*self.tre.get_children())
        self.productos_seleccionados.clear()
        self.calcular_precio_total()

    def eliminar_articulo(self):
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un artículo para eliminar.")
            return

        item_id = selected_item[0]
        valores = self.tre.item(item_id)["values"]
        articulo = valores[2]

        self.tre.delete(item_id)
        self.productos_seleccionados = [prod for prod in self.productos_seleccionados if prod[2] != articulo]
        self.calcular_precio_total()

    def editar_articulo(self):
        selected_item = self.tre.selection()
        if not selected_item:
            messagebox.showerror("Error", "Seleccione un artículo para editar.")
            return

        item_values = self.tre.item(selected_item[0], "values")
        current_producto = item_values[2]
        current_cantidad = int(item_values[4])

        new_cantidad = simpledialog.askinteger("Editar artículo", "Ingrese la nueva cantidad:", initialvalue=current_cantidad)

        if new_cantidad is not None:
            try:
                conn = sqlite3.connect(self.db_name)
                c = conn.cursor()
                c.execute("SELECT precio, costo, stock FROM articulos WHERE articulo=?", (current_producto,))
                resultado = c.fetchone()
                conn.close()

                if not resultado:
                    messagebox.showerror("Error", "Producto no encontrado.")
                    return

                precio, costo, stock = resultado

                if new_cantidad > stock:
                    messagebox.showerror("Error", f"Stock insuficiente. Solo hay {stock} unidades disponibles.")
                    return

                total = precio * new_cantidad
                total_cop = "{:,.0f}".format(total)

                self.tre.item(selected_item[0], values=(self.numero_factura, self.entry_cliente.get(), current_producto, "{:,.0f}".format(precio), new_cantidad, total_cop))

                for idx, producto in enumerate(self.productos_seleccionados):
                    if producto[2] == current_producto:
                        self.productos_seleccionados[idx] = (self.numero_factura, self.entry_cliente.get(), current_producto, precio, new_cantidad, total_cop, costo)
                        break

                self.calcular_precio_total()

            except sqlite3.Error as e:
                print("Error al editar artículo:", e)

    def ver_ventas_realizadas(self):
        try:
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute("SELECT factura, cliente, articulo, precio, cantidad, total, fecha, hora FROM ventas ORDER BY factura DESC")
            ventas = c.fetchall()
            conn.close()

            ventana_ventas = tk.Toplevel(self)
            ventana_ventas.title("Ventas realizadas")
            ventana_ventas.geometry("1100x650+120+20")
            ventana_ventas.configure(bg="#C6D9E3")
            ventana_ventas.resizable(False, False)
            ventana_ventas.transient(self.master)
            ventana_ventas.grab_set()
            ventana_ventas.focus_set()
            ventana_ventas.lift()

            def filtrar_ventas():
                factura_a_buscar = entry_factura.get()
                cliente_a_buscar = entry_cliente.get()
                for item in tree.get_children():
                    tree.delete(item)

                ventas_filtradas = [
                    venta for venta in ventas
                    if (str(venta[0]) == factura_a_buscar or not factura_a_buscar) and
                    (cliente_a_buscar.lower() in venta[1].lower() or not cliente_a_buscar)
                ]

                for venta in ventas_filtradas:
                    venta_formateada = list(venta)
                    venta_formateada[3] = "{:,.0f}".format(float(venta[3]))
                    venta_formateada[5] = "{:,.0f}".format(float(venta[5]))
                    tree.insert("", "end", values=venta_formateada)

            label_ventas_realizadas = tk.Label(ventana_ventas, text="Ventas realizadas", font="sans 26 bold", bg="#C6D9E3")
            label_ventas_realizadas.place(x=350, y=20)

            filtro_frame = tk.Frame(ventana_ventas, bg="#C6D9E3")
            filtro_frame.place(x=20, y=60, width=1060, height=60)

            # Cambio aquí: Mover "Numero de factura" a la izquierda y "Cliente" a la derecha de su respectiva entrada
            label_factura = tk.Label(filtro_frame, text="Numero de factura", bg="#C6D9E3", font="sans 14 bold")
            label_factura.place(x=10, y=15)
        
            entry_factura = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_factura.place(x=200, y=10, width=200, height=40)

            # CAMBIO AQUÍ: Mover el label "Cliente" junto al recuadro de entrada del cliente (a la derecha)
            entry_cliente = ttk.Entry(filtro_frame, font="sans 14 bold")
            entry_cliente.place(x=620, y=10, width=200, height=40)
            
            label_cliente = tk.Label(filtro_frame, text="Cliente", bg="#C6D9E3", font="sans 14 bold")
            label_cliente.place(x=550, y=15)

            btn_filtrar = tk.Button(filtro_frame, text="Filtrar", font="sans 14 bold", command=filtrar_ventas)
            btn_filtrar.place(x=840, y=10)

            tree_frame = tk.Frame(ventana_ventas, bg="white")
            tree_frame.place(x=20, y=130, width=1060, height=500)

            scrol_y = ttk.Scrollbar(tree_frame)
            scrol_y.pack(side=RIGHT, fill=Y)

            scrol_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL)
            scrol_x.pack(side=BOTTOM, fill=X)

            tree = ttk.Treeview(tree_frame, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total", "Fecha", "Hora"), show="headings")
            tree.pack(expand=True, fill=BOTH)

            scrol_y.config(command=tree.yview)
            scrol_x.config(command=tree.xview)

            tree.heading("Factura", text="Factura")
            tree.heading("Cliente", text="Cliente")
            tree.heading("Producto", text="Producto")
            tree.heading("Precio", text="Precio")
            tree.heading("Cantidad", text="Cantidad")
            tree.heading("Total", text="Total")
            tree.heading("Fecha", text="Fecha")
            tree.heading("Hora", text="Hora")

            tree.column("Factura", width=60, anchor="center")
            tree.column("Cliente", width=120, anchor="center")
            tree.column("Producto", width=120, anchor="center")
            tree.column("Precio", width=80, anchor="center")
            tree.column("Cantidad", width=80, anchor="center")
            tree.column("Total", width=80, anchor="center")
            tree.column("Fecha", width=80, anchor="center")
            tree.column("Hora", width=80, anchor="center")

            for venta in ventas:
                venta_formateada = list(venta)
                venta_formateada[3] = "{:,.0f}".format(float(venta[3]))
                venta_formateada[5] = "{:,.0f}".format(float(venta[5]))
                tree.insert("", "end", values=venta_formateada)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al obtener las ventas: {e}")

    def generar_factura_pdf(self, total_venta, cliente):
        try:
            # Crear directorio si no existe
            if not os.path.exists("facturas"):
                os.makedirs("facturas")
                
            factura_path = f"facturas/Factura_{self.numero_factura}.pdf"
            c = canvas.Canvas(factura_path, pagesize=letter)

            empresa_nombre = "Mini Market Version 1.0"
            empresa_direccion = "Calle 1 # 1a - 01, Neiva - Huila"
            empresa_telefono = "+57 123456789"
            empresa_email = "info@marketsystem.com"
            empresa_webside = "www.marketsystem.com"

            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(colors.darkblue)
            c.drawCentredString(300, 750, "FACTURA DE SERVICIOS")

            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, 710, f"{empresa_nombre}")
            c.setFont("Helvetica", 12)
            c.drawString(50, 690, f"Dirección: {empresa_direccion}")
            c.drawString(50, 670, f"Telefono: {empresa_telefono}")
            c.drawString(50, 650, f"Email: {empresa_email}")
            c.drawString(50, 630, f"Webside: {empresa_webside}")

            c.setLineWidth(0.5)
            c.setStrokeColor(colors.gray)
            c.line(50, 620, 550, 620)

            c.setFont("Helvetica", 12)
            c.drawString(50, 600, f"Número de factura: {self.numero_factura}")
            c.drawString(50, 580, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.line(50, 560, 550, 560)

            c.drawString(50, 540, f"Cliente: {cliente}")
            c.drawString(50, 520, "Descripción de productos:")

            y_offset = 500
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y_offset, "Producto")
            c.drawString(270, y_offset, "Cantidad")
            c.drawString(370, y_offset, "Precio")
            c.drawString(470, y_offset, "Total")

            c.line(50, y_offset - 10, 550, y_offset - 10)
            y_offset -= 30
            c.setFont("Helvetica", 12)
            for item in self.productos_seleccionados: 
                factura, cliente, producto, precio, cantidad, total, costo = item
                c.drawString(70, y_offset, producto)
                c.drawString(270, y_offset, str(cantidad))
                c.drawString(370, y_offset, "${:,.0f}".format(precio))
                c.drawString(470, y_offset, total)
                y_offset -= 20

            c.line(50, y_offset, 550, y_offset)
            y_offset -= 20
            
            c.setFont("Helvetica-Bold", 14)
            c.setFillColor(colors.darkblue)
            c.drawString(50, y_offset, f"Total a Pagar: $ {total_venta:,.0f}")
            c.setFillColor(colors.darkblue)
            c.setFont("Helvetica", 12)

            y_offset -= 20
            c.line(50, y_offset, 550, y_offset)

            c.setFont("Helvetica-Bold", 16)
            c.drawString(150, y_offset - 60, "Gracias por tu compra, vuelve pronto!")

            y_offset -= 100
            c.setFont("Helvetica", 10)
            c.drawString(50, y_offset, "Términos y Condiciones:")
            c.drawString(50, y_offset - 20, "1. Los productos comprados no tienen devolución.")
            c.drawString(50, y_offset - 40, "2. Conserve esta factura como comprobante de su compra.")
            c.drawString(50, y_offset - 60, "3. Para más información, visite nuestro sitio web o contacte a servicio al cliente")

            c.save()

            messagebox.showinfo("Factura generada", f"Se ha generado la factura en: {factura_path}")

            # Abrir el archivo PDF
            if sys.platform == 'win32':
                os.startfile(os.path.abspath(factura_path))
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.call(['open', factura_path])
            else:  # Linux
                import subprocess
                subprocess.call(['xdg-open', factura_path])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura: {e}")

    def widgets(self):
        label = tk.Label(self, text="Ventas")
        label.pack()

        labelframe = tk.LabelFrame(self, font="sans 12 bold", bg="#C6D9E3")
        labelframe.place(x=25, y=30, width=1045, height=180)

        tk.Label(labelframe, text="Cliente:", font="sans 14 bold", bg="#C6D9E3").place(x=10, y=11)
        self.entry_cliente = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_cliente.place(x=120, y=8, width=260, height=40)
        self.entry_cliente.bind('<KeyRelease>', self.filtrar_clientes)

        tk.Label(labelframe, text="Producto:", font="sans 14 bold", bg="#C6D9E3").place(x=10, y=70)
        self.entry_producto = ttk.Combobox(labelframe, font="sans 14 bold")
        self.entry_producto.place(x=120, y=60, width=260, height=40)
        self.entry_producto.bind('<KeyRelease>', self.filtrar_productos)
        self.entry_producto.bind('<<ComboboxSelected>>', self.actualizar_stock)

        tk.Label(labelframe, text="Cantidad:", font="sans 14 bold", bg="#C6D9E3").place(x=500, y=11)
        self.entry_cantidad = ttk.Entry(labelframe, font="sans 14 bold")
        self.entry_cantidad.place(x=610, y=8, width=100, height=40)

        self.label_stock = tk.Label(labelframe, text="Stock: ", font="sans 14 bold", bg="#C6D9E3")
        self.label_stock.place(x=500, y=70)

        tk.Label(labelframe, text="N° Factura:", font="sans 14 bold", bg="#C6D9E3").place(x=750, y=11)
        self.label_numero_factura = tk.Label(labelframe, text=str(self.numero_factura), font="sans 14 bold", bg="#C6D9E3")
        self.label_numero_factura.place(x=950, y=11)

        tk.Button(labelframe, text="Agregar Artículo", font="sans 14 bold", command=self.agregar_articulo).place(x=90, y=120, width=200, height=40)
        tk.Button(labelframe, text="Eliminar Artículo", font="sans 14 bold", command=self.eliminar_articulo).place(x=310, y=120, width=200, height=40)
        tk.Button(labelframe, text="Editar Artículo", font="sans 14 bold", command=self.editar_articulo).place(x=530, y=120, width=200, height=40)
        tk.Button(labelframe, text="Limpiar Lista", font="sans 14 bold", command=self.limpiar_lista).place(x=750, y=120, width=200, height=40)

        treFrame = tk.Frame(self, bg="white")
        treFrame.place(x=70, y=220, width=980, height=300)

        scrol_y = ttk.Scrollbar(treFrame)
        scrol_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrol_x = ttk.Scrollbar(treFrame, orient=tk.HORIZONTAL)
        scrol_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tre = ttk.Treeview(treFrame, yscrollcommand=scrol_y.set, xscrollcommand=scrol_x.set, columns=("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"), show="headings")
        self.tre.pack(expand=True, fill=tk.BOTH)

        scrol_y.config(command=self.tre.yview)
        scrol_x.config(command=self.tre.xview)

        for col in ("Factura", "Cliente", "Producto", "Precio", "Cantidad", "Total"):
            self.tre.heading(col, text=col)
            self.tre.column(col, anchor="center")

        self.label_precio_total = tk.Label(self, text="Precio a pagar: $ 0", font="sans 18 bold", bg="#C6D9E3")
        self.label_precio_total.place(x=680, y=550)

        tk.Button(self, text="Pagar", font="sans 14 bold", command=self.realizar_pago).place(x=70, y=550, width=200, height=40)

        tk.Button(self, text="Ver Ventas Realizadas", font="sans 14 bold", command=self.ver_ventas_realizadas).place(x=300, y=550, width=250, height=40)
