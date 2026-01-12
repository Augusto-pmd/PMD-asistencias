import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Plus, Edit2, Trash2, Briefcase } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProjectManagement = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', start_date: '' });

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching projects:', error);
      toast.error('Error al cargar obras');
      setLoading(false);
    }
  };

  const handleAddProject = async () => {
    if (!formData.name || !formData.start_date) {
      toast.error('Por favor completa los campos obligatorios');
      return;
    }
    try {
      await axios.post(`${API}/projects`, {
        name: formData.name,
        description: formData.description,
        start_date: formData.start_date
      });
      toast.success('Obra agregada exitosamente');
      setIsAddModalOpen(false);
      setFormData({ name: '', description: '', start_date: '' });
      await fetchProjects();
    } catch (error) {
      console.error('Error adding project:', error);
      toast.error('Error al agregar obra');
    }
  };

  const handleEditProject = async () => {
    if (!formData.name || !formData.start_date) {
      toast.error('Por favor completa los campos obligatorios');
      return;
    }
    try {
      await axios.put(`${API}/projects/${selectedProject.id}`, {
        name: formData.name,
        description: formData.description,
        start_date: formData.start_date
      });
      toast.success('Obra actualizada exitosamente');
      setIsEditModalOpen(false);
      setSelectedProject(null);
      setFormData({ name: '', description: '', start_date: '' });
      await fetchProjects();
    } catch (error) {
      console.error('Error updating project:', error);
      toast.error('Error al actualizar obra');
    }
  };

  const handleDeleteProject = async (id) => {
    if (!window.confirm('¿Estás seguro de eliminar esta obra? Los empleados asignados quedarán sin obra.')) return;
    try {
      await axios.delete(`${API}/projects/${id}`);
      toast.success('Obra eliminada exitosamente');
      await fetchProjects();
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Error al eliminar obra');
    }
  };

  const openEditModal = (project) => {
    setSelectedProject(project);
    setFormData({ 
      name: project.name, 
      description: project.description || '',
      start_date: project.start_date
    });
    setIsEditModalOpen(true);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-96"><div className="text-slate-500">Cargando...</div></div>;
  }

  return (
    <div className="space-y-4 sm:space-y-6" data-testid="project-management">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-slate-900 mb-2">Obras</h1>
          <p className="text-sm sm:text-base text-slate-500">Gestiona los proyectos y obras activas</p>
        </div>
        <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
          <DialogTrigger asChild>
            <Button className="btn-primary w-full sm:w-auto" data-testid="add-project-btn">
              <Plus className="w-4 h-4 mr-2" />
              Agregar Obra
            </Button>
          </DialogTrigger>
          <DialogContent data-testid="add-project-dialog">
            <DialogHeader>
              <DialogTitle>Agregar Nueva Obra</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <Label htmlFor="name">Nombre de la Obra *</Label>
                <Input
                  id="name"
                  data-testid="project-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Casa Barrio Norte"
                />
              </div>
              <div>
                <Label htmlFor="description">Descripción</Label>
                <Input
                  id="description"
                  data-testid="project-description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Construcción de vivienda unifamiliar"
                />
              </div>
              <div>
                <Label htmlFor="start_date">Fecha de Inicio *</Label>
                <Input
                  id="start_date"
                  data-testid="project-date-input"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddModalOpen(false)}>Cancelar</Button>
              <Button onClick={handleAddProject} data-testid="submit-project-btn">Agregar</Button>
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
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Descripción</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Fecha Inicio</th>
                <th className="text-left py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Estado</th>
                <th className="text-right py-4 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {projects.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-12 text-slate-400">
                    No hay obras registradas
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
                  <tr key={project.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors" data-testid={`project-row-${project.id}`}>
                    <td className="py-4 px-6 text-sm text-slate-700 font-medium">{project.name}</td>
                    <td className="py-4 px-6 text-sm text-slate-600">{project.description || '-'}</td>
                    <td className="py-4 px-6 text-sm text-slate-700">{new Date(project.start_date).toLocaleDateString('es-AR')}</td>
                    <td className="py-4 px-6">
                      <Badge variant={project.is_active ? "success" : "secondary"} data-testid={`project-status-${project.id}`}>
                        {project.is_active ? 'Activa' : 'Inactiva'}
                      </Badge>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => openEditModal(project)} data-testid={`edit-project-${project.id}`}>
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDeleteProject(project.id)} data-testid={`delete-project-${project.id}`}>
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
        <DialogContent data-testid="edit-project-dialog">
          <DialogHeader>
            <DialogTitle>Editar Obra</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label htmlFor="edit-name">Nombre de la Obra *</Label>
              <Input
                id="edit-name"
                data-testid="edit-project-name-input"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-description">Descripción</Label>
              <Input
                id="edit-description"
                data-testid="edit-project-description-input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="edit-start-date">Fecha de Inicio *</Label>
              <Input
                id="edit-start-date"
                data-testid="edit-project-date-input"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>Cancelar</Button>
            <Button onClick={handleEditProject} data-testid="update-project-btn">Actualizar</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProjectManagement;
