import axios from 'axios';

// Detectamos la IP del servidor automáticamente desde la URL del navegador
const SERVER_IP = window.location.hostname;
const API_BASE_URL = `http://${SERVER_IP}:8000/api`;

console.log("Conectando a API en:", API_BASE_URL);

const api = {
  getSectores: () => axios.get(`${API_BASE_URL}/sectores`),
  getAreas: (sectorId) => axios.get(`${API_BASE_URL}/areas/${sectorId}`),
  getProyectos: () => axios.get(`${API_BASE_URL}/proyectos`),
  getProyecto: (id) => axios.get(`${API_BASE_URL}/proyectos/${id}`),
  createProyecto: (data) => axios.post(`${API_BASE_URL}/proyectos`, data),
  updateProyecto: (id, data) => axios.put(`${API_BASE_URL}/proyectos/${id}`, data),
  deleteProyecto: (id) => axios.delete(`${API_BASE_URL}/proyectos/${id}`),
  getRequisitos: (areaId) => axios.get(`${API_BASE_URL}/requisitos/${areaId}`),
  getSelecciones: (proyectoId) => axios.get(`${API_BASE_URL}/selecciones/${proyectoId}`),
  saveSelecciones: (proyectoId, requisitoIds) => axios.post(`${API_BASE_URL}/selecciones/${proyectoId}`, requisitoIds),
  getProyectoTex: (proyectoId, requisitoId) => axios.get(`${API_BASE_URL}/selecciones/${proyectoId}/${requisitoId}/tex`),
  saveProyectoMetadata: (proyectoId, requisitoId, metadata) => axios.post(`${API_BASE_URL}/selecciones/${proyectoId}/${requisitoId}/metadata`, metadata),
  getStructures: () => axios.get(`${API_BASE_URL}/estructuras`),
  getUbigeo: () => axios.get(`${API_BASE_URL}/ubigeo`),
  previewPdf: (proyectoId, texCode = null) => axios.post(`${API_BASE_URL}/pdf/preview`, { proyecto_id: proyectoId, tex_code: texCode }),
};

export default api;
