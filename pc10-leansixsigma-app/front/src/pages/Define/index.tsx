import React from 'react';
import { useLocation } from 'react-router-dom';

export const DefinePage: React.FC = () => {
  const location = useLocation();
  const state = location.state as {
    initialProblem?: string;
    defineRecommendations?: { id: string; name: string; reason?: string }[];
  } | null;

  const initialProblem = state?.initialProblem ?? '';
  const defineRecommendations = state?.defineRecommendations ?? [];

  return (
    <div style={{ padding: '24px' }}>
      <h1>Definir</h1>

      {initialProblem && (
        <section style={{ marginBottom: '24px' }}>
          <h2>Problema ingresado</h2>
          <p>{initialProblem}</p>
        </section>
      )}

      {defineRecommendations.length > 0 && (
        <section>
          <h2>Herramientas recomendadas por la IA</h2>
          <ul>
            {defineRecommendations.map((rec) => (
              <li key={rec.id}>
                <strong>{rec.name}</strong>
                {rec.reason && <p style={{ margin: '4px 0 0 0' }}>{rec.reason}</p>}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
};
