import { useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { DMAIC_STRUCTURE } from '../../../utils/menuData';
import styles from './Sidebar.module.css';

type Tool = { name: string; path: string };
type Phase = { id: string; phase: string; tools: Tool[] };

const PHASE_LABELS: Record<string, string> = {
  Define: 'Definir',
  Measure: 'Medir',
  Analyze: 'Analizar',
  Improve: 'Innovar',
  Control: 'Controlar',
};

export const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const state = location.state as { defineRecommendations?: { id: string; name: string }[] } | null;
  const defineRecommendations = state?.defineRecommendations;

  const phases = useMemo<Phase[]>(() => {
    return DMAIC_STRUCTURE.map((phase) => ({
      ...phase,
      phase: PHASE_LABELS[phase.id] ?? phase.phase,
    }));
  }, []);

  const defineTools =
    defineRecommendations && defineRecommendations.length > 0
      ? defineRecommendations.map((rec) => ({ name: rec.name, path: rec.id }))
      : DMAIC_STRUCTURE.find((p) => p.id === 'Define')?.tools ?? [];

  const [openPhase, setOpenPhase] = useState<string | null>('Define');

  const togglePhase = (phaseId: string) => {
    setOpenPhase(openPhase === phaseId ? null : phaseId);
  };

  const handleToolClick = (toolPath: string) => {
    navigate(`/tools/${toolPath}`);
  };

  return (
    <div className={styles.sidebar}>
      <div className={styles.title}>Pasos DMAIC</div>

      {phases.map((phase) => {
        const tools = phase.id === 'Define' ? defineTools : phase.tools;

        return (
          <div key={phase.id} className={styles.phaseContainer}>
            <button
              className={`${styles.phaseButton} ${openPhase === phase.id ? styles.active : ''}`}
              onClick={() => togglePhase(phase.id)}
            >
              <span>{phase.phase}</span>
              <span className={`${styles.arrow} ${openPhase === phase.id ? styles.rotated : ''}`}>▼</span>
            </button>

            {openPhase === phase.id && (
              <div className={styles.toolsList}>
                {tools.map((tool) => (
                  <div
                    key={tool.path}
                    className={styles.toolLink}
                    onClick={() => handleToolClick(tool.path)}
                  >
                    {tool.name}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
