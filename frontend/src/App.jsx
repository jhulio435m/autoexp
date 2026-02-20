import React, { useState, useEffect } from 'react';
import api from './api';
import { 
  FileText, Settings, Plus, FolderOpen, ChevronRight, LayoutDashboard, 
  Save, FileCode, ArrowLeft, Trash2, RefreshCw, MapPin, Briefcase, 
  Layers, FileSearch, ChevronDown, LogOut, Bell, Check, Info, X, 
  Edit3, Eye, Download, Search, FileCheck, FileX, ChevronUp
} from 'lucide-react';

// --- COMPONENTES ATÓMICOS ---

const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden ${className}`}>
    {children}
  </div>
);

const Input = ({ label, value, onChange, type = "text", placeholder = "" }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</label>
    <input
      type={type} value={value || ''} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm"
    />
  </div>
);

const TextArea = ({ label, value, onChange, placeholder = "" }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</label>
    <textarea
      value={value || ''} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm min-h-[100px]"
    />
  </div>
);

const Select = ({ label, value, onChange, options, formatFunc = (v) => v }) => (
  <div className="space-y-1.5">
    <label className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{label}</label>
    <select
      value={value || ''} onChange={(e) => onChange(e.target.value)}
      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-sm appearance-none"
    >
      <option value="">Seleccione...</option>
      {options.map((opt, i) => (<option key={i} value={opt.id || opt}>{formatFunc(opt)}</option>))}
    </select>
  </div>
);

// --- MODALES ---

function NewProjectModal({ isOpen, onClose, onSuccess }) {
  const [ubigeoData, setUbigeoData] = useState({});
  const [sectores, setSectores] = useState([]);
  const [areas, setAreas] = useState([]);
  const [formData, setFormData] = useState({
    entidad: '', nombre: '', cui: '', departamento: '', provincia: '', distrito: '', localidad: '',
    sector_id: '', area_id: '', monto: 0, plazo: 0, modalidad: 'CONTRATA', sistema_contratacion: 'SUMA ALZADA',
    jefe_proyecto: '', cip_jefe: '', zona_utm: '18S', este_utm: 0, norte_utm: 0
  });

  useEffect(() => {
    if (isOpen) {
      api.getUbigeo().then(res => setUbigeoData(res.data));
      api.getSectores().then(res => setSectores(res.data));
    }
  }, [isOpen]);

  useEffect(() => {
    if (formData.sector_id) api.getAreas(formData.sector_id).then(res => setAreas(res.data));
    else setAreas([]);
  }, [formData.sector_id]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await api.createProyecto(formData);
      onSuccess(res.data.id);
    } catch (err) { alert("Error: " + err.message); }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <Card className="max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <h2 className="text-xl font-black text-slate-900 uppercase">Nuevo Expediente</h2>
          <button onClick={onClose} className="p-2 hover:bg-white rounded-lg text-slate-400 transition-all border border-slate-200"><X size={20} /></button>
        </div>
        <form onSubmit={handleSubmit} className="flex-1 overflow-auto p-8 space-y-8">
          <div className="grid grid-cols-2 gap-8">
            <div className="space-y-4">
              <Select label="Sector" value={formData.sector_id} options={sectores} formatFunc={s => s.nombre} onChange={v => setFormData({...formData, sector_id: v, area_id: ''})} />
              <Select label="Área" value={formData.area_id} options={areas} formatFunc={a => a.nombre} onChange={v => setFormData({...formData, area_id: v})} />
              <Input label="CUI" value={formData.cui} onChange={v => setFormData({...formData, cui: v})} />
              <Input label="Entidad" value={formData.entidad} onChange={v => setFormData({...formData, entidad: v})} />
            </div>
            <div className="space-y-4">
              <Select label="Departamento" value={formData.departamento} options={Object.keys(ubigeoData)} onChange={v => setFormData({...formData, departamento: v, provincia: '', distrito: ''})} />
              <Select label="Provincia" value={formData.provincia} options={formData.departamento ? Object.keys(ubigeoData[formData.departamento]) : []} onChange={v => setFormData({...formData, provincia: v, distrito: ''})} />
              <Select label="Distrito" value={formData.distrito} options={(formData.departamento && formData.provincia) ? ubigeoData[formData.departamento][formData.provincia] : []} onChange={v => setFormData({...formData, distrito: v})} />
              <Input label="Localidad" value={formData.localidad} onChange={v => setFormData({...formData, localidad: v})} />
            </div>
            <div className="col-span-2"><TextArea label="Nombre del Proyecto" value={formData.nombre} onChange={v => setFormData({...formData, nombre: v})} /></div>
          </div>
        </form>
        <div className="p-6 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button onClick={onClose} className="px-6 py-2 rounded-xl text-xs font-black text-slate-500 uppercase">CANCELAR</button>
          <button onClick={handleSubmit} className="bg-slate-900 text-white px-8 py-2 rounded-xl text-xs font-black uppercase hover:bg-blue-600 transition-all">CREAR</button>
        </div>
      </Card>
    </div>
  );
}

// --- NAVEGACIÓN ---

const SidebarItem = ({ active, label, onClick, icon: Icon, sub = false }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
      active ? "bg-blue-600 text-white shadow-lg" : "text-slate-400 hover:text-white hover:bg-slate-800"
    } ${sub ? "ml-4 w-[calc(100%-1rem)]" : ""}`}
  >
    <Icon size={18} />
    <span className="truncate">{label}</span>
  </button>
);

