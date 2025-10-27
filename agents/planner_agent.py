"""
Agente de Planejamento - Planeja tarefas e cria roadmaps
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import re
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType, TaskPriority


@dataclass
class Task:
    """Representa uma tarefa no plano"""
    id: str
    description: str
    priority: TaskPriority
    estimated_time: str
    dependencies: List[str]
    assigned_agent: str
    status: str = "pending"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ExecutionPlan:
    """Plano de execução completo"""
    tasks: List[Task]
    workflow_stages: List[str]
    estimated_total_time: str
    critical_path: List[str]
    risks: List[str]
    metadata: Dict[str, Any]


class PlannerAgent(BaseAgent):
    """
    Agente de Planejamento

    Responsabilidades:
    - Analisar requisitos e criar plano de execução
    - Quebrar tarefas complexas em subtarefas
    - Estimar esforço e tempo
    - Identificar dependências
    - Definir ordem de execução
    - Identificar riscos potenciais
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.PLANNER,
            name="PlannerAgent",
            description="Cria planos de execução detalhados para tarefas de desenvolvimento",
            config=config
        )

    def _execute_logic(self, context: AgentContext) -> ExecutionPlan:
        """
        Cria um plano de execução detalhado

        Args:
            context: Contexto com a descrição da tarefa

        Returns:
            ExecutionPlan com todas as tarefas planejadas
        """
        self.logger.info("Analisando requisitos e criando plano...")

        # Analisa a descrição da tarefa
        task_analysis = self._analyze_task(context.task_description)

        # Cria as tarefas
        tasks = self._create_tasks(task_analysis, context)

        # Define workflow stages
        workflow_stages = self._determine_workflow_stages(tasks)

        # Calcula caminho crítico
        critical_path = self._calculate_critical_path(tasks)

        # Identifica riscos
        risks = self._identify_risks(tasks, context)

        # Estima tempo total
        total_time = self._estimate_total_time(tasks)

        plan = ExecutionPlan(
            tasks=tasks,
            workflow_stages=workflow_stages,
            estimated_total_time=total_time,
            critical_path=critical_path,
            risks=risks,
            metadata={
                'complexity': task_analysis.get('complexity', 'medium'),
                'task_count': len(tasks),
                'agents_involved': list(set(t.assigned_agent for t in tasks))
            }
        )

        self.logger.info(f"Plano criado com {len(tasks)} tarefas")
        return plan

    def _analyze_task(self, description: str) -> Dict[str, Any]:
        """Analisa a descrição da tarefa para extrair informações"""
        analysis = {
            'type': 'unknown',
            'complexity': 'medium',
            'requires_coding': False,
            'requires_testing': False,
            'requires_documentation': False,
            'requires_analysis': False
        }

        description_lower = description.lower()

        # Detecta tipo de tarefa
        if any(word in description_lower for word in ['criar', 'implementar', 'desenvolver', 'adicionar']):
            analysis['type'] = 'development'
            analysis['requires_coding'] = True

        if any(word in description_lower for word in ['teste', 'test', 'validar', 'verificar']):
            analysis['requires_testing'] = True

        if any(word in description_lower for word in ['documentar', 'doc', 'readme']):
            analysis['requires_documentation'] = True

        if any(word in description_lower for word in ['analisar', 'performance', 'otimizar', 'métricas']):
            analysis['requires_analysis'] = True

        # Detecta complexidade
        if any(word in description_lower for word in ['simples', 'pequeno', 'trivial']):
            analysis['complexity'] = 'low'
        elif any(word in description_lower for word in ['complexo', 'grande', 'difícil']):
            analysis['complexity'] = 'high'

        return analysis

    def _create_tasks(self, analysis: Dict[str, Any], context: AgentContext) -> List[Task]:
        """Cria lista de tarefas baseada na análise"""
        tasks = []
        task_id = 1

        # Sempre começa com planejamento (já feito por este agente)
        tasks.append(Task(
            id=f"PLAN-{task_id}",
            description="Criar plano de execução detalhado",
            priority=TaskPriority.CRITICAL,
            estimated_time="5min",
            dependencies=[],
            assigned_agent="planner",
            status="completed"
        ))
        task_id += 1

        # Adiciona tarefas baseadas na análise
        if analysis['requires_coding']:
            tasks.append(Task(
                id=f"DEV-{task_id}",
                description=f"Implementar: {context.task_description}",
                priority=TaskPriority.HIGH,
                estimated_time=self._estimate_dev_time(analysis['complexity']),
                dependencies=[f"PLAN-1"],
                assigned_agent="developer"
            ))
            task_id += 1

        if analysis['requires_testing']:
            tasks.append(Task(
                id=f"TEST-{task_id}",
                description="Criar e executar testes automatizados",
                priority=TaskPriority.HIGH,
                estimated_time="20min",
                dependencies=[f"DEV-{task_id-1}"] if analysis['requires_coding'] else [f"PLAN-1"],
                assigned_agent="tester"
            ))
            task_id += 1

        # Sempre adiciona revisão de código se houver desenvolvimento
        if analysis['requires_coding']:
            tasks.append(Task(
                id=f"REV-{task_id}",
                description="Revisar código e qualidade",
                priority=TaskPriority.HIGH,
                estimated_time="15min",
                dependencies=[f"DEV-{d}" for d in range(2, task_id) if f"DEV-{d}" in [t.id for t in tasks]],
                assigned_agent="reviewer"
            ))
            task_id += 1

        if analysis['requires_documentation']:
            tasks.append(Task(
                id=f"DOC-{task_id}",
                description="Criar/atualizar documentação",
                priority=TaskPriority.MEDIUM,
                estimated_time="15min",
                dependencies=[t.id for t in tasks if t.assigned_agent in ['developer', 'reviewer']],
                assigned_agent="documenter"
            ))
            task_id += 1

        if analysis['requires_analysis']:
            tasks.append(Task(
                id=f"ANAL-{task_id}",
                description="Analisar resultados e performance",
                priority=TaskPriority.MEDIUM,
                estimated_time="20min",
                dependencies=[t.id for t in tasks],
                assigned_agent="analyst"
            ))
            task_id += 1

        return tasks

    def _estimate_dev_time(self, complexity: str) -> str:
        """Estima tempo de desenvolvimento baseado na complexidade"""
        if complexity == 'low':
            return "15min"
        elif complexity == 'high':
            return "60min"
        else:
            return "30min"

    def _determine_workflow_stages(self, tasks: List[Task]) -> List[str]:
        """Determina os estágios do workflow baseado nas tarefas"""
        stages = []
        agent_to_stage = {
            'planner': 'planning',
            'developer': 'development',
            'reviewer': 'review',
            'tester': 'testing',
            'documenter': 'documentation',
            'analyst': 'analysis'
        }

        for task in tasks:
            stage = agent_to_stage.get(task.assigned_agent)
            if stage and stage not in stages:
                stages.append(stage)

        return stages

    def _calculate_critical_path(self, tasks: List[Task]) -> List[str]:
        """Calcula o caminho crítico do projeto"""
        # Simplificado: retorna tasks de prioridade CRITICAL e HIGH em ordem
        critical_tasks = [
            task.id for task in sorted(
                tasks,
                key=lambda t: (t.priority.value, len(t.dependencies)),
                reverse=True
            ) if task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]
        ]
        return critical_tasks

    def _identify_risks(self, tasks: List[Task], context: AgentContext) -> List[str]:
        """Identifica riscos potenciais no projeto"""
        risks = []

        # Verifica complexidade
        high_priority_count = sum(1 for t in tasks if t.priority == TaskPriority.HIGH)
        if high_priority_count > 3:
            risks.append("Alto número de tarefas de prioridade alta pode indicar projeto complexo")

        # Verifica dependências
        max_dependencies = max((len(t.dependencies) for t in tasks), default=0)
        if max_dependencies > 3:
            risks.append("Tarefas com muitas dependências podem causar bloqueios")

        # Verifica se há testes
        has_testing = any(t.assigned_agent == 'tester' for t in tasks)
        if not has_testing:
            risks.append("Sem testes planejados - qualidade pode ser comprometida")

        return risks

    def _estimate_total_time(self, tasks: List[Task]) -> str:
        """Estima tempo total baseado nas tarefas"""
        time_mapping = {
            '5min': 5,
            '10min': 10,
            '15min': 15,
            '20min': 20,
            '30min': 30,
            '45min': 45,
            '60min': 60
        }

        total_minutes = sum(time_mapping.get(task.estimated_time, 30) for task in tasks)

        if total_minutes < 60:
            return f"{total_minutes}min"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}min" if minutes else f"{hours}h"
