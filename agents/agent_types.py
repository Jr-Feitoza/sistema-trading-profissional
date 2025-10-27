"""
Tipos e enumerações para o sistema de agentes
"""

from enum import Enum
from typing import Dict, Any, List


class AgentType(Enum):
    """Tipos de agentes disponíveis"""
    PLANNER = "planner"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DOCUMENTER = "documenter"
    ANALYST = "analyst"


class AgentStatus(Enum):
    """Status do agente durante execução"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Prioridade de tarefas"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


class WorkflowStage(Enum):
    """Estágios do workflow de desenvolvimento"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    REVIEW = "review"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    DEPLOYMENT = "deployment"
