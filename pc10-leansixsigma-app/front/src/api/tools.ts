// src/api/tools.ts
import { apiClient } from './client'; // El que creamos antes
import { AnalysisRequest, AnalysisResult } from '../types/analysis';

export const ToolService = {
    analyze: async (payload: AnalysisRequest): Promise<AnalysisResult> => {
        const { data } = await apiClient.post<AnalysisResult>('/analyze', payload);
        return data;
    },
    
    getAiRecommendation: async (phase: string, text: string) => {
        const { data } = await apiClient.post('/recommend', { phase, description: text });
        return data;
    }
};