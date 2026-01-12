# PMD PAGOS - Product Requirements Document

## Descripción del Producto
Aplicación web para gestionar pagos de empleados y contratistas en un negocio de construcción.

## Stack Tecnológico
- **Frontend:** React + TailwindCSS + Shadcn/UI
- **Backend:** FastAPI (Python)
- **Base de datos:** MongoDB

## Características Implementadas

### Gestión de Empleados ✅
- CRUD completo de empleados
- Campos: nombre, salario diario, obra asignada, rubro
- Rubros disponibles: Albañilería, Steel Framing, Pintura, Plomería, Electricidad
- Tabla con columnas: Nombre, Obra, Rubro, Salario Diario, Estado, Acciones

### Gestión de Contratistas ✅
- CRUD completo de contratistas
- Campos: nombre, obra/proyecto, presupuesto total, pago semanal
- Barras de progreso mostrando % de presupuesto consumido
- Alertas cuando el presupuesto supera el 80%

### Gestión de Obras (Proyectos) ✅
- CRUD de proyectos/obras
- Asignación de empleados a obras específicas

### Control de Asistencia ✅
- Registro de asistencia semanal
- Estados: Presente, Ausente, Tarde
- Registro de horas de tardanza con descuento automático

### Gestión de Adelantos ✅
- Registro de adelantos con fecha y descripción
- Descuento automático del salario semanal

### Resumen de Pagos ✅
- Cálculo automático de salarios semanales
- Resumen total a pagar el viernes
- Desglose por empleados y contratistas

### Impresión de Recibos ✅
- Recibos de empleados con detalle de adelantos
- Recibos de contratistas con certificación semanal
- Botón para imprimir todos los recibos
- Formato A4 (5 recibos por página)

### UI/UX ✅
- Nombre: "PMD PAGOS"
- Tema en gama de azules
- Diseño responsivo (mobile-friendly)
- Menú hamburguesa en móvil

## Bugs Corregidos (12/01/2026)

### Bug 1: Modal de edición de empleados ✅
- **Problema:** No incluía campos de Obra y Rubro
- **Solución:** Se agregaron los campos Select para Obra y Rubro en el modal de edición

### Bug 2: Impresión de recibos de contratistas ✅
- **Problema:** No existían botones para imprimir recibos de contratistas
- **Solución:** Se agregaron 3 botones: "Recibos Empleados", "Recibos Contratistas", "Todos los Recibos"

### Bug 3: Overlay en página de asistencia ✅
- **Problema:** Reportado overlay que impedía clicks
- **Verificación:** No se reproduce, la página funciona correctamente

## Próximas Tareas Pendientes

### P0 - Alta Prioridad
- [ ] Implementar certificaciones semanales editables para contratistas (el contratista no cobra siempre lo mismo)

### P1 - Media Prioridad
- [ ] Exportar a Excel/PDF
- [ ] Reportes financieros avanzados

### P2 - Baja Prioridad
- [ ] Roles de usuario (admin, contador, etc.)
- [ ] Fotos de avance de obra
- [ ] Historial de cambios

## Estructura del Proyecto

```
/app/
├── backend/
│   ├── .env
│   ├── requirements.txt
│   └── server.py
└── frontend/
    ├── .env
    ├── package.json
    └── src/
        ├── App.js (componentes principales)
        ├── App.css
        ├── index.css
        └── components/
            ├── Projects.js
            └── PrintableReceipts.js
```

## Endpoints API

- `GET/POST /api/employees` - Gestión de empleados
- `PUT/DELETE /api/employees/{id}` - Actualizar/Eliminar empleado
- `GET/POST /api/contractors` - Gestión de contratistas
- `GET/POST /api/projects` - Gestión de obras
- `GET/POST /api/attendance` - Control de asistencia
- `GET /api/attendance/week/{week_start}` - Asistencia semanal
- `GET/POST /api/advances` - Gestión de adelantos
- `GET /api/dashboard/stats` - Estadísticas del dashboard
- `POST /api/payments/calculate` - Calcular pagos
- `GET /api/payments/by-project/{week_start}` - Pagos por obra
