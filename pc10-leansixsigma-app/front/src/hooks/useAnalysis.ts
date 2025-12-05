// src/hooks/useAnalysis.ts
import { useState } from 'react';
import { ToolService } from '../api/tools';
import { AnalysisResult } from '../types/analysis';

export const useAnalysis = () => {
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const executeTool = async (toolName: string, data: any[], params = {}) => {
        setLoading(true);
        setError(null);
        try {
            const res = await ToolService.analyze({ tool_name: toolName, data, parameters: params });
            setResult(res);
        } catch (err) {
            setError("Error al ejecutar la herramienta");
        } finally {
            setLoading(false);
        }
    };

    return { result, loading, error, executeTool };
};