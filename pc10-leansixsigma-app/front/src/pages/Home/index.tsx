// src/pages/Home/index.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

export const Home = () => {
  const [problem, setProblem] = useState('');
  const navigate = useNavigate();

  const handleContinue = () => {
    if (!problem.trim()) return;

    // Navegar a la siguiente ruta (ej: crear proyecto)
    // Pasamos el problema como "state" para que la siguiente pantalla lo reciba
    // y pueda preguntarle a la IA.
    navigate('/projects/create', { state: { initialProblem: problem } });
  };

  return (
    <div className="home-container">
      {/* Header Superior */}
      <header className="header">
        <div className="brand">SixSigma Assistant</div>
        <div className="profile-btn">Perfil / Ayuda</div>
      </header>

      {/* Contenido Central */}
      <main className="main-content">
        <div className="main-inner">
          <div>
            <h1 className="title center">Asistente DMAIC Six Sigma</h1>
            <p className="subtitle">Ingrese la problemática que lo aqueja</p>
          </div>
          <div className="card">
            <textarea
              className="problem-input"
              placeholder="Describa aquí su problema o reto..."
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              onKeyDown={(e) => {
                // Permitir enviar con Ctrl + Enter
                if (e.key === 'Enter' && e.ctrlKey) handleContinue();
              }}
            />

            <button 
              className="action-btn" 
              onClick={handleContinue}
              disabled={!problem.trim()} // Deshabilitar si está vacío
            >
              Continuar al paso Definir
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}; 