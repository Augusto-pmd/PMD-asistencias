import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { Users, Calendar, DollarSign, History, LayoutDashboard, Plus, Edit2, Trash2, Check, X, Clock, Briefcase, Menu, XIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function getWeekDates(weekStart) {
  const dates = [];
  const start = new Date(weekStart);
  for (let i = 0; i < 7; i++) {
    const date = new Date(start);
    date.setDate(start.getDate() + i);
    dates.push(date.toISOString().split('T')[0]);
  }
  return dates;
}

function getCurrentWeekStart() {
  const today = new Date();
  const day = today.getDay();
  const diff = today.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(today.setDate(diff));
  return monday.toISOString().split('T')[0];
}

function formatCurrency(amount) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount);
}

const ProgressBar = ({ percentage, showLabel = true }) => {
  const getColor = () => {
    if (percentage >= 95) return 'bg-rose-500';
    if (percentage >= 80) return 'bg-orange-500';
    if (percentage >= 60) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const getBackgroundColor = () => {
    if (percentage >= 95) return 'bg-rose-100';
    if (percentage >= 80) return 'bg-orange-100';
    if (percentage >= 60) return 'bg-amber-100';
    return 'bg-emerald-100';
  };

  return (
    <div className="w-full">
      <div className={`w-full h-2 ${getBackgroundColor()} rounded-full overflow-hidden`}>
        <div 
          className={`h-full ${getColor()} transition-all duration-300`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-slate-500 mt-1">{percentage.toFixed(1)}%</p>
      )}
    </div>
  );
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [contractors, setContractors] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchContractors();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching stats:', error);
      toast.error('Error al cargar estadísticas');
      setLoading(false);
    }
  };

  const fetchContractors = async () => {
    try {
      const response = await axios.get(`${API}/contractors`);
      setContractors(response.data);
    } catch (error) {
      console.error('Error fetching contractors:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-slate-500">Cargando...</div>
      </div>
    );
  }

  const contractorsNearBudget = contractors.filter(c => {
    const percentage = c.budget > 0 ? (c.total_paid / c.budget) * 100 : 0;
    return percentage >= 80 && c.is_active;
  });

  return (
    <div className="space-y-4 sm:space-y-6" data-testid="dashboard">
      <div>
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Dashboard</h1>
        <p className="text-sm sm:text-base text-slate-500">Resumen de la semana actual</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        <Card className="p-4 sm:p-6 stat-card bg-white border border-blue-200 rounded-xl shadow-sm" data-testid="stat-card-employees">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs sm:text-sm font-medium text-slate-500 mb-1">Empleados Activos</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">{stats?.active_employees || 0}</p>
              <p className="text-xs text-slate-400 mt-1">de {stats?.total_employees || 0} totales</p>
            </div>
            <div className="p-2 sm:p-3 bg-blue-50 rounded-lg">
              <Users className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-6 stat-card bg-white border border-blue-200 rounded-xl shadow-sm" data-testid="stat-card-contractors">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs sm:text-sm font-medium text-slate-500 mb-1">Contratistas Activos</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900">{stats?.active_contractors || 0}</p>
              <p className="text-xs text-slate-400 mt-1">de {stats?.total_contractors || 0} totales</p>
            </div>
            <div className="p-2 sm:p-3 bg-blue-100 rounded-lg">
              <Briefcase className="w-5 h-5 sm:w-6 sm:h-6 text-blue-700" />
            </div>
          </div>
        </Card>

        <Card className="p-4 sm:p-6 stat-card bg-white border border-blue-200 rounded-xl shadow-sm sm:col-span-2 lg:col-span-1" data-testid="stat-card-advances">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs sm:text-sm font-medium text-slate-500 mb-1">Adelantos</p>
              <p className="text-2xl sm:text-3xl font-bold text-slate-900 font-mono-numbers">
                {formatCurrency(stats?.total_advances_this_week || 0)}
              </p>
              <p className="text-xs text-slate-400 mt-1">descontados</p>
            </div>
            <div className="p-2 sm:p-3 bg-rose-50 rounded-lg">
              <DollarSign className="w-5 h-5 sm:w-6 sm:h-6 text-rose-600" />
            </div>
          </div>
        </Card>
      </div>

      <Card className="p-4 sm:p-6 bg-gradient-to-br from-blue-50 to-sky-50 border border-blue-200 rounded-xl shadow-sm">
        <div className="text-center">
          <p className="text-xs sm:text-sm font-medium text-blue-700 mb-2">Total a Pagar el Viernes</p>
          <p className="text-3xl sm:text-4xl lg:text-5xl font-bold text-blue-900 font-mono-numbers mb-4">
            {formatCurrency(stats?.total_to_pay_friday || 0)}
          </p>
          <div className="grid grid-cols-3 gap-2 sm:gap-4 mt-4 text-xs sm:text-sm">
            <div className="bg-white/70 rounded-lg p-2 sm:p-3">
              <p className="text-blue-600 mb-1">Empleados</p>
              <p className="font-bold text-slate-900 font-mono-numbers text-xs sm:text-sm">
                {formatCurrency(stats?.total_payment_this_week || 0)}
              </p>
            </div>
            <div className="bg-white/70 rounded-lg p-2 sm:p-3">
              <p className="text-blue-600 mb-1">Contratistas</p>
              <p className="font-bold text-slate-900 font-mono-numbers text-xs sm:text-sm">
                {formatCurrency(stats?.contractors_payment_this_week || 0)}
              </p>
            </div>
            <div className="bg-white/70 rounded-lg p-2 sm:p-3">
              <p className="text-blue-600 mb-1">Adelantos</p>
              <p className="font-bold text-rose-600 font-mono-numbers text-xs sm:text-sm">
                -{formatCurrency(stats?.total_advances_this_week || 0)}
              </p>
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-4 sm:p-6 bg-white border border-blue-200 rounded-xl shadow-sm">
        <h2 className="text-lg sm:text-xl font-bold text-slate-900 mb-4">Acciones Rápidas</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <Link to="/employees">
            <Button className="w-full btn-primary" data-testid="quick-action-employees">
              <Users className="w-4 h-4 mr-2" />
              Gestionar Empleados
            </Button>
          </Link>
          <Link to="/contractors">
            <Button className="w-full btn-primary" data-testid="quick-action-contractors">
              <Briefcase className="w-4 h-4 mr-2" />
              Gestionar Contratistas
            </Button>
          </Link>
          <Link to="/attendance">
            <Button className="w-full btn-primary" data-testid="quick-action-attendance">
              <Calendar className="w-4 h-4 mr-2" />
              Registrar Asistencia
            </Button>
          </Link>
          <Link to="/advances">
            <Button className="w-full btn-primary" data-testid="quick-action-advances">
              <DollarSign className="w-4 h-4 mr-2" />
              Gestionar Adelantos
            </Button>
          </Link>
        </div>
      </Card>
    </div>
  );
};

