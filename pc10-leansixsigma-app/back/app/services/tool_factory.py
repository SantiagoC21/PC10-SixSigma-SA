from app.tools.pareto import ParetoTool
from app.tools.sampling import SamplingTool
from app.tools.risk_analysis import RiskAnalysisTool
from app.tools.anova import AnovaTool
from app.tools.cost_tree import CostTreeTool
from app.tools.structure_tree import StructureTreeTool
from app.tools.boxplot import BoxPlotTool
from app.tools.brainstorming import BrainstormingTool
from app.tools.z_bench import ZBenchTool
from app.tools.control_charts import ControlChartTool
from app.tools.gantt import GanttTool
from app.tools.cost_benefit import CostBenefitTool
from app.tools.affinity import AffinityTool
from app.tools.radar import RadarTool
from app.tools.doe import DoeTool
from app.tools.interviews import InterviewAnalysisTool
from app.tools.ishikawa import IshikawaTool
from app.tools.stratification import StratificationTool
from app.tools.fmea import FmeaTool
from app.tools.gage_rr import GageRRTool
from app.tools.run_chart import RunChartTool
from app.tools.histogram import HistogramTool
from app.tools.confidence_interval import ConfidenceIntervalTool
from app.tools.process_map import ProcessMapTool
from app.tools.raci import RaciTool
from app.tools.control_plan import ControlPlanTool
from app.tools.pareto_abc import ParetoAbcTool
from app.tools.qfd import QfdTool
from app.tools.multiple_regression import MultipleRegressionTool
from app.tools.rsm import RsmTool
from app.tools.hypothesis_test import HypothesisTestTool
from app.tools.normality_test import NormalityTestTool
from app.tools.chi_square import ChiSquareTool
from app.tools.balanced_scorecard import BalancedScorecardTool 
from app.tools.pmi import PmiTool
class ToolFactory:
    
    @staticmethod
    def get_tool(tool_name: str):
        tools_map = {
            "pareto": ParetoTool,
            "sampling": SamplingTool,
            "risk_analysis": RiskAnalysisTool,
            "amef": RiskAnalysisTool,
            "anova": AnovaTool,
            "cost_tree": CostTreeTool,
            "structure_tree": StructureTreeTool,
            "ctq_tree": StructureTreeTool,
            "job_tree": StructureTreeTool,
            "boxplot": BoxPlotTool,
            "diagrama_caja": BoxPlotTool,
            "brainstorming": BrainstormingTool,
            "lluvia_ideas": BrainstormingTool,
            "z_bench": ZBenchTool,
            "sigma_level": ZBenchTool,
            "dpmo": ZBenchTool,
            "control_charts": ControlChartTool,
            "spc": ControlChartTool,
            "xbar_r": ControlChartTool,
            "gantt": GanttTool,
            "cronograma": GanttTool,
            "cost_benefit": CostBenefitTool,
            "roi_analysis": CostBenefitTool, # Alias
            "cba": CostBenefitTool,
            "affinity_diagram": AffinityTool,
            "afinidades": AffinityTool,
            "radar": RadarTool,
            "spider_chart": RadarTool,
            "gap_analysis": RadarTool,
            "doe": DoeTool,
            "design_of_experiments": DoeTool,
            "factorial_design": DoeTool,
            "interviews": InterviewAnalysisTool,      # <--- Herramienta 20/30 Lista
            "entrevistas": InterviewAnalysisTool,     # Alias
            "voc_analysis": InterviewAnalysisTool,     # Alias
            "ishikawa": IshikawaTool,
            "fishbone": IshikawaTool,
            "espina_pescado": IshikawaTool,
            "stratification": StratificationTool, # <--- Herramienta 22/30 Lista
            "estratificacion": StratificationTool,
            "fmea": FmeaTool,      # <--- Herramienta 24/30 (Reemplaza/Complementa a risk_analysis)
            "amef_standard": FmeaTool,
            "gage_rr": GageRRTool,   # <--- Herramienta 25/30 Lista
            "msa": GageRRTool,
            "run_chart": RunChartTool,     # <--- Herramienta 26/30 Lista
            "time_series": RunChartTool,   
            "tendencias": RunChartTool,
            "histogram": HistogramTool,
            "distribucion": HistogramTool,
            "normalidad": HistogramTool,
            "confidence_interval": ConfidenceIntervalTool, # <--- Herramienta 28/30 Lista
            "intervalo_confianza": ConfidenceIntervalTool, # Alias
            "ic": ConfidenceIntervalTool,
            "process_map": ProcessMapTool,   # <--- Herramienta 29/30 Lista
            "flujograma": ProcessMapTool,    # Alias
            "flowchart": ProcessMapTool,
            "raci": RaciTool,
            "matriz_responsabilidades": RaciTool,
            "control_plan": ControlPlanTool,
            "plan_control": ControlPlanTool,  # Alias
            "control_plan_matrix": ControlPlanTool,
            "pareto_abc": ParetoAbcTool,
            "pareto": ParetoAbcTool,
            "abc_analysis": ParetoAbcTool,
            "qfd": QfdTool,
            "casa_calidad": QfdTool,
            "house_of_quality": QfdTool,
            "multiple_regression": MultipleRegressionTool, # <--- Herramienta 34 (Extra)
            "regresion_multiple": MultipleRegressionTool,
            "regression": MultipleRegressionTool,
            "rsm": RsmTool,
            "response_surface": RsmTool,
            "superficie_respuesta": RsmTool,
            "hypothesis_test": HypothesisTestTool,
            "t_test": HypothesisTestTool,
            "prueba_hipotesis": HypothesisTestTool,
            "normality_test": NormalityTestTool,
            "prueba_normalidad": NormalityTestTool,
            "qq_plot": NormalityTestTool,
            "chi_square": ChiSquareTool,
            "chi_cuadrado": ChiSquareTool,
            "crosstab": ChiSquareTool,
            "balanced_scorecard": BalancedScorecardTool,
            "bsc": BalancedScorecardTool,
            "cuadro_mando": BalancedScorecardTool,
            "pmi": PmiTool,
            "plus_minus_interesting": PmiTool,
        }
        
        tool_class = tools_map.get(tool_name.lower())
        
        if not tool_class:
            raise ValueError(f"Herramienta '{tool_name}' no encontrada o no implementada.")
            
        return tool_class   