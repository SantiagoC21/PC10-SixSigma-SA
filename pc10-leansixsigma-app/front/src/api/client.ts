// frontend/src/api/client.ts
import axios from 'axios';

// Apuntamos al puerto donde corre tu FastAPI
const API_URL = 'http://127.0.0.1:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Función genérica para analizar datos
export const runAnalysis = async (toolName: string, data: any[], params: any = {}) => {
  try {
    const response = await apiClient.post('/analyze', {
      tool_name: toolName,
      data: data,
      parameters: params
    });
    return response.data;
  } catch (error) {
    console.error("Error al conectar con Python:", error);
    throw error;
  }
};

// Función para pedir recomendaciones a la IA
export const askAI = async (phase: string, description: string) => {
  try {
    const response = await apiClient.post('/recommend', {
      phase: phase,
      description: description
    });
    return response.data;
  } catch (error) {
    console.error("Error en IA:", error);
    throw error;
  }
};