const EmployeeManagement = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [formData, setFormData] = useState({ name: '', daily_salary: '' });

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching employees:', error);
      toast.error('Error al cargar empleados');
      setLoading(false);
    }
  };

  const handleAddEmployee = async () => {
    if (!formData.name || !formData.daily_salary) {
      toast.error('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.post(`${API}/employees`, {
        name: formData.name,
        daily_salary: parseFloat(formData.daily_salary)
      });
      toast.success('Empleado agregado exitosamente');
      setIsAddModalOpen(false);
      setFormData({ name: '', daily_salary: '' });
      fetchEmployees();
    } catch (error) {
      console.error('Error adding employee:', error);
      toast.error('Error al agregar empleado');
    }
  };

  const handleEditEmployee = async () => {
    if (!formData.name || !formData.daily_salary) {
      toast.error('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.put(`${API}/employees/${selectedEmployee.id}`, {
        name: formData.name,
        daily_salary: parseFloat(formData.daily_salary)
      });
      toast.success('Empleado actualizado exitosamente');
      setIsEditModalOpen(false);
      setSelectedEmployee(null);
      setFormData({ name: '', daily_salary: '' });
      fetchEmployees();
    } catch (error) {
      console.error('Error updating employee:', error);
      toast.error('Error al actualizar empleado');
    }
  };

  const handleDeleteEmployee = async (id) => {
    if (!window.confirm('¿Estás seguro de eliminar este empleado?')) return;
    try {
      await axios.delete(`${API}/employees/${id}`);
      toast.success('Empleado eliminado exitosamente');
      await fetchEmployees();
    } catch (error) {
      console.error('Error deleting employee:', error);
      toast.error('Error al eliminar empleado');
    }
  };

  const openEditModal = (employee) => {
    setSelectedEmployee(employee);
    setFormData({ name: employee.name, daily_salary: employee.daily_salary });
    setIsEditModalOpen(true);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-6" data-testid="employee-management">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Empleados</h1>
          <p className="text-slate-500">Gestiona tu equipo de trabajo</p>
        </div>
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary" data-testid="add-employee-btn">
              <Plus className="w-4 h-4 mr-2" />
              Agregar Empleado
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="add-employee-dialog">
            <DialogHeader>
              <DialogTitle>Agregar Nuevo Empleado</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label htmlFor="name">Nombre Completo</Label>
                <Input
                  id="name"
                  data-testid="employee-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Juan Pérez"
                />
              </div>
              <div>
                <Label htmlFor="salary">Salario Diario</Label>
                <Input
                  id="salary"
                  data-testid="employee-salary-input"
                  type="number"
                  value={formData.daily_salary}
                  onChange={(e) => setFormData({ ...formData, daily_salary: e.target.value })}
                  placeholder="5000"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleAddEmployee} data-testid="submit-employee-btn">Agregar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Nombre</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Salario Diario</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Estado</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan="4" className="text-center py-12 text-slate-400">
                    No hay empleados registrados
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`employee-row-${employee.id}`}>
                    <td className="py-4 px-6 text-sm text-slate-700">{employee.name}</td>
                    <td className="py-4 px-6 text-sm text-slate-700 font-mono-numbers">
                      {formatCurrency(employee.daily_salary)}
                    </td>
                    <td className="py-4 px-6">
                      <Badge variant={employee.is_active ? "success" : "secondary"} data-testid={`employee-status-${employee.id}`}>
                        {employee.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => openEditModal(employee)} data-testid={`edit-employee-${employee.id}`}>
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteEmployee(employee.id)} data-testid={`delete-employee-${employee.id}`}>
                          <Trash2 className="w-4 h-4 text-rose-500" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent data-testid="edit-employee-dialog">
          <DialogHeader>
            <DialogTitle>Editar Empleado</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-name">Nombre Completo</Label>
              <Input
                id="edit-name"
                data-testid="edit-employee-name-input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-salary">Salario Diario</Label>
              <Input
                id="edit-salary"
                data-testid="edit-employee-salary-input"
                type="number"
                value={formData.daily_salary}
                onChange={(e) => setFormData({ ...formData, daily_salary: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleEditEmployee} data-testid="update-employee-btn">Actualizar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const ContractorManagement = () => {
  const [contractors, setContractors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedContractor, setSelectedContractor] = useState(null);
  const [formData, setFormData] = useState({ name: '', weekly_payment: '', project_name: '', budget: '' });

  useEffect(() => {
    fetchContractors();
  }, []);

  const fetchContractors = async () => {
    try {
      const response = await axios.get(`${API}/contractors`);
      setContractors(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching contractors:', error);
      toast.error('Error al cargar contratistas');
      setLoading(false);
    }
  };

  const handleAddContractor = async () => {
    if (!formData.name || !formData.weekly_payment || !formData.project_name || !formData.budget) {
      toast.error('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.post(`${API}/contractors`, {
        name: formData.name,
        weekly_payment: parseFloat(formData.weekly_payment),
        project_name: formData.project_name,
        budget: parseFloat(formData.budget)
      });
      toast.success('Contratista agregado exitosamente');
      setIsAddModalOpen(false);
      setFormData({ name: '', weekly_payment: '', project_name: '', budget: '' });
      await fetchContractors();
    } catch (error) {
      console.error('Error adding contractor:', error);
      toast.error('Error al agregar contratista');
    }
  };

  const handleEditContractor = async () => {
    if (!formData.name || !formData.weekly_payment || !formData.project_name || !formData.budget) {
      toast.error('Por favor completa todos los campos');
      return;
    }
    try {
      await axios.put(`${API}/contractors/${selectedContractor.id}`, {
        name: formData.name,
        weekly_payment: parseFloat(formData.weekly_payment),
        project_name: formData.project_name,
        budget: parseFloat(formData.budget)
      });
      toast.success('Contratista actualizado exitosamente');
      setIsEditModalOpen(false);
      setSelectedContractor(null);
      setFormData({ name: '', weekly_payment: '', project_name: '', budget: '' });
      await fetchContractors();
    } catch (error) {
      console.error('Error updating contractor:', error);
      toast.error('Error al actualizar contratista');
    }
  };

  const handleDeleteContractor = async (id) => {
    if (!window.confirm('¿Estás seguro de eliminar este contratista?')) return;
    try {
      await axios.delete(`${API}/contractors/${id}`);
      toast.success('Contratista eliminado exitosamente');
      await fetchContractors();
    } catch (error) {
      console.error('Error deleting contractor:', error);
      toast.error('Error al eliminar contratista');
    }
  };

  const openEditModal = (contractor) => {
    setSelectedContractor(contractor);
    setFormData({ 
      name: contractor.name, 
      weekly_payment: contractor.weekly_payment,
      project_name: contractor.project_name,
      budget: contractor.budget
    });
    setIsEditModalOpen(true);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-6" data-testid="contractor-management">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Contratistas</h1>
          <p className="text-slate-500">Gestiona los contratistas con presupuesto por obra</p>
        </div>
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary" data-testid="add-contractor-btn">
              <Plus className="w-4 h-4 mr-2" />
              Agregar Contratista
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="add-contractor-dialog">
            <DialogHeader>
              <DialogTitle>Agregar Nuevo Contratista</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label htmlFor="name">Nombre Completo</Label>
                <Input
                  id="name"
                  data-testid="contractor-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="María González"
                />
              </div>
              <div>
                <Label htmlFor="project_name">Obra / Proyecto</Label>
                <Input
                  id="project_name"
                  data-testid="contractor-project-input"
                  value={formData.project_name}
                  onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
                  placeholder="Casa Barrio Norte"
                />
              </div>
              <div>
                <Label htmlFor="budget">Presupuesto Total de la Obra</Label>
                <Input
                  id="budget"
                  data-testid="contractor-budget-input"
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                  placeholder="500000"
                />
              </div>
              <div>
                <Label htmlFor="weekly_payment">Pago Semanal</Label>
                <Input
                  id="weekly_payment"
                  data-testid="contractor-payment-input"
                  type="number"
                  value={formData.weekly_payment}
                  onChange={(e) => setFormData({ ...formData, weekly_payment: e.target.value })}
                  placeholder="15000"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleAddContractor} data-testid="submit-contractor-btn">Agregar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Nombre</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Obra</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Pago Semanal</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Presupuesto</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Pagado</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">% Consumido</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Saldo</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {contractors.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-12 text-slate-400">
                    No hay contratistas registrados
                  </td>
                </tr>
              ) : (
                contractors.map((contractor) => {
                  const percentageUsed = contractor.budget > 0 ? (contractor.total_paid / contractor.budget) * 100 : 0;
                  const isNearBudget = percentageUsed >= 80;
                  const isOverBudget = contractor.remaining_balance < 0;
                  
                  return (
                    <tr key={contractor.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`contractor-row-${contractor.id}`}>
                      <td className="py-4 px-6 text-sm text-slate-700 font-medium">{contractor.name}</td>
                      <td className="py-4 px-6 text-sm text-slate-600">{contractor.project_name}</td>
                      <td className="py-4 px-6 text-sm text-slate-700 text-right font-mono-numbers">
                        {formatCurrency(contractor.weekly_payment)}
                      </td>
                      <td className="py-4 px-6 text-sm text-slate-700 text-right font-mono-numbers">
                        {formatCurrency(contractor.budget)}
                      </td>
                      <td className="py-4 px-6 text-sm text-slate-700 text-right font-mono-numbers">
                        {formatCurrency(contractor.total_paid || 0)}
                      </td>
                      <td className="py-4 px-6">
                        <div className="min-w-[120px]">
                          <ProgressBar percentage={percentageUsed} />
                        </div>
                      </td>
                      <td className={`py-4 px-6 text-sm text-right font-bold font-mono-numbers ${
                        isOverBudget ? 'text-rose-600' : isNearBudget ? 'text-amber-600' : 'text-emerald-600'
                      }`}>
                        {formatCurrency(contractor.remaining_balance)}
                      </td>
                      <td className="py-4 px-6 text-right">
                        <div className="flex justify-end gap-2">
                          <Button variant="ghost" size="sm" onClick={() => openEditModal(contractor)} data-testid={`edit-contractor-${contractor.id}`}>
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDeleteContractor(contractor.id)} data-testid={`delete-contractor-${contractor.id}`}>
                            <Trash2 className="w-4 h-4 text-rose-500" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent data-testid="edit-contractor-dialog">
          <DialogHeader>
            <DialogTitle>Editar Contratista</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-name">Nombre Completo</Label>
              <Input
                id="edit-name"
                data-testid="edit-contractor-name-input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-project-name">Obra / Proyecto</Label>
              <Input
                id="edit-project-name"
                data-testid="edit-contractor-project-input"
                value={formData.project_name}
                onChange={(e) => setFormData({ ...formData, project_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-budget">Presupuesto Total de la Obra</Label>
              <Input
                id="edit-budget"
                data-testid="edit-contractor-budget-input"
                type="number"
                value={formData.budget}
                onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-weekly-payment">Pago Semanal</Label>
              <Input
                id="edit-weekly-payment"
                data-testid="edit-contractor-payment-input"
                type="number"
                value={formData.weekly_payment}
                onChange={(e) => setFormData({ ...formData, weekly_payment: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleEditContractor} data-testid="update-contractor-btn">Actualizar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const AttendanceSheet = () => {
  const [employees, setEmployees] = useState([]);
  const [weekStart, setWeekStart] = useState(getCurrentWeekStart());
  const [attendance, setAttendance] = useState({});
  const [loading, setLoading] = useState(true);
  const [showLateModal, setShowLateModal] = useState(false);
  const [selectedCell, setSelectedCell] = useState(null);
  const [lateHours, setLateHours] = useState('');

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    if (employees.length > 0) {
      fetchAttendance();
    }
  }, [weekStart, employees]);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data.filter(e => e.is_active));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching employees:', error);
      toast.error('Error al cargar empleados');
      setLoading(false);
    }
  };

  const fetchAttendance = async () => {
    try {
      const response = await axios.get(`${API}/attendance/week/${weekStart}`);
      const attendanceMap = {};
      response.data.forEach(record => {
        const key = `${record.employee_id}-${record.date}`;
        attendanceMap[key] = {
          status: record.status,
          late_hours: record.late_hours || 0
        };
      });
      setAttendance(attendanceMap);
    } catch (error) {
      console.error('Error fetching attendance:', error);
      toast.error('Error al cargar asistencia');
    }
  };

  const handleAttendanceClick = async (employeeId, date, currentStatus) => {
    const statuses = ['present', 'absent', 'late'];
    const currentIndex = statuses.indexOf(currentStatus);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];

    if (nextStatus === 'late') {
      setSelectedCell({ employeeId, date });
      setLateHours('');
      setShowLateModal(true);
    } else {
      await updateAttendance(employeeId, date, nextStatus, 0);
    }
  };

  const updateAttendance = async (employeeId, date, status, hours = 0) => {
    try {
      await axios.post(`${API}/attendance`, {
        employee_id: employeeId,
        date: date,
        status: status,
        late_hours: hours,
        week_start_date: weekStart
      });
      
      const key = `${employeeId}-${date}`;
      setAttendance({ 
        ...attendance, 
        [key]: { status: status, late_hours: hours }
      });
      toast.success('Asistencia actualizada');
    } catch (error) {
      console.error('Error updating attendance:', error);
      toast.error('Error al actualizar asistencia');
    }
  };

  const handleLateSubmit = async () => {
    if (!lateHours || parseFloat(lateHours) < 0) {
      toast.error('Por favor ingresa las horas de retraso');
      return;
    }
    
    await updateAttendance(
      selectedCell.employeeId, 
      selectedCell.date, 
      'late', 
      parseFloat(lateHours)
    );
    setShowLateModal(false);
    setSelectedCell(null);
    setLateHours('');
  };

  const weekDates = getWeekDates(weekStart);
  const dayNames = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-6" data-testid="attendance-sheet">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Asistencia</h1>
          <p className="text-slate-500">Registra la asistencia semanal</p>
        </div>
        <Input
          type="date"
          data-testid="week-start-input"
          value={weekStart}
          onChange={(e) => setWeekStart(e.target.value)}
          className="w-48"
        />
      </div>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider sticky left-0 bg-slate-50">Empleado</th>
                {weekDates.map((date, idx) => (
                  <th key={date} className="text-center py-4 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                    <div>{dayNames[idx]}</div>
                    <div className="text-slate-400 font-normal">{new Date(date).getDate()}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {employees.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-12 text-slate-400">
                    No hay empleados activos
                  </td>
                </tr>
              ) : (
                employees.map((employee) => (
                  <tr key={employee.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`attendance-row-${employee.id}`}>
                    <td className="py-3 px-6 text-sm text-slate-700 font-medium sticky left-0 bg-white">{employee.name}</td>
                    {weekDates.map((date) => {
                      const key = `${employee.id}-${date}`;
                      const record = attendance[key] || {};
                      const status = record.status || '';
                      const hours = record.late_hours || 0;
                      return (
                        <td key={date} className="py-1 px-1">
                          <div
                            className={`attendance-cell ${status ? `selected-${status}` : ''}`}
                            onClick={() => handleAttendanceClick(employee.id, date, status)}
                            data-testid={`attendance-cell-${employee.id}-${date}`}
                          >
                            {status === 'present' && <Check className="w-5 h-5 mx-auto" />}
                            {status === 'absent' && <X className="w-5 h-5 mx-auto" />}
                            {status === 'late' && (
                              <div className="flex flex-col items-center">
                                <Clock className="w-5 h-5" />
                                {hours > 0 && <span className="text-xs mt-1">{hours}h</span>}
                              </div>
                            )}
                            {!status && <span className="text-slate-300">-</span>}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 flex items-center justify-center bg-blue-100 rounded">
              <Check className="w-5 h-5 text-blue-700" />
            </div>
            <span className="text-slate-700">Presente</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 flex items-center justify-center bg-rose-100 rounded">
              <X className="w-5 h-5 text-rose-700" />
            </div>
            <span className="text-slate-700">Ausente</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 flex items-center justify-center bg-amber-100 rounded">
              <Clock className="w-5 h-5 text-amber-700" />
            </div>
            <span className="text-slate-700">Tarde</span>
          </div>
          <span className="text-slate-600 ml-auto">Haz clic en las celdas para cambiar el estado</span>
        </div>
      </Card>

      <Dialog open={showLateModal} onOpenChange={setShowLateModal}>
        <DialogContent data-testid="late-hours-dialog">
          <DialogHeader>
            <DialogTitle>Registrar Horas de Retraso</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="late_hours">Horas de Retraso</Label>
              <Input
                id="late_hours"
                data-testid="late-hours-input"
                type="number"
                step="0.5"
                min="0"
                max="8"
                value={lateHours}
                onChange={(e) => setLateHours(e.target.value)}
                placeholder="Ej: 1, 1.5, 2"
              />
              <p className="text-xs text-slate-500 mt-2">
                Se descontará el equivalente de las horas ingresadas del salario diario (jornada de 8 horas)
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLateModal(false)}>Cancelar</Button>
            <Button onClick={handleLateSubmit} data-testid="submit-late-hours-btn">Guardar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const AdvanceManagement = () => {
  const [employees, setEmployees] = useState([]);
  const [advances, setAdvances] = useState([]);
  const [weekStart, setWeekStart] = useState(getCurrentWeekStart());
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formData, setFormData] = useState({ employee_id: '', amount: '', date: '', description: '' });

  useEffect(() => {
    fetchEmployees();
    fetchAdvances();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API}/employees`);
      setEmployees(response.data.filter(e => e.is_active));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching employees:', error);
      toast.error('Error al cargar empleados');
      setLoading(false);
    }
  };

  const fetchAdvances = async () => {
    try {
      const response = await axios.get(`${API}/advances`);
      setAdvances(response.data);
    } catch (error) {
      console.error('Error fetching advances:', error);
      toast.error('Error al cargar adelantos');
    }
  };

  const handleAddAdvance = async () => {
    if (!formData.employee_id || !formData.amount || !formData.date) {
      toast.error('Por favor completa los campos obligatorios');
      return;
    }
    try {
      await axios.post(`${API}/advances`, {
        employee_id: formData.employee_id,
        amount: parseFloat(formData.amount),
        date: formData.date,
        description: formData.description,
        week_start_date: weekStart
      });
      toast.success('Adelanto registrado exitosamente');
      setIsAddModalOpen(false);
      setFormData({ employee_id: '', amount: '', date: '', description: '' });
      fetchAdvances();
    } catch (error) {
      console.error('Error adding advance:', error);
      toast.error('Error al registrar adelanto');
    }
  };

  const handleDeleteAdvance = async (id) => {
    if (!window.confirm('¿Estás seguro de eliminar este adelanto?')) return;
    try {
      await axios.delete(`${API}/advances/${id}`);
      toast.success('Adelanto eliminado exitosamente');
      await fetchAdvances();
    } catch (error) {
      console.error('Error deleting advance:', error);
      toast.error('Error al eliminar adelanto');
    }
  };

  const getEmployeeName = (employeeId) => {
    const employee = employees.find(e => e.id === employeeId);
    return employee ? employee.name : 'Desconocido';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-6" data-testid="advance-management">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Adelantos</h1>
          <p className="text-slate-500">Gestiona los adelantos de pago</p>
        </div>
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary" data-testid="add-advance-btn">
              <Plus className="w-4 h-4 mr-2" />
              Registrar Adelanto
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="add-advance-dialog">
            <DialogHeader>
              <DialogTitle>Registrar Nuevo Adelanto</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label htmlFor="employee">Empleado</Label>
                <Select value={formData.employee_id} onValueChange={(value) => setFormData({ ...formData, employee_id: value })}>
                  <SelectTrigger data-testid="advance-employee-select">
                    <SelectValue placeholder="Selecciona un empleado" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.map(emp => (
                      <SelectItem key={emp.id} value={emp.id}>{emp.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="amount">Monto</Label>
                <Input
                  id="amount"
                  data-testid="advance-amount-input"
                  type="number"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  placeholder="1000"
                />
              </div>
              <div>
                <Label htmlFor="date">Fecha</Label>
                <Input
                  id="date"
                  data-testid="advance-date-input"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="description">Descripción (opcional)</Label>
                <Input
                  id="description"
                  data-testid="advance-description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Motivo del adelanto"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleAddAdvance} data-testid="submit-advance-btn">Registrar</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Empleado</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Monto</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Fecha</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Descripción</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {advances.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-slate-400">
                    No hay adelantos registrados
                  </td>
                </tr>
              ) : (
                advances.map((advance) => (
                  <tr key={advance.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`advance-row-${advance.id}`}>
                    <td className="py-4 px-6 text-sm text-slate-700">{getEmployeeName(advance.employee_id)}</td>
                    <td className="py-4 px-6 text-sm text-slate-700 font-mono-numbers">
                      {formatCurrency(advance.amount)}
                    </td>
                    <td className="py-4 px-6 text-sm text-slate-700">{new Date(advance.date).toLocaleDateString('es-AR')}</td>
                    <td className="py-4 px-6 text-sm text-slate-500">{advance.description || '-'}</td>
                    <td className="py-4 px-6 text-right">
                      <Button variant="ghost" size="sm" onClick={() => handleDeleteAdvance(advance.id)} data-testid={`delete-advance-${advance.id}`}>
                        <Trash2 className="w-4 h-4 text-rose-500" />
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

const PaymentSummary = () => {
  const [employees, setEmployees] = useState([]);
  const [contractors, setContractors] = useState([]);
  const [weekStart, setWeekStart] = useState(getCurrentWeekStart());
  const [attendance, setAttendance] = useState([]);
  const [advances, setAdvances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [paymentData, setPaymentData] = useState([]);

  useEffect(() => {
    fetchData();
  }, [weekStart]);

  const fetchData = async () => {
    try {
      const [empRes, contrRes, attRes, advRes] = await Promise.all([
        axios.get(`${API}/employees`),
        axios.get(`${API}/contractors`),
        axios.get(`${API}/attendance/week/${weekStart}`),
        axios.get(`${API}/advances`)
      ]);
      
      setEmployees(empRes.data.filter(e => e.is_active));
      setContractors(contrRes.data.filter(c => c.is_active));
      setAttendance(attRes.data);
      setAdvances(advRes.data);
      calculatePayments(empRes.data.filter(e => e.is_active), contrRes.data.filter(c => c.is_active), attRes.data, advRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Error al cargar datos');
      setLoading(false);
    }
  };

  const calculatePayments = (emps, contrs, att, adv) => {
    const payments = [];
    
    // Calcular pagos de empleados
    emps.forEach(employee => {
      const employeeAttendance = att.filter(a => a.employee_id === employee.id);
      const daysWorked = employeeAttendance.filter(a => a.status === 'present' || a.status === 'late').length;
      
      // Calcular descuento por horas tarde
      const totalLateHours = employeeAttendance
        .filter(a => a.status === 'late')
        .reduce((sum, a) => sum + (a.late_hours || 0), 0);
      const hourlyRate = employee.daily_salary / 8;
      const lateDiscount = totalLateHours * hourlyRate;
      
      const employeeAdvances = adv.filter(a => a.employee_id === employee.id && a.week_start_date === weekStart);
      const totalAdvances = employeeAdvances.reduce((sum, a) => sum + a.amount, 0);
      
      const grossSalary = daysWorked * employee.daily_salary;
      const totalSalary = grossSalary - lateDiscount;
      const netPayment = totalSalary - totalAdvances;
      
      payments.push({
        type: 'employee',
        person: employee,
        daysWorked,
        grossSalary,
        lateDiscount,
        lateHours: totalLateHours,
        totalSalary,
        totalAdvances,
        netPayment
      });
    });
    
    // Agregar contratistas
    contrs.forEach(contractor => {
      const afterPayment = contractor.remaining_balance - contractor.weekly_payment;
      payments.push({
        type: 'contractor',
        person: contractor,
        daysWorked: 'Semanal',
        totalSalary: contractor.weekly_payment,
        totalAdvances: 0,
        netPayment: contractor.weekly_payment,
        project: contractor.project_name,
        budget: contractor.budget,
        totalPaid: contractor.total_paid || 0,
        remainingBalance: contractor.remaining_balance,
        afterPaymentBalance: afterPayment
      });
    });
    
    setPaymentData(payments);
  };

  const handleCalculatePayments = async () => {
    try {
      await axios.post(`${API}/payments/calculate`, { week_start_date: weekStart });
      toast.success('Pagos calculados y guardados en historial');
    } catch (error) {
      console.error('Error calculating payments:', error);
      toast.error('Error al calcular pagos');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  const totalToPay = paymentData.reduce((sum, p) => sum + p.netPayment, 0);

  return (
    <div className="space-y-6" data-testid="payment-summary">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Resumen de Pagos</h1>
          <p className="text-slate-500">Calcula los pagos de la semana</p>
        </div>
        <div className="flex gap-4 items-center">
          <Input
            type="date"
            data-testid="payment-week-start-input"
            value={weekStart}
            onChange={(e) => setWeekStart(e.target.value)}
            className="w-48"
          />
          <Button className="btn-primary" onClick={handleCalculatePayments} data-testid="calculate-payments-btn">
            <DollarSign className="w-4 h-4 mr-2" />
            Guardar en Historial
          </Button>
        </div>
      </div>

      <Card className="p-6 bg-gradient-to-br from-blue-50 to-sky-50 border border-blue-200 rounded-xl shadow-sm">
        <div className="text-center">
          <p className="text-sm font-medium text-blue-700 mb-2">Total a Disponer el Viernes</p>
          <p className="text-5xl font-bold text-blue-900 font-mono-numbers">{formatCurrency(totalToPay)}</p>
        </div>
      </Card>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Persona</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Tipo</th>
                <th className="text-center py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Días/Semana</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Salario Base</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Desc. Tardanzas</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Adelantos</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Pago Neto</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Saldo Obra</th>
              </tr>
            </thead>
            <tbody>
              {paymentData.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-12 text-slate-400">
                    No hay datos para mostrar
                  </td>
                </tr>
              ) : (
                paymentData.map((payment, idx) => (
                  <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`payment-row-${payment.person.id}`}>
                    <td className="py-4 px-6">
                      <div>
                        <div className="text-sm text-slate-700 font-medium">{payment.person.name}</div>
                        {payment.project && (
                          <div className="text-xs text-slate-500">{payment.project}</div>
                        )}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <Badge variant={payment.type === 'employee' ? 'default' : 'secondary'}>
                        {payment.type === 'employee' ? 'Empleado' : 'Contratista'}
                      </Badge>
                    </td>
                    <td className="py-4 px-6 text-sm text-slate-700 text-center">{payment.daysWorked}</td>
                    <td className="py-4 px-6 text-sm text-slate-700 text-right font-mono-numbers">
                      {formatCurrency(payment.type === 'employee' ? payment.grossSalary : payment.totalSalary)}
                    </td>
                    <td className="py-4 px-6 text-right">
                      {payment.type === 'employee' && payment.lateDiscount > 0 ? (
                        <div>
                          <div className="text-sm text-amber-600 font-mono-numbers">
                            -{formatCurrency(payment.lateDiscount)}
                          </div>
                          <div className="text-xs text-slate-400">
                            ({payment.lateHours}h)
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-slate-400">-</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-sm text-rose-600 text-right font-mono-numbers">
                      -{formatCurrency(payment.totalAdvances)}
                    </td>
                    <td className="py-4 px-6 text-sm text-emerald-600 text-right font-bold font-mono-numbers">
                      {formatCurrency(payment.netPayment)}
                    </td>
                    <td className="py-4 px-6 text-right">
                      {payment.type === 'contractor' ? (
                        <div className="text-right">
                          <div className={`text-sm font-bold font-mono-numbers ${
                            payment.afterPaymentBalance < 0 ? 'text-rose-600' : 
                            payment.afterPaymentBalance < payment.budget * 0.2 ? 'text-amber-600' : 
                            'text-emerald-600'
                          }`}>
                            {formatCurrency(payment.afterPaymentBalance)}
                          </div>
                          <div className="text-xs text-slate-400">
                            de {formatCurrency(payment.budget)}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-slate-400">-</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

const PaymentHistoryPage = () => {
  const [payments, setPayments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [payRes, empRes] = await Promise.all([
        axios.get(`${API}/payments/history`),
        axios.get(`${API}/employees`)
      ]);
      setPayments(payRes.data);
      setEmployees(empRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Error al cargar historial');
      setLoading(false);
    }
  };

  const getEmployeeName = (employeeId) => {
    const employee = employees.find(e => e.id === employeeId);
    return employee ? employee.name : 'Desconocido';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-6" data-testid="payment-history">
      <div>
        <h1 className="text-4xl font-bold text-slate-900 mb-2">Historial de Pagos</h1>
        <p className="text-slate-500">Consulta los pagos anteriores</p>
      </div>

      <Card className="bg-white border border-blue-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Empleado</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Semana</th>
                <th className="text-center py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Días</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Salario Total</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Adelantos</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Pago Neto</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Fecha de Pago</th>
              </tr>
            </thead>
            <tbody>
              {payments.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-12 text-slate-400">
                    No hay pagos registrados en el historial
                  </td>
                </tr>
              ) : (
                payments.map((payment) => (
                  <tr key={payment.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`history-row-${payment.id}`}>
                    <td className="py-4 px-6 text-sm text-slate-700">{getEmployeeName(payment.employee_id)}</td>
                    <td className="py-4 px-6 text-sm text-slate-700">{payment.week_start_date}</td>
                    <td className="py-4 px-6 text-sm text-slate-700 text-center">{payment.days_worked}</td>
                    <td className="py-4 px-6 text-sm text-slate-700 text-right font-mono-numbers">
                      {formatCurrency(payment.total_salary)}
                    </td>
                    <td className="py-4 px-6 text-sm text-rose-600 text-right font-mono-numbers">
                      -{formatCurrency(payment.total_advances)}
                    </td>
                    <td className="py-4 px-6 text-sm text-emerald-600 text-right font-bold font-mono-numbers">
                      {formatCurrency(payment.net_payment)}
                    </td>
                    <td className="py-4 px-6 text-sm text-slate-500">
                      {new Date(payment.paid_at).toLocaleDateString('es-AR')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

const Sidebar = () => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/employees', icon: Users, label: 'Empleados' },
    { path: '/contractors', icon: Briefcase, label: 'Contratistas' },
    { path: '/attendance', icon: Calendar, label: 'Asistencia' },
    { path: '/advances', icon: DollarSign, label: 'Adelantos' },
    { path: '/payments', icon: DollarSign, label: 'Resumen de Pagos' },
    { path: '/history', icon: History, label: 'Historial' }
  ];

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white border-b border-blue-200 px-4 py-3 flex items-center justify-between">
        <h2 className="text-xl font-bold text-blue-900">PMD PAGOS</h2>
        <button
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="p-2 rounded-lg hover:bg-blue-50"
          data-testid="mobile-menu-toggle"
        >
          {isMobileMenuOpen ? <XIcon className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-white border-r border-blue-200 
        transform transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        pt-16 lg:pt-0
      `} data-testid="sidebar">
        <div className="p-6 hidden lg:block">
          <h2 className="text-2xl font-bold text-blue-900">PMD PAGOS</h2>
          <p className="text-sm text-blue-600 mt-1">Gestión de Pagos</p>
        </div>
        <nav className="px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-3 mb-1 rounded-lg transition-all ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-medium'
                    : 'text-slate-600 hover:bg-blue-50/50'
                }`}
                data-testid={`nav-${item.path}`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Toaster position="top-right" richColors />
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 p-4 sm:p-6 lg:p-8 bg-slate-50 min-h-screen pt-20 lg:pt-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/employees" element={<EmployeeManagement />} />
              <Route path="/contractors" element={<ContractorManagement />} />
              <Route path="/attendance" element={<AttendanceSheet />} />
              <Route path="/advances" element={<AdvanceManagement />} />
              <Route path="/payments" element={<PaymentSummary />} />
              <Route path="/history" element={<PaymentHistoryPage />} />
            </Routes>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