const SidebarSection = ({ label }) => (
  <div className="px-4 mt-6 mb-2 text-[10px] font-black text-slate-600 uppercase tracking-widest">{label}</div>
);

// --- PANTALLAS ---

function ProjectSelection({ onSelectProject }) {
  const [proyectos, setProyectos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchProyectos = () => {
    setLoading(true);
    api.getProyectos().then(res => { setProyectos(res.data); setLoading(false); });
  };

  useEffect(() => fetchProyectos(), []);

  if (loading && proyectos.length === 0) return (
    <div className="flex flex-col items-center justify-center h-screen gap-4">
      <RefreshCw className="animate-spin text-blue-600" size={40} />
      <p className="text-slate-500 font-medium italic">Sincronizando...</p>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto py-12 px-6">
      <div className="flex justify-between items-end mb-10">
        <div>
          <h1 className="text-4xl font-black text-slate-900 uppercase tracking-tighter">Mis Expedientes</h1>
          <p className="text-slate-500 mt-1">Gestión automatizada de documentación técnica.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="bg-slate-900 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 hover:bg-blue-600 transition-all shadow-xl shadow-slate-900/10">
          <Plus size={20} /> NUEVO PROYECTO
        </button>
      </div>
      <div className="grid grid-cols-1 gap-4">
        {proyectos.map(p => (
          <Card key={p.id} className="hover:border-blue-400 transition-all group card-hover p-6 flex items-center">
            <div className="bg-slate-50 p-4 rounded-xl text-slate-400 group-hover:text-blue-600 transition-colors"><FileSearch size={28} /></div>
            <div className="ml-6 flex-1">
              <span className="text-[10px] font-black bg-blue-100 text-blue-700 px-2 py-0.5 rounded uppercase">{p.cui}</span>
              <h3 className="text-xl font-black text-slate-800 uppercase group-hover:text-blue-600 transition-colors mt-1 leading-tight">{p.nombre}</h3>
            </div>
            <button onClick={() => onSelectProject(p)} className="bg-slate-900 text-white px-8 py-3 rounded-xl font-black text-xs hover:bg-blue-600 transition-all flex items-center gap-2 uppercase tracking-widest">GESTIONAR <ChevronRight size={16} /></button>
          </Card>
        ))}
      </div>
      <NewProjectModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onSuccess={() => {setIsModalOpen(false); fetchProyectos();}} />
    </div>
  );
}

function ProjectDashboard({ proyecto, onBack }) {
  const [view, setView] = useState('editor'); // 'editor', 'config_general', 'config_tecnica'
  const [subview, setSubview] = useState('list'); // 'list', 'edit', 'preview'
  const [pData, setPData] = useState(proyecto);
  const [saving, setSaving] = useState(false);
  
  const [requisitos, setRequisitos] = useState([]);
  const [selecciones, setSelecciones] = useState([]);
  const [loadingTech, setLoadingTech] = useState(false);

  const [activeDoc, setActiveDoc] = useState(null);
  const [mode, setMode] = useState('form'); // 'form' o 'latex'
  const [texCode, setTexCode] = useState('');
  const [pdfDisplay, setPdfDisplay] = useState(null);
  const [compiling, setCompiling] = useState(false);
  const [isLoadingDoc, setIsLoadingDoc] = useState(false);
  const [docMetadata, setDocMetadata] = useState({});
  const [docStructures, setDocStructures] = useState({});

  useEffect(() => {
    api.getStructures().then(res => setDocStructures(res.data));
  }, []);

  // Función para obtener la estructura del documento activo
  const getActiveStructure = () => {
    if (!activeDoc || !docStructures) return null;
    const sectorSlug = pData.sector_slug || 'transporte'; // Fallback a transporte para prueba
    const docKey = activeDoc.nombre.toLowerCase().includes('resumen ejecutivo') ? 'resumen_ejecutivo' : 
                   activeDoc.nombre.toLowerCase().includes('memoria descriptiva') ? 'memoria_descriptiva' : null;
    return docStructures[sectorSlug]?.[docKey];
  };

  const renderField = (field) => (
    <div key={field.id}>
      {field.type === 'textarea' ? (
        <TextArea 
          label={field.label} 
          value={docMetadata[field.id]} 
          onChange={v => setDocMetadata({...docMetadata, [field.id]: v})} 
        />
      ) : field.type === 'select' ? (
        <Select 
          label={field.label} 
          value={docMetadata[field.id]} 
          options={field.options}
          onChange={v => setDocMetadata({...docMetadata, [field.id]: v})} 
        />
      ) : (
        <Input 
          label={field.label} 
          type={field.type}
          value={docMetadata[field.id]} 
          onChange={v => setDocMetadata({...docMetadata, [field.id]: v})} 
        />
      )}
    </div>
  );

  // Grupos contraídos (por ID de grupo)
  const [collapsedGroups, setCollapsedGroups] = useState([]);
  const [collapsedTechGroups, setCollapsedTechGroups] = useState([]);

  const toggleGroup = (groupId, isTech = false) => {
    if (isTech) {
      setCollapsedTechGroups(prev => 
        prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
      );
    } else {
      setCollapsedGroups(prev => 
        prev.includes(groupId) ? prev.filter(id => id !== groupId) : [...prev, groupId]
      );
    }
  };

  const fetchTechData = () => {
    setLoadingTech(true);
    Promise.all([api.getRequisitos(pData.area_id), api.getSelecciones(pData.id)])
      .then(([reqRes, selRes]) => {
        setRequisitos(reqRes.data);
        setSelecciones(selRes.data);
        setLoadingTech(false);
      });
  };

  useEffect(() => {
    if (view === 'config_tecnica' || view === 'editor') fetchTechData();
  }, [view, pData.area_id, pData.id]);

  const handleSave = async () => {
    setSaving(true);
    try {
      if (view === 'config_tecnica') {
        await api.saveSelecciones(pData.id, selecciones);
      } else if (view === 'editor' && subview === 'edit') {
        await api.saveProyectoMetadata(pData.id, activeDoc.id, docMetadata);
      } else {
        await api.updateProyecto(pData.id, pData);
      }
    } catch (err) { console.error(err); }
    setSaving(false);
  };

  const handleAction = async (doc, action) => {
    if (action === 'delete') {
      if (confirm("¿Eliminar este documento? Se desmarcará del checklist.")) {
        const nuevas = selecciones.filter(id => id !== doc.id);
        await api.saveSelecciones(pData.id, nuevas);
        setSelecciones(nuevas);
      }
      return;
    }

    setActiveDoc(doc);
    setIsLoadingDoc(true);
    setPdfDisplay(null);
    setTexCode('');

    try {
      const res = await api.getProyectoTex(pData.id, doc.id);
      setTexCode(res.data.tex_code);
      setDocMetadata(res.data.metadata || {});

      if (action === 'edit') {
        setSubview('edit');
        setMode('form');
      } else if (action === 'view') {
        setSubview('preview');
        const pdfRes = await api.previewPdf(pData.id, res.data.tex_code);
        setPdfDisplay(pdfRes.data.pdf_base64);
      } else if (action === 'download') {
        const pdfRes = await api.previewPdf(pData.id, res.data.tex_code);
        const link = document.createElement('a');
        link.href = `data:application/pdf;base64,${pdfRes.data.pdf_base64}`;
        link.download = `${doc.nombre.replace(/ /g, '_')}.pdf`;
        link.click();
      }
    } catch (err) {
      console.error(err);
      alert("Error al cargar documento");
    } finally {
      setIsLoadingDoc(false);
    }
  };

  const handleCompile = async (overrideTex = null) => {
    setCompiling(true);
    try {
      const res = await api.previewPdf(pData.id, overrideTex || texCode);
      setPdfDisplay(res.data.pdf_base64);
    } catch (err) { alert("Error al compilar"); }
    finally { setCompiling(false); }
  };

  const handleDownload = (doc) => {
    api.previewPdf(pData.id, texCode).then(res => {
      const link = document.createElement('a');
      link.href = `data:application/pdf;base64,${res.data.pdf_base64}`;
      link.download = `${doc.nombre.replace(/ /g, '_')}.pdf`;
      link.click();
    });
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      <aside className="w-72 bg-slate-900 flex flex-col shrink-0">
        <div className="p-6 border-b border-slate-800/50 flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-black">H</div>
          <span className="text-white font-black text-sm tracking-tighter">HEISENBERG</span>
        </div>
        <nav className="flex-1 overflow-y-auto p-4 space-y-1">
          <SidebarSection label="Laboratorio" />
          <SidebarItem icon={FileCode} label="Generador de Docs" active={view === 'editor'} onClick={() => {setView('editor'); setSubview('list');}} />
          <SidebarSection label="Configuración" />
          <SidebarItem icon={LayoutDashboard} label="Datos Generales" active={view === 'config_general'} onClick={() => setView('config_general')} sub />
          <SidebarItem icon={Layers} label="Estructura Técnica" active={view === 'config_tecnica'} onClick={() => setView('config_tecnica')} sub />
        </nav>
        <div className="p-4 border-t border-slate-800/50"><button onClick={onBack} className="flex items-center gap-3 w-full px-4 py-3 text-slate-400 hover:text-white hover:bg-red-500/10 rounded-lg font-bold transition-all"><LogOut size={18} /> Salir</button></div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-20 bg-white border-b border-slate-200 px-8 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px] font-black">{pData.cui}</span>
            <h2 className="font-black text-slate-900 truncate uppercase">{pData.nombre}</h2>
          </div>
          <button onClick={handleSave} disabled={saving} className="bg-slate-900 text-white px-6 py-2.5 rounded-xl font-black text-xs hover:bg-blue-600 transition-all flex items-center gap-2">
            {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />} GUARDAR CAMBIOS
          </button>
        </header>

        <main className="flex-1 overflow-auto bg-[#F1F5F9] p-8">
          {view === 'config_general' && (
            <div className="max-w-4xl mx-auto space-y-6">
              <Card className="p-8">
                <h3 className="text-xl font-black mb-8 uppercase text-slate-900 border-b pb-4">Configuración General</h3>
                <div className="grid grid-cols-2 gap-6">
                  <Input label="Entidad" value={pData.entidad} onChange={v => setPData({...pData, entidad: v})} />
                  <Input label="CUI" value={pData.cui} onChange={v => setPData({...pData, cui: v})} />
                  <div className="col-span-2"><TextArea label="Nombre del Proyecto" value={pData.nombre} onChange={v => setPData({...pData, nombre: v})} /></div>
                  <Input label="Jefe de Proyecto" value={pData.jefe_proyecto} onChange={v => setPData({...pData, jefe_proyecto: v})} />
                  <Input label="CIP" value={pData.cip_jefe} onChange={v => setPData({...pData, cip_jefe: v})} />
                  <Input label="Monto" type="number" value={pData.monto} onChange={v => setPData({...pData, monto: v})} />
                  <Input label="Plazo" type="number" value={pData.plazo} onChange={v => setPData({...pData, plazo: v})} />
                </div>
              </Card>
            </div>
          )}

          {view === 'config_tecnica' && (
            <div className="max-w-6xl mx-auto space-y-6">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h3 className="text-3xl font-black text-slate-900 uppercase">Estructura del Expediente</h3>
                  <p className="text-slate-500 text-sm mt-1 uppercase font-bold tracking-widest text-blue-600/60">Configura los componentes obligatorios del proyecto</p>
                </div>
                <div className="bg-white border border-slate-200 px-4 py-2 rounded-xl shadow-sm flex items-center gap-3">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Seleccionados: {selecciones.length} items</span>
                </div>
              </div>

              {loadingTech ? (
                <div className="flex justify-center py-20"><RefreshCw className="animate-spin text-blue-600" size={32} /></div>
              ) : (
                <div className="space-y-4">
                  {requisitos.map(g => {
                    const isCollapsed = collapsedTechGroups.includes(g.id);
                    return (
                      <div 
                        key={g.id} 
                        className={`transition-all duration-500 rounded-3xl border ${
                          isCollapsed 
                            ? 'bg-transparent border-transparent' 
                            : 'bg-white border-slate-200 shadow-xl shadow-slate-200/50 p-2'
                        }`}
                      >
                        <button 
                          onClick={() => toggleGroup(g.id, true)}
                          className={`flex items-center justify-between w-full group/header px-4 py-4 rounded-2xl transition-all duration-300 ${
                            isCollapsed ? 'hover:bg-white hover:shadow-sm' : 'bg-slate-50/50'
                          }`}
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-black text-xs transition-all duration-500 ${
                              isCollapsed ? 'bg-slate-900 text-white' : 'bg-blue-600 text-white'
                            }`}>
                              {g.letra}
                            </div>
                            <div className="text-left">
                              <h4 className="font-black text-slate-800 uppercase tracking-widest text-xs group-hover/header:text-blue-600 transition-colors">
                                {g.nombre}
                              </h4>
                              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Componentes de Ingeniería</p>
                            </div>
                          </div>
                          <div className={`p-2 rounded-full transition-all duration-500 ${
                            isCollapsed ? 'text-slate-400' : 'text-blue-600 bg-blue-100 rotate-180'
                          }`}>
                            <ChevronDown size={20} />
                          </div>
                        </button>

                        <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${
                          isCollapsed ? 'grid-rows-[0fr] opacity-0' : 'grid-rows-[1fr] opacity-100'
                        }`}>
                          <div className="overflow-hidden">
                            <div className={`p-4 pt-6 grid gap-3 ${g.letra === 'A' ? 'grid-cols-2' : 'grid-cols-1'}`}>
                              {g.items.map(i => (
                                <label 
                                  key={i.id} 
                                  className={`flex items-center gap-3 p-4 rounded-xl border transition-all cursor-pointer group/item relative ${
                                    selecciones.includes(i.id) 
                                      ? "bg-blue-50 border-blue-200 text-blue-900 ring-2 ring-blue-500/5 shadow-sm" 
                                      : "bg-white border-slate-100 text-slate-600 hover:border-slate-300 hover:bg-slate-50"
                                  }`}
                                >
                                  <div className={`w-5 h-5 rounded flex items-center justify-center border transition-all ${
                                    selecciones.includes(i.id)
                                      ? "bg-blue-600 border-blue-600"
                                      : "bg-white border-slate-300 group-hover/item:border-blue-400"
                                  }`}>
                                    {selecciones.includes(i.id) && <Check size={14} className="text-white" />}
                                  </div>
                                  <input 
                                    type="checkbox" 
                                    className="hidden" 
                                    checked={selecciones.includes(i.id)}
                                    onChange={() => setSelecciones(selecciones.includes(i.id) ? selecciones.filter(x => x !== i.id) : [...selecciones, i.id])}
                                  />
                                  <div className="flex-1 flex items-center justify-between">
                                    <span className="text-[11px] font-black uppercase tracking-tight line-clamp-1">{i.nombre}</span>
                                    {i.normativa && (
                                      <div className="relative group/info ml-2">
                                        <Info size={14} className="text-slate-300 hover:text-blue-500 transition-colors shrink-0" />
                                        <div className="absolute bottom-full right-0 mb-2 w-64 p-3 bg-slate-900 text-white text-[10px] rounded-lg shadow-xl opacity-0 invisible group-hover/info:opacity-100 group-hover/info:visible transition-all z-50 pointer-events-none font-sans normal-case tracking-normal">
                                          <p className="font-black text-blue-400 uppercase tracking-widest mb-1">Normativa</p>
                                          <p className="font-medium text-slate-300 leading-relaxed italic">"{i.normativa}"</p>
                                          <div className="absolute top-full right-4 border-8 border-transparent border-t-slate-900"></div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                </label>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {view === 'editor' && subview === 'list' && (
            <div className="max-w-5xl mx-auto space-y-8">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-3xl font-black text-slate-900 uppercase">Panel de Control Documental</h3>
                  <p className="text-slate-500 text-sm mt-1 uppercase font-bold tracking-widest">Documentos del Expediente Técnico</p>
                </div>
                <div className="bg-blue-50 text-blue-600 px-4 py-2 rounded-xl border border-blue-100 font-black text-xs">
                  {selecciones.length} DOCUMENTOS ACTIVOS
                </div>
              </div>

              {requisitos.map(g => {
                const itemsGrupo = g.items.filter(i => selecciones.includes(i.id));
                if (itemsGrupo.length === 0) return null;
                const isCollapsed = collapsedGroups.includes(g.id);
                
                return (
                  <div 
                    key={g.id} 
                    className={`transition-all duration-500 rounded-3xl border ${
                      isCollapsed 
                        ? 'bg-transparent border-transparent' 
                        : 'bg-white border-slate-200 shadow-xl shadow-slate-200/50 p-2'
                    }`}
                  >
                    <button 
                      onClick={() => toggleGroup(g.id)}
                      className={`flex items-center justify-between w-full group/header px-4 py-4 rounded-2xl transition-all duration-300 ${
                        isCollapsed ? 'hover:bg-white hover:shadow-sm' : 'bg-slate-50/50'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center font-black text-xs transition-all duration-500 ${
                          isCollapsed ? 'bg-slate-900 text-white shadow-lg' : 'bg-blue-600 text-white shadow-blue-600/20'
                        }`}>
                          {g.letra}
                        </div>
                        <div className="text-left">
                          <h4 className="font-black text-slate-800 uppercase tracking-widest text-xs group-hover/header:text-blue-600 transition-colors">
                            {g.nombre}
                          </h4>
                          <span className="text-[10px] font-black text-blue-500/60 uppercase tracking-widest">
                            {itemsGrupo.length} Documentos en el lote
                          </span>
                        </div>
                      </div>
                      <div className={`p-2 rounded-full transition-all duration-500 ${
                        isCollapsed ? 'text-slate-400' : 'text-blue-600 bg-blue-100 rotate-180'
                      }`}>
                        <ChevronDown size={20} />
                      </div>
                    </button>
                    
                    <div className={`grid transition-[grid-template-rows,opacity] duration-500 ease-in-out ${
                      isCollapsed ? 'grid-rows-[0fr] opacity-0' : 'grid-rows-[1fr] opacity-100'
                    }`}>
                      <div className="overflow-hidden">
                        <div className="p-4 pt-6 grid grid-cols-1 gap-3">
                          {itemsGrupo.map(i => (
                            <div key={i.id} className="group/item relative">
                              <Card className="p-4 flex items-center justify-between hover:border-blue-300 transition-all bg-white shadow-sm border-slate-100 hover:shadow-md">
                                <div className="flex items-center gap-4">
                                  <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 group-hover/item:text-blue-600 group-hover/item:bg-blue-50 transition-all border border-transparent group-hover/item:border-blue-100">
                                    <FileText size={20} />
                                  </div>
                                  <div>
                                    <p className="font-black text-slate-800 text-sm uppercase tracking-tight">{i.nombre}</p>
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <button onClick={() => handleAction(i, 'view')} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" title="Ver PDF"><Eye size={18} /></button>
                                  <button onClick={() => handleAction(i, 'edit')} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all" title="Editar Contenido"><Edit3 size={18} /></button>
                                  <button onClick={() => handleAction(i, 'download')} className="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all" title="Descargar PDF"><Download size={18} /></button>
                                  <div className="w-px h-6 bg-slate-100 mx-1"></div>
                                  <button onClick={() => handleAction(i, 'delete')} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all" title="Deseleccionar"><Trash2 size={18} /></button>
                                </div>
                              </Card>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {view === 'editor' && subview === 'edit' && (
            <div className="h-full flex flex-col gap-6">
              <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200">
                <div className="flex items-center gap-4">
                  <button onClick={() => setSubview('list')} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500"><ArrowLeft size={20} /></button>
                  <div>
                    <h3 className="font-black text-slate-900 uppercase leading-none">{activeDoc?.nombre}</h3>
                    <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest mt-1">Editando Contenido Técnico</p>
                  </div>
                </div>
                <div className="flex bg-slate-100 p-1 rounded-lg">
                  <button onClick={() => setMode('form')} className={`px-6 py-2 rounded-md text-[10px] font-black tracking-widest transition-all ${mode === 'form' ? 'bg-white shadow text-blue-600' : 'text-slate-500'}`}>FORMULARIO</button>
                  <button onClick={() => setMode('latex')} className={`px-6 py-2 rounded-md text-[10px] font-black tracking-widest transition-all ${mode === 'latex' ? 'bg-white shadow text-blue-600' : 'text-slate-500'}`}>EDITOR LATEX</button>
                </div>
                <button onClick={() => handleCompile()} disabled={compiling} className="bg-blue-600 text-white px-6 py-2.5 rounded-xl text-[10px] font-black tracking-widest hover:bg-blue-700 transition-all flex items-center gap-2">
                  {compiling ? <RefreshCw size={14} className="animate-spin" /> : <Eye size={14} />} PREVISUALIZAR
                </button>
              </div>

              <div className="flex-1 grid grid-cols-2 gap-6 min-h-0">
                                  <Card className="flex flex-col bg-slate-50 relative overflow-hidden">
                                    {isLoadingDoc ? (
                                      <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center">
                                        <RefreshCw className="animate-spin text-blue-600" size={32} />
                                      </div>
                                    ) : null}
                                    
                                    {mode === 'form' ? (
                                      <div className="p-10 space-y-10 overflow-y-auto">
                                        <div className="flex items-center gap-4 mb-2">
                                          <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-blue-600 shadow-sm border border-slate-200">
                                            <Edit3 size={24} />
                                          </div>
                                          <div>
                                            <h3 className="text-xl font-black text-slate-900 uppercase leading-none">{activeDoc?.nombre}</h3>
                                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mt-1.5">Automatización de Contenido</p>
                                          </div>
                                        </div>
                
                                                                {getActiveStructure() ? (
                                                                  <div className="space-y-12">
                                                                    {getActiveStructure().secciones.map(sec => (
                                                                      <div key={sec.id} className="space-y-8">
                                                                        <h4 className="text-xs font-black text-blue-600 uppercase tracking-[0.3em] border-b-2 border-blue-100 pb-3">
                                                                          {sec.label}
                                                                        </h4>
                                                                        
                                                                        <div className="space-y-8 pl-4 border-l-2 border-slate-100">
                                                                          {/* Renderizado de Subsecciones si existen */}
                                                                          {sec.subsecciones ? sec.subsecciones.map(sub => (
                                                                            <div key={sub.id} className="space-y-4">
                                                                              <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50 px-2 py-1 rounded w-fit">
                                                                                {sub.label}
                                                                              </h5>
                                                                              <div className="grid grid-cols-1 gap-6">
                                                                                {sub.campos.map(field => renderField(field))}
                                                                              </div>
                                                                            </div>
                                                                          )) : (
                                                                            /* Renderizado directo de campos si no hay subsecciones */
                                                                            <div className="grid grid-cols-1 gap-6">
                                                                              {sec.campos.map(field => renderField(field))}
                                                                            </div>
                                                                          )}
                                                                        </div>
                                                                      </div>
                                                                    ))}
                                                                  </div>
                                                                ) : (
                                        
                                          <div className="bg-amber-50 border border-amber-100 p-6 rounded-2xl text-center">
                                            <p className="text-amber-700 font-bold text-sm uppercase tracking-tight">Sin Estructura Dinámica</p>
                                            <p className="text-amber-600 text-xs mt-1">Este documento no tiene campos de formulario configurados. Usa el Editor LaTeX para añadir contenido manualmente.</p>
                                          </div>
                                        )}
                                      </div>
                                    ) : (
                                      <textarea 
                                        className="flex-1 p-8 font-mono text-xs bg-slate-900 text-blue-400 outline-none resize-none leading-relaxed"
                                        value={texCode} onChange={e => setTexCode(e.target.value)}
                                      />
                                    )}
                                  </Card>
                
                <Card className="bg-slate-200">
                  {pdfDisplay ? (<iframe src={`data:application/pdf;base64,${pdfDisplay}`} className="w-full h-full" />) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-400">
                      <FileSearch size={48} className="mb-4 opacity-20" />
                      <p className="text-xs font-black uppercase tracking-widest opacity-40">Sin Previsualización</p>
                    </div>
                  )}
                </Card>
              </div>
            </div>
          )}

          {view === 'editor' && subview === 'preview' && (
            <div className="h-full flex flex-col gap-6">
              <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200">
                <div className="flex items-center gap-4">
                  <button onClick={() => setSubview('list')} className="p-2 hover:bg-slate-100 rounded-lg text-slate-500"><ArrowLeft size={20} /></button>
                  <h3 className="font-black text-slate-900 uppercase leading-none">{activeDoc?.nombre}</h3>
                </div>
                <button onClick={() => handleDownload(activeDoc)} className="bg-slate-900 text-white px-6 py-2.5 rounded-xl text-xs font-black tracking-widest flex items-center gap-2 hover:bg-blue-600 transition-all">
                  <Download size={16} /> DESCARGAR PDF
                </button>
              </div>
              <Card className="flex-1 bg-white">
                {pdfDisplay ? (<iframe src={`data:application/pdf;base64,${pdfDisplay}`} className="w-full h-full" />) : (
                  <div className="flex flex-col items-center justify-center h-full gap-4">
                    <RefreshCw className="animate-spin text-blue-600" size={32} />
                    <p className="text-xs font-black text-slate-400 uppercase tracking-widest">Generando Vista Previa...</p>
                  </div>
                )}
              </Card>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [selectedProject, setSelectedProject] = useState(null);
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      {selectedProject ? <ProjectDashboard proyecto={selectedProject} onBack={() => setSelectedProject(null)} /> : <ProjectSelection onSelectProject={setSelectedProject} />}
    </div>
  );
}
