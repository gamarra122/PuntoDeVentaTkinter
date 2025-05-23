-- Creación de la base de datos
CREATE DATABASE GestionComercial;
GO

USE GestionComercial;
GO

-- Tabla de Vendedores
CREATE TABLE Vendedores (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(20) UNIQUE NOT NULL,
    Nombre VARCHAR(100) NOT NULL,
    Usuario VARCHAR(50) UNIQUE NOT NULL,
    Clave VARCHAR(100) NOT NULL,
    Activo BIT DEFAULT 1
);

-- Tabla de Clientes
CREATE TABLE Clientes (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(20) UNIQUE NOT NULL,
    RazonSocial VARCHAR(100) NOT NULL,
    CUIT VARCHAR(20) UNIQUE,
    Condicion VARCHAR(50), -- CONSUMIDOR FINAL, RESPONSABLE INSCRIPTO, etc.
    Direccion VARCHAR(200),
    Telefono VARCHAR(50),
    Email VARCHAR(100),
    Activo BIT DEFAULT 1
);

-- Tabla de Categorías de Artículos
CREATE TABLE CategoriasArticulos (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(200)
);

-- Tabla de Artículos
CREATE TABLE Articulos (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(20) UNIQUE NOT NULL,
    CodigoBarras VARCHAR(50),
    Descripcion VARCHAR(200) NOT NULL,
    CategoriaID INT REFERENCES CategoriasArticulos(ID),
    PrecioCompra DECIMAL(18,2) DEFAULT 0,
    PrecioVenta DECIMAL(18,2) DEFAULT 0,
    IVA DECIMAL(5,2) DEFAULT 21.00,
    Stock DECIMAL(18,2) DEFAULT 0,
    StockMinimo DECIMAL(18,2) DEFAULT 0,
    Activo BIT DEFAULT 1
);

-- Tabla de Tipos de Comprobantes
CREATE TABLE TiposComprobantes (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(10) NOT NULL,
    Descripcion VARCHAR(50) NOT NULL,
    Activo BIT DEFAULT 1
);

-- Tabla de Formas de Pago
CREATE TABLE FormasPago (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Codigo VARCHAR(10) NOT NULL,
    Descripcion VARCHAR(50) NOT NULL,
    PorcentajeRecargo DECIMAL(5,2) DEFAULT 0,
    Activo BIT DEFAULT 1
);

-- Tabla de Ventas (Cabecera)
CREATE TABLE Ventas (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Numero INT NOT NULL,
    Fecha DATETIME DEFAULT GETDATE(),
    FechaVencimiento DATETIME,
    VendedorID INT REFERENCES Vendedores(ID),
    ClienteID INT REFERENCES Clientes(ID),
    TipoComprobanteID INT REFERENCES TiposComprobantes(ID),
    FormaPagoID INT REFERENCES FormasPago(ID),
    Observaciones VARCHAR(500),
    Subtotal DECIMAL(18,2) DEFAULT 0,
    DescuentoPorcentaje DECIMAL(5,2) DEFAULT 0,
    DescuentoMonto DECIMAL(18,2) DEFAULT 0,
    Neto DECIMAL(18,2) DEFAULT 0,
    Exento DECIMAL(18,2) DEFAULT 0,
    IVA DECIMAL(18,2) DEFAULT 0,
    Total DECIMAL(18,2) DEFAULT 0,
    Anulada BIT DEFAULT 0
);

-- Tabla de Ventas (Detalle)
CREATE TABLE VentasDetalle (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    VentaID INT REFERENCES Ventas(ID) ON DELETE CASCADE,
    ArticuloID INT REFERENCES Articulos(ID),
    Cantidad DECIMAL(18,2) NOT NULL,
    PrecioUnitario DECIMAL(18,2) NOT NULL,
    DescuentoPorcentaje DECIMAL(5,2) DEFAULT 0,
    Subtotal DECIMAL(18,2) NOT NULL,
    IVA DECIMAL(5,2) DEFAULT 21.00,
    Total DECIMAL(18,2) NOT NULL,
    Observacion VARCHAR(200)
);

-- Datos iniciales
INSERT INTO TiposComprobantes (Codigo, Descripcion) VALUES 
('FA', 'FACTURA A'),
('FB', 'FACTURA B'),
('FC', 'FACTURA C'),
('ND', 'NOTA DE DÉBITO'),
('NC', 'NOTA DE CRÉDITO');

INSERT INTO FormasPago (Codigo, Descripcion, PorcentajeRecargo) VALUES
('EFE', 'Efectivo', 0),
('DEB', 'Débito', 0),
('CRE', 'Crédito', 10.00),
('TRA', 'Transferencia', 0),
('CC', 'Cuenta Corriente', 15.00),
('REM', 'Remito', 0);

-- Insertar un vendedor admin
INSERT INTO Vendedores (Codigo, Nombre, Usuario, Clave) VALUES
('ADM', 'ADMIN HS', 'admin', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855');

-- Insertar cliente consumidor final
INSERT INTO Clientes (Codigo, RazonSocial, CUIT, Condicion) VALUES
('CF', 'CONSUMIDOR FINAL', '11111111111', 'CONSUMIDOR FINAL');