"""
Orquestrador de Workflow - Coordena a execução de múltiplos agentes
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
from .base_agent import BaseAgent, AgentContext, AgentResult
from .agent_types import AgentType, AgentStatus, WorkflowStage
from .planner_agent import PlannerAgent
from .developer_agent import DeveloperAgent
from .reviewer_agent import ReviewerAgent
from .tester_agent import TesterAgent
from .documenter_agent import DocumenterAgent
from .analyst_agent import AnalystAgent


@dataclass
class WorkflowStep:
    """Representa um passo no workflow"""
    agent_type: AgentType
    agent: BaseAgent
    depends_on: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    optional: bool = False


@dataclass
class WorkflowResult:
    """Resultado da execução do workflow"""
    success: bool
    steps_completed: List[str]
    steps_failed: List[str]
    agent_results: Dict[str, AgentResult]
    total_duration: float
    summary: str
    metadata: Dict[str, Any]


class WorkflowOrchestrator:
    """
    Orquestrador de Workflow de Agentes

    Responsabilidades:
    - Coordenar execução de múltiplos agentes
    - Gerenciar dependências entre agentes
    - Passar contexto entre agentes
    - Tratar erros e falhas
    - Gerar relatórios de execução
    - Suportar workflows customizados
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.workflow_steps: List[WorkflowStep] = []

        # Inicializa agentes
        self._initialize_agents()

    def _initialize_agents(self):
        """Inicializa todos os agentes disponíveis"""
        self.agents = {
            AgentType.PLANNER: PlannerAgent(self.config.get('planner', {})),
            AgentType.DEVELOPER: DeveloperAgent(self.config.get('developer', {})),
            AgentType.REVIEWER: ReviewerAgent(self.config.get('reviewer', {})),
            AgentType.TESTER: TesterAgent(self.config.get('tester', {})),
            AgentType.DOCUMENTER: DocumenterAgent(self.config.get('documenter', {})),
            AgentType.ANALYST: AnalystAgent(self.config.get('analyst', {}))
        }
        self.logger.info(f"Inicializados {len(self.agents)} agentes")

    def create_workflow(self, workflow_type: str = "full_development") -> List[WorkflowStep]:
        """
        Cria um workflow baseado no tipo

        Args:
            workflow_type: Tipo de workflow ('full_development', 'code_review', 'testing_only', etc.)

        Returns:
            Lista de passos do workflow
        """
        workflows = {
            'full_development': self._create_full_development_workflow,
            'code_review': self._create_code_review_workflow,
            'testing_only': self._create_testing_workflow,
            'documentation': self._create_documentation_workflow,
            'analysis': self._create_analysis_workflow,
            'quick_fix': self._create_quick_fix_workflow,
        }

        workflow_creator = workflows.get(workflow_type, self._create_full_development_workflow)
        return workflow_creator()

    def _create_full_development_workflow(self) -> List[WorkflowStep]:
        """Cria workflow completo de desenvolvimento"""
        return [
            WorkflowStep(
                agent_type=AgentType.PLANNER,
                agent=self.agents[AgentType.PLANNER],
                depends_on=[]
            ),
            WorkflowStep(
                agent_type=AgentType.DEVELOPER,
                agent=self.agents[AgentType.DEVELOPER],
                depends_on=[AgentType.PLANNER.value]
            ),
            WorkflowStep(
                agent_type=AgentType.REVIEWER,
                agent=self.agents[AgentType.REVIEWER],
                depends_on=[AgentType.DEVELOPER.value]
            ),
            WorkflowStep(
                agent_type=AgentType.TESTER,
                agent=self.agents[AgentType.TESTER],
                depends_on=[AgentType.DEVELOPER.value]
            ),
            WorkflowStep(
                agent_type=AgentType.DOCUMENTER,
                agent=self.agents[AgentType.DOCUMENTER],
                depends_on=[AgentType.DEVELOPER.value, AgentType.REVIEWER.value]
            ),
            WorkflowStep(
                agent_type=AgentType.ANALYST,
                agent=self.agents[AgentType.ANALYST],
                depends_on=[
                    AgentType.REVIEWER.value,
                    AgentType.TESTER.value
                ]
            )
        ]

    def _create_code_review_workflow(self) -> List[WorkflowStep]:
        """Cria workflow apenas de revisão"""
        return [
            WorkflowStep(
                agent_type=AgentType.REVIEWER,
                agent=self.agents[AgentType.REVIEWER],
                depends_on=[]
            ),
            WorkflowStep(
                agent_type=AgentType.ANALYST,
                agent=self.agents[AgentType.ANALYST],
                depends_on=[AgentType.REVIEWER.value]
            )
        ]

    def _create_testing_workflow(self) -> List[WorkflowStep]:
        """Cria workflow apenas de testes"""
        return [
            WorkflowStep(
                agent_type=AgentType.TESTER,
                agent=self.agents[AgentType.TESTER],
                depends_on=[]
            ),
            WorkflowStep(
                agent_type=AgentType.ANALYST,
                agent=self.agents[AgentType.ANALYST],
                depends_on=[AgentType.TESTER.value]
            )
        ]

    def _create_documentation_workflow(self) -> List[WorkflowStep]:
        """Cria workflow apenas de documentação"""
        return [
            WorkflowStep(
                agent_type=AgentType.DOCUMENTER,
                agent=self.agents[AgentType.DOCUMENTER],
                depends_on=[]
            )
        ]

    def _create_analysis_workflow(self) -> List[WorkflowStep]:
        """Cria workflow apenas de análise"""
        return [
            WorkflowStep(
                agent_type=AgentType.ANALYST,
                agent=self.agents[AgentType.ANALYST],
                depends_on=[]
            )
        ]

    def _create_quick_fix_workflow(self) -> List[WorkflowStep]:
        """Cria workflow para correções rápidas"""
        return [
            WorkflowStep(
                agent_type=AgentType.DEVELOPER,
                agent=self.agents[AgentType.DEVELOPER],
                depends_on=[]
            ),
            WorkflowStep(
                agent_type=AgentType.TESTER,
                agent=self.agents[AgentType.TESTER],
                depends_on=[AgentType.DEVELOPER.value]
            )
        ]

    def execute_workflow(
        self,
        task_description: str,
        project_path: str,
        workflow_type: str = "full_development",
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Executa um workflow completo

        Args:
            task_description: Descrição da tarefa
            project_path: Caminho do projeto
            workflow_type: Tipo de workflow a executar
            context_metadata: Metadados adicionais para o contexto

        Returns:
            WorkflowResult com resultados da execução
        """
        start_time = datetime.now()

        self.logger.info(f"Iniciando workflow: {workflow_type}")
        self.logger.info(f"Tarefa: {task_description}")

        # Cria contexto compartilhado
        context = AgentContext(
            project_path=project_path,
            task_description=task_description,
            metadata=context_metadata or {},
            shared_data={},
            history=[]
        )

        # Cria workflow
        steps = self.create_workflow(workflow_type)

        # Executa workflow
        steps_completed = []
        steps_failed = []
        agent_results = {}

        for step in steps:
            agent_name = step.agent_type.value

            # Verifica dependências
            if not self._check_dependencies(step, steps_completed, steps_failed):
                if step.optional:
                    self.logger.warning(f"Pulando passo opcional {agent_name} devido a dependências não atendidas")
                    continue
                else:
                    self.logger.error(f"Dependências não atendidas para {agent_name}")
                    steps_failed.append(agent_name)
                    continue

            # Executa agente
            self.logger.info(f"Executando agente: {agent_name}")
            try:
                result = step.agent.execute(context)
                agent_results[agent_name] = result

                if result.is_success():
                    steps_completed.append(agent_name)
                    self.logger.info(f"Agente {agent_name} concluído com sucesso")

                    # Armazena resultado no contexto compartilhado
                    context.shared_data[agent_name] = result.output
                else:
                    steps_failed.append(agent_name)
                    self.logger.error(f"Agente {agent_name} falhou: {result.errors}")

                    # Para se não for opcional
                    if not step.optional:
                        self.logger.error("Parando workflow devido a falha em passo obrigatório")
                        break

            except Exception as e:
                self.logger.error(f"Erro ao executar {agent_name}: {str(e)}", exc_info=True)
                steps_failed.append(agent_name)

                if not step.optional:
                    break

        # Calcula duração total
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()

        # Determina sucesso
        success = len(steps_failed) == 0 and len(steps_completed) > 0

        # Gera resumo
        summary = self._generate_workflow_summary(
            steps_completed,
            steps_failed,
            agent_results,
            total_duration
        )

        result = WorkflowResult(
            success=success,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            agent_results=agent_results,
            total_duration=total_duration,
            summary=summary,
            metadata={
                'workflow_type': workflow_type,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'task': task_description
            }
        )

        self.logger.info(f"Workflow concluído: {'SUCESSO' if success else 'FALHA'}")
        return result

    def _check_dependencies(
        self,
        step: WorkflowStep,
        completed: List[str],
        failed: List[str]
    ) -> bool:
        """Verifica se as dependências de um passo foram atendidas"""
        for dependency in step.depends_on:
            if dependency in failed:
                return False
            if dependency not in completed:
                return False
        return True

    def _generate_workflow_summary(
        self,
        completed: List[str],
        failed: List[str],
        results: Dict[str, AgentResult],
        duration: float
    ) -> str:
        """Gera resumo da execução do workflow"""
        summary_lines = [
            "=" * 60,
            "RESUMO DO WORKFLOW",
            "=" * 60,
            f"Duração total: {duration:.2f}s",
            f"Passos concluídos: {len(completed)}",
            f"Passos falhos: {len(failed)}",
            ""
        ]

        if completed:
            summary_lines.append("✓ CONCLUÍDOS:")
            for agent_name in completed:
                result = results.get(agent_name)
                if result:
                    summary_lines.append(f"  - {agent_name} ({result.execution_time:.2f}s)")

        if failed:
            summary_lines.append("")
            summary_lines.append("✗ FALHOS:")
            for agent_name in failed:
                result = results.get(agent_name)
                if result and result.errors:
                    summary_lines.append(f"  - {agent_name}: {result.errors[0]}")
                else:
                    summary_lines.append(f"  - {agent_name}")

        summary_lines.append("=" * 60)

        return "\n".join(summary_lines)

    def execute_custom_workflow(
        self,
        task_description: str,
        project_path: str,
        agent_sequence: List[AgentType],
        context_metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Executa um workflow customizado

        Args:
            task_description: Descrição da tarefa
            project_path: Caminho do projeto
            agent_sequence: Sequência de agentes a executar
            context_metadata: Metadados adicionais

        Returns:
            WorkflowResult
        """
        # Cria steps customizados
        custom_steps = []
        previous_agent = None

        for agent_type in agent_sequence:
            depends_on = [previous_agent.value] if previous_agent else []

            custom_steps.append(WorkflowStep(
                agent_type=agent_type,
                agent=self.agents[agent_type],
                depends_on=depends_on
            ))

            previous_agent = agent_type

        # Executa usando os steps customizados
        start_time = datetime.now()

        context = AgentContext(
            project_path=project_path,
            task_description=task_description,
            metadata=context_metadata or {},
            shared_data={},
            history=[]
        )

        steps_completed = []
        steps_failed = []
        agent_results = {}

        for step in custom_steps:
            agent_name = step.agent_type.value

            if not self._check_dependencies(step, steps_completed, steps_failed):
                steps_failed.append(agent_name)
                continue

            try:
                result = step.agent.execute(context)
                agent_results[agent_name] = result

                if result.is_success():
                    steps_completed.append(agent_name)
                    context.shared_data[agent_name] = result.output
                else:
                    steps_failed.append(agent_name)
                    break

            except Exception as e:
                self.logger.error(f"Erro: {str(e)}")
                steps_failed.append(agent_name)
                break

        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        success = len(steps_failed) == 0

        summary = self._generate_workflow_summary(
            steps_completed,
            steps_failed,
            agent_results,
            total_duration
        )

        return WorkflowResult(
            success=success,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            agent_results=agent_results,
            total_duration=total_duration,
            summary=summary,
            metadata={'workflow_type': 'custom'}
        )

    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """Retorna um agente específico"""
        return self.agents.get(agent_type)

    def list_available_workflows(self) -> List[str]:
        """Lista workflows disponíveis"""
        return [
            'full_development',
            'code_review',
            'testing_only',
            'documentation',
            'analysis',
            'quick_fix'
        ]
