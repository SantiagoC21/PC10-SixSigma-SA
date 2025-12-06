import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { askAI } from '../../api/client';

export const DefinePage: React.FC = () => {
  const location = useLocation();
  const state = location.state as {
    initialProblem?: string;
    defineRecommendations?: { id: string; name: string; reason?: string }[];
  } | null;

  const initialProblem = state?.initialProblem ?? '';
  const defineRecommendations = state?.defineRecommendations ?? [];
  const [measureRecommendations, setMeasureRecommendations] = useState<
    { id: string; name: string; reason?: string }[]
  >([]);
  const [loadingMeasure, setLoadingMeasure] = useState(false);
  const [measureError, setMeasureError] = useState<string | null>(null);

  const handleMeasureClick = async () => {
    if (!initialProblem.trim()) return;

    try {
      setLoadingMeasure(true);
      setMeasureError(null);
      const aiResponse = await askAI('Measure', initialProblem);
      setMeasureRecommendations(aiResponse.recommendations ?? []);
    } catch (error) {
      console.error('Error llamando a askAI (Measure):', error);
      setMeasureError('No pudimos obtener recomendaciones de Medir.');
    } finally {
      setLoadingMeasure(false);
    }
  };

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

      <section style={{ marginTop: '32px' }}>
        <button
          onClick={handleMeasureClick}
          disabled={loadingMeasure || !initialProblem.trim()}
          style={{
            padding: '10px 16px',
            backgroundColor: '#0b5ed7',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: loadingMeasure || !initialProblem.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          {loadingMeasure ? 'Cargando Medir...' : 'Medir'}
        </button>

        {measureError && (
          <p style={{ color: 'red', marginTop: '12px' }}>{measureError}</p>
        )}

        {measureRecommendations.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <h2>Herramientas de Medir recomendadas</h2>
            <ul>
              {measureRecommendations.map((rec) => (
                <li key={rec.id}>
                  <strong>{rec.name}</strong>
                  {rec.reason && <p style={{ margin: '4px 0 0 0' }}>{rec.reason}</p>}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </div>
  );
};
