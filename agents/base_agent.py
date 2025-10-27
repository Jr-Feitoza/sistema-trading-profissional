"""
Classe base para todos os agentes de IA
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .agent_types import AgentType, AgentStatus, TaskPriority


@dataclass
class AgentContext:
    """Contexto compartilhado entre agentes"""
    project_path: str
    task_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AgentResult:
    """Resultado da execução de um agente"""
    agent_type: AgentType
    status: AgentStatus
    output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0

    def is_success(self) -> bool:
        """Verifica se a execução foi bem-sucedida"""
        return self.status == AgentStatus.COMPLETED and not self.errors

    def add_error(self, error: str):
        """Adiciona um erro ao resultado"""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Adiciona um aviso ao resultado"""
        self.warnings.append(warning)


class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes de IA.

    Cada agente tem:
    - Um tipo específico (AgentType)
    - Capacidade de executar tarefas
    - Validação de entrada
    - Logging e rastreamento
    - Comunicação com outros agentes via contexto compartilhado
    """

    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None
    ):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(f"Agent.{name}")

    def execute(self, context: AgentContext) -> AgentResult:
        """
        Executa a tarefa principal do agente.

        Args:
            context: Contexto compartilhado com informações da tarefa

        Returns:
            AgentResult com o resultado da execução
        """
        start_time = datetime.now()
        self.status = AgentStatus.THINKING
        result = AgentResult(
            agent_type=self.agent_type,
            status=AgentStatus.WORKING,
            output=None
        )

        try:
            self.logger.info(f"Iniciando execução: {context.task_description}")

            # Validação de entrada
            validation_errors = self.validate_input(context)
            if validation_errors:
                result.status = AgentStatus.FAILED
                result.errors = validation_errors
                return result

            # Execução da lógica específica do agente
            self.status = AgentStatus.WORKING
            output = self._execute_logic(context)

            # Atualiza resultado
            result.output = output
            result.status = AgentStatus.COMPLETED
            self.status = AgentStatus.COMPLETED

            # Registra no histórico do contexto
            context.history.append({
                'agent': self.name,
                'timestamp': datetime.now().isoformat(),
                'result': output
            })

        except Exception as e:
            self.logger.error(f"Erro durante execução: {str(e)}", exc_info=True)
            result.status = AgentStatus.FAILED
            result.add_error(f"Exception: {str(e)}")
            self.status = AgentStatus.FAILED

        finally:
            end_time = datetime.now()
            result.execution_time = (end_time - start_time).total_seconds()
            result.timestamp = end_time

        return result

    @abstractmethod
    def _execute_logic(self, context: AgentContext) -> Any:
        """
        Implementa a lógica específica do agente.
        Deve ser sobrescrito por cada agente concreto.

        Args:
            context: Contexto da tarefa

        Returns:
            Resultado específico do agente
        """
        pass

    def validate_input(self, context: AgentContext) -> List[str]:
        """
        Valida a entrada antes da execução.
        Pode ser sobrescrito por agentes específicos.

        Args:
            context: Contexto a validar

        Returns:
            Lista de erros de validação (vazia se válido)
        """
        errors = []

        if not context.task_description:
            errors.append("Task description is required")

        if not context.project_path:
            errors.append("Project path is required")

        return errors

    def get_status(self) -> AgentStatus:
        """Retorna o status atual do agente"""
        return self.status

    def reset(self):
        """Reseta o agente para o estado inicial"""
        self.status = AgentStatus.IDLE

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, status={self.status.value})>"
