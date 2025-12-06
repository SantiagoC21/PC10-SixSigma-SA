// src/pages/Home/index.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { askAI } from '../../api/client';
import './Home.css';

export const Home = () => {
  const [problem, setProblem] = useState('');
  const navigate = useNavigate();

  const handleContinue = async () => {
    if (!problem.trim()) return;

    try {
      const aiResponse = await askAI('Define', problem);
      console.log('Respuesta IA (Define):', aiResponse);

      // Navegar a la pantalla Definir pasando también las recomendaciones de la IA
      navigate('/define', { 
        state: { 
          initialProblem: problem,
          defineRecommendations: aiResponse.recommendations
        } 
      });
    } catch (error) {
      console.error('Error llamando a askAI:', error);
      // Si falla la IA, igual navegamos solo con el problema inicial
      navigate('/define', { state: { initialProblem: problem } });
    }

    // Navegar a la siguiente ruta (ej: crear proyecto)
    // Pasamos el problema como "state" para que la siguiente pantalla lo reciba
    // y pueda preguntarle a la IA.
  };

  return (
    <div className="home-container">
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