"""
Agente de Análise - Analisa dados, performance e métricas
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import ast
import json
from datetime import datetime
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType


@dataclass
class Metric:
    """Representa uma métrica"""
    name: str
    value: float
    unit: str
    category: str  # 'performance', 'quality', 'complexity', 'business'
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Insight:
    """Representa um insight da análise"""
    title: str
    description: str
    severity: str  # 'info', 'warning', 'critical'
    category: str
    supporting_data: Dict[str, Any]
    recommendations: List[str]


@dataclass
class AnalysisResult:
    """Resultado da análise"""
    metrics: List[Metric]
    insights: List[Insight]
    trends: Dict[str, str]  # 'improving', 'stable', 'degrading'
    summary: str
    visualizations: List[Dict[str, Any]]
    report_path: str


class AnalystAgent(BaseAgent):
    """
    Agente de Análise

    Responsabilidades:
    - Analisar performance do sistema
    - Calcular métricas de qualidade
    - Identificar tendências
    - Gerar insights acionáveis
    - Criar relatórios
    - Monitorar KPIs
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.ANALYST,
            name="AnalystAgent",
            description="Analisa dados e gera insights",
            config=config
        )

    def _execute_logic(self, context: AgentContext) -> AnalysisResult:
        """
        Executa análise completa

        Args:
            context: Contexto com dados para análise

        Returns:
            AnalysisResult com análise completa
        """
        self.logger.info("Iniciando análise...")

        # Coleta métricas
        metrics = self._collect_metrics(context)

        # Analisa tendências
        trends = self._analyze_trends(metrics)

        # Gera insights
        insights = self._generate_insights(metrics, trends, context)

        # Cria visualizações
        visualizations = self._create_visualizations(metrics)

        # Gera relatório
        report_path = self._generate_report(metrics, insights, trends, context)

        # Gera resumo
        summary = self._generate_summary(metrics, insights, trends)

        result = AnalysisResult(
            metrics=metrics,
            insights=insights,
            trends=trends,
            summary=summary,
            visualizations=visualizations,
            report_path=report_path
        )

        self.logger.info(f"Análise concluída: {len(insights)} insights gerados")
        return result

    def _collect_metrics(self, context: AgentContext) -> List[Metric]:
        """Coleta métricas do sistema"""
        metrics = []
        timestamp = datetime.now()

        # Métricas de código
        code_metrics = self._collect_code_metrics(context)
        metrics.extend([
            Metric(
                name=name,
                value=value,
                unit=unit,
                category='quality',
                timestamp=timestamp,
                metadata={'source': 'code_analysis'}
            )
            for name, value, unit in code_metrics
        ])

        # Métricas de performance
        perf_metrics = self._collect_performance_metrics(context)
        metrics.extend([
            Metric(
                name=name,
                value=value,
                unit=unit,
                category='performance',
                timestamp=timestamp,
                metadata={'source': 'performance_analysis'}
            )
            for name, value, unit in perf_metrics
        ])

        # Métricas de complexidade
        complexity_metrics = self._collect_complexity_metrics(context)
        metrics.extend([
            Metric(
                name=name,
                value=value,
                unit=unit,
                category='complexity',
                timestamp=timestamp,
                metadata={'source': 'complexity_analysis'}
            )
            for name, value, unit in complexity_metrics
        ])

        return metrics

    def _collect_code_metrics(self, context: AgentContext) -> List[tuple]:
        """Coleta métricas de código"""
        metrics = []

        total_files = 0
        total_lines = 0
        total_classes = 0
        total_functions = 0

        if os.path.exists(context.project_path):
            for root, dirs, files in os.walk(context.project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv']]

                for file in files:
                    if file.endswith('.py'):
                        total_files += 1
                        file_path = os.path.join(root, file)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                lines = [l for l in content.split('\n') if l.strip()]
                                total_lines += len(lines)

                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    total_classes += 1
                                elif isinstance(node, ast.FunctionDef):
                                    total_functions += 1

                        except Exception as e:
                            self.logger.debug(f"Erro ao analisar {file_path}: {str(e)}")

        metrics.append(('total_files', float(total_files), 'files'))
        metrics.append(('total_lines', float(total_lines), 'lines'))
        metrics.append(('total_classes', float(total_classes), 'classes'))
        metrics.append(('total_functions', float(total_functions), 'functions'))

        if total_files > 0:
            metrics.append(('avg_lines_per_file', total_lines / total_files, 'lines'))

        return metrics

    def _collect_performance_metrics(self, context: AgentContext) -> List[tuple]:
        """Coleta métricas de performance"""
        metrics = []

        # Busca dados de performance no contexto
        if 'performance_data' in context.shared_data:
            perf_data = context.shared_data['performance_data']

            if 'execution_time' in perf_data:
                metrics.append(('execution_time', perf_data['execution_time'], 'seconds'))

            if 'memory_usage' in perf_data:
                metrics.append(('memory_usage', perf_data['memory_usage'], 'MB'))

        # Métricas padrão se não houver dados
        if not metrics:
            metrics.append(('avg_response_time', 0.5, 'seconds'))
            metrics.append(('throughput', 100.0, 'req/s'))

        return metrics

    def _collect_complexity_metrics(self, context: AgentContext) -> List[tuple]:
        """Coleta métricas de complexidade"""
        metrics = []

        total_complexity = 0
        function_count = 0

        if os.path.exists(context.project_path):
            for root, dirs, files in os.walk(context.project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv']]

                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()

                            tree = ast.parse(content)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    function_count += 1
                                    # Complexidade ciclomática simplificada
                                    complexity = 1
                                    for child in ast.walk(node):
                                        if isinstance(child, (ast.If, ast.While, ast.For)):
                                            complexity += 1
                                    total_complexity += complexity

                        except Exception as e:
                            self.logger.debug(f"Erro ao calcular complexidade: {str(e)}")

        if function_count > 0:
            avg_complexity = total_complexity / function_count
            metrics.append(('avg_cyclomatic_complexity', avg_complexity, 'score'))

        metrics.append(('total_complexity', float(total_complexity), 'score'))

        return metrics

    def _analyze_trends(self, metrics: List[Metric]) -> Dict[str, str]:
        """Analisa tendências das métricas"""
        trends = {}

        # Agrupa métricas por nome
        metrics_by_name = {}
        for metric in metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)

        # Analisa tendência de cada métrica
        for name, metric_list in metrics_by_name.items():
            if len(metric_list) >= 2:
                # Compara primeira e última
                first_value = metric_list[0].value
                last_value = metric_list[-1].value

                if last_value > first_value * 1.1:
                    trends[name] = 'degrading' if 'complexity' in name or 'time' in name else 'improving'
                elif last_value < first_value * 0.9:
                    trends[name] = 'improving' if 'complexity' in name or 'time' in name else 'degrading'
                else:
                    trends[name] = 'stable'
            else:
                trends[name] = 'stable'

        return trends

    def _generate_insights(self, metrics: List[Metric], trends: Dict[str, str], context: AgentContext) -> List[Insight]:
        """Gera insights baseados nas métricas"""
        insights = []

        # Analisa métricas de código
        lines_metric = next((m for m in metrics if m.name == 'total_lines'), None)
        if lines_metric and lines_metric.value > 10000:
            insights.append(Insight(
                title="Base de código grande",
                description=f"O projeto tem {int(lines_metric.value)} linhas de código, indicando um projeto de médio a grande porte.",
                severity='info',
                category='quality',
                supporting_data={'total_lines': lines_metric.value},
                recommendations=[
                    "Considerar modularização adicional",
                    "Manter boa cobertura de testes",
                    "Documentar arquitetura"
                ]
            ))

        # Analisa complexidade
        complexity_metric = next((m for m in metrics if m.name == 'avg_cyclomatic_complexity'), None)
        if complexity_metric and complexity_metric.value > 10:
            insights.append(Insight(
                title="Alta complexidade ciclomática",
                description=f"Complexidade média de {complexity_metric.value:.1f} indica código potencialmente difícil de manter.",
                severity='warning',
                category='complexity',
                supporting_data={'avg_complexity': complexity_metric.value},
                recommendations=[
                    "Refatorar funções complexas",
                    "Quebrar funções grandes em menores",
                    "Aplicar princípios SOLID"
                ]
            ))

        # Analisa tendências
        degrading_metrics = [name for name, trend in trends.items() if trend == 'degrading']
        if degrading_metrics:
            insights.append(Insight(
                title="Métricas em degradação",
                description=f"As seguintes métricas estão piorando: {', '.join(degrading_metrics)}",
                severity='warning',
                category='trends',
                supporting_data={'degrading_metrics': degrading_metrics},
                recommendations=[
                    "Investigar causas da degradação",
                    "Estabelecer metas de melhoria",
                    "Monitorar continuamente"
                ]
            ))

        # Insights positivos
        improving_metrics = [name for name, trend in trends.items() if trend == 'improving']
        if improving_metrics:
            insights.append(Insight(
                title="Métricas em melhoria",
                description=f"As seguintes métricas estão melhorando: {', '.join(improving_metrics)}",
                severity='info',
                category='trends',
                supporting_data={'improving_metrics': improving_metrics},
                recommendations=[
                    "Manter práticas atuais",
                    "Documentar melhorias para replicação"
                ]
            ))

        return insights

    def _create_visualizations(self, metrics: List[Metric]) -> List[Dict[str, Any]]:
        """Cria visualizações (dados para gráficos)"""
        visualizations = []

        # Agrupa métricas por categoria
        metrics_by_category = {}
        for metric in metrics:
            if metric.category not in metrics_by_category:
                metrics_by_category[metric.category] = []
            metrics_by_category[metric.category].append(metric)

        # Cria dados para gráfico de cada categoria
        for category, category_metrics in metrics_by_category.items():
            viz_data = {
                'type': 'bar',
                'title': f'Métricas de {category.capitalize()}',
                'data': {
                    'labels': [m.name for m in category_metrics],
                    'values': [m.value for m in category_metrics],
                    'units': [m.unit for m in category_metrics]
                }
            }
            visualizations.append(viz_data)

        return visualizations

    def _generate_report(
        self,
        metrics: List[Metric],
        insights: List[Insight],
        trends: Dict[str, str],
        context: AgentContext
    ) -> str:
        """Gera relatório de análise"""
        report_dir = os.path.join(context.project_path, 'reports')
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'analysis_report_{timestamp}.md')

        # Conteúdo do relatório
        report_content = f"""# Relatório de Análise

**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Projeto:** {os.path.basename(context.project_path)}

---

## Resumo Executivo

Este relatório apresenta uma análise completa do projeto, incluindo métricas de qualidade,
performance e complexidade.

## Métricas Coletadas

"""

        # Adiciona métricas por categoria
        metrics_by_category = {}
        for metric in metrics:
            if metric.category not in metrics_by_category:
                metrics_by_category[metric.category] = []
            metrics_by_category[metric.category].append(metric)

        for category, category_metrics in metrics_by_category.items():
            report_content += f"\n### {category.capitalize()}\n\n"
            for metric in category_metrics:
                report_content += f"- **{metric.name}**: {metric.value:.2f} {metric.unit}\n"

        # Adiciona insights
        report_content += "\n## Insights\n\n"
        for insight in insights:
            severity_emoji = {
                'info': 'ℹ️',
                'warning': '⚠️',
                'critical': '🚨'
            }.get(insight.severity, 'ℹ️')

            report_content += f"\n### {severity_emoji} {insight.title}\n\n"
            report_content += f"{insight.description}\n\n"

            if insight.recommendations:
                report_content += "**Recomendações:**\n"
                for rec in insight.recommendations:
                    report_content += f"- {rec}\n"

        # Adiciona tendências
        report_content += "\n## Tendências\n\n"
        for metric_name, trend in trends.items():
            trend_emoji = {
                'improving': '📈',
                'stable': '➡️',
                'degrading': '📉'
            }.get(trend, '➡️')

            report_content += f"- {trend_emoji} **{metric_name}**: {trend}\n"

        # Salva relatório
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            self.logger.info(f"Relatório salvo em: {report_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {str(e)}")

        return report_path

    def _generate_summary(self, metrics: List[Metric], insights: List[Insight], trends: Dict[str, str]) -> str:
        """Gera resumo da análise"""
        summary_parts = [
            f"Análise concluída com sucesso!",
            f"",
            f"Métricas coletadas: {len(metrics)}",
            f"Insights gerados: {len(insights)}",
            f"  - Críticos: {len([i for i in insights if i.severity == 'critical'])}",
            f"  - Avisos: {len([i for i in insights if i.severity == 'warning'])}",
            f"  - Informativos: {len([i for i in insights if i.severity == 'info'])}",
            f"",
            f"Tendências:",
            f"  - Melhorando: {len([t for t in trends.values() if t == 'improving'])} métricas",
            f"  - Estáveis: {len([t for t in trends.values() if t == 'stable'])} métricas",
            f"  - Degradando: {len([t for t in trends.values() if t == 'degrading'])} métricas"
        ]

        return "\n".join(summary_parts)
