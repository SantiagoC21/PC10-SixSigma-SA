import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { DMAIC_STRUCTURE } from '../../../utils/menuData';
import styles from './Sidebar.module.css';

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { defineRecommendations?: { id: string; name: string }[] } | null;
  const defineRecommendations = state?.defineRecommendations;

  // Tomamos la fase Definir de la estructura estática como base (para el nombre de la fase)
  const staticDefinePhase = DMAIC_STRUCTURE.find((p) => p.id === 'Define');

  // Construimos las herramientas a partir de las recomendaciones de la IA si existen,
  // usando id como path y name como texto a mostrar.
  const defineTools = defineRecommendations && defineRecommendations.length > 0
    ? defineRecommendations.map((rec) => ({ name: rec.name, path: rec.id }))
    : staticDefinePhase?.tools ?? [];

  // Estado para saber cuál fase está abierta (por defecto 'Definir')
  const [openPhase, setOpenPhase] = useState<string | null>("Define");

  const togglePhase = (phaseId: string) => {
    // Si toco la que ya está abierta, la cierro. Si no, abro la nueva.
    setOpenPhase(openPhase === phaseId ? null : phaseId);
  };

  const handleToolClick = (toolPath: string) => {
    navigate(`/tools/${toolPath}`);
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.title}>Pasos DMAIC</div>

      {/* Solo mostramos la fase Definir */}
      {staticDefinePhase && (
        <div key={staticDefinePhase.id} className={styles.phaseContainer}>
          {/* Botón Negro de la Fase */}
          <button 
            className={`${styles.phaseButton} ${openPhase === staticDefinePhase.id ? styles.active : ''}`}
            onClick={() => togglePhase(staticDefinePhase.id)}
          >
            <span>{staticDefinePhase.phase}</span>
            <span className={`${styles.arrow} ${openPhase === staticDefinePhase.id ? styles.rotated : ''}`}>
              ▼
            </span>
          </button>

          {/* Lista de Herramientas (Solo si está abierto) */}
          {openPhase === staticDefinePhase.id && (
            <div className={styles.toolsList}>
              {defineTools.map((tool) => (
                <div 
                  key={tool.name} 
                  className={styles.toolLink}
                  onClick={() => handleToolClick(tool.path)}
                >
                  {tool.name}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};