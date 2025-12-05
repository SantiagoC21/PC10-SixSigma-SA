// src/types/analysis.ts
export interface AnalysisRequest {
    tool_name: string;
    data: any[];
    parameters?: Record<string, any>;
}

export interface AnalysisResult {
    tool_name: string;
    summary: string;
    chart_data: any[];
    details: any;
}