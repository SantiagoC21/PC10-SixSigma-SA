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
            "estratificacion": StratificationTool
            
        }
        
        tool_class = tools_map.get(tool_name.lower())
        
        if not tool_class:
            raise ValueError(f"Herramienta '{tool_name}' no encontrada o no implementada.")
            
        return tool_class   