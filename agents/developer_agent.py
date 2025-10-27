"""
Agente de Desenvolvimento - Desenvolve código e implementações
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import ast
import re
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType


@dataclass
class CodeChange:
    """Representa uma mudança no código"""
    file_path: str
    change_type: str  # 'create', 'modify', 'delete'
    description: str
    code: str = ""
    line_start: int = None
    line_end: int = None


@dataclass
class DevelopmentResult:
    """Resultado do desenvolvimento"""
    changes: List[CodeChange]
    files_created: List[str]
    files_modified: List[str]
    files_deleted: List[str]
    summary: str
    complexity_score: int
    metadata: Dict[str, Any]


class DeveloperAgent(BaseAgent):
    """
    Agente de Desenvolvimento

    Responsabilidades:
    - Implementar novas features
    - Corrigir bugs
    - Refatorar código
    - Seguir padrões de código
    - Escrever código limpo e manutenível
    - Integrar com código existente
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.DEVELOPER,
            name="DeveloperAgent",
            description="Desenvolve e implementa código seguindo melhores práticas",
            config=config
        )

    def _execute_logic(self, context: AgentContext) -> DevelopmentResult:
        """
        Implementa as mudanças de código necessárias

        Args:
            context: Contexto com a tarefa de desenvolvimento

        Returns:
            DevelopmentResult com todas as mudanças realizadas
        """
        self.logger.info("Iniciando desenvolvimento...")

        # Analisa o código existente
        codebase_analysis = self._analyze_codebase(context.project_path)

        # Planeja as mudanças necessárias
        planned_changes = self._plan_changes(context, codebase_analysis)

        # Gera o código
        changes = self._generate_code(planned_changes, context)

        # Valida as mudanças
        validation_results = self._validate_changes(changes, context)

        # Prepara resultado
        result = DevelopmentResult(
            changes=changes,
            files_created=[c.file_path for c in changes if c.change_type == 'create'],
            files_modified=[c.file_path for c in changes if c.change_type == 'modify'],
            files_deleted=[c.file_path for c in changes if c.change_type == 'delete'],
            summary=self._generate_summary(changes),
            complexity_score=self._calculate_complexity(changes),
            metadata={
                'validation': validation_results,
                'patterns_used': self._identify_patterns(changes),
                'lines_added': sum(len(c.code.split('\n')) for c in changes if c.code),
            }
        )

        self.logger.info(f"Desenvolvimento concluído: {len(changes)} mudanças")
        return result

    def _analyze_codebase(self, project_path: str) -> Dict[str, Any]:
        """Analisa o código existente para entender a estrutura"""
        analysis = {
            'structure': {},
            'patterns': [],
            'dependencies': [],
            'style': {}
        }

        # Identifica estrutura de diretórios
        if os.path.exists(project_path):
            for root, dirs, files in os.walk(project_path):
                # Ignora diretórios comuns
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]

                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, project_path)
                        analysis['structure'][rel_path] = {
                            'type': 'python',
                            'size': os.path.getsize(file_path)
                        }

        return analysis

    def _plan_changes(self, context: AgentContext, codebase_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Planeja as mudanças necessárias baseado no contexto"""
        changes = []

        task_lower = context.task_description.lower()

        # Detecta tipo de mudança necessária
        if 'criar' in task_lower or 'adicionar' in task_lower or 'implementar' in task_lower:
            changes.append({
                'type': 'feature',
                'action': 'create',
                'description': context.task_description
            })

        if 'corrigir' in task_lower or 'bug' in task_lower or 'fix' in task_lower:
            changes.append({
                'type': 'bugfix',
                'action': 'modify',
                'description': context.task_description
            })

        if 'refatorar' in task_lower or 'melhorar' in task_lower or 'otimizar' in task_lower:
            changes.append({
                'type': 'refactor',
                'action': 'modify',
                'description': context.task_description
            })

        return changes

    def _generate_code(self, planned_changes: List[Dict[str, Any]], context: AgentContext) -> List[CodeChange]:
        """Gera o código necessário para as mudanças planejadas"""
        code_changes = []

        for change in planned_changes:
            if change['type'] == 'feature':
                # Exemplo de geração de código para nova feature
                code_change = self._generate_feature_code(change, context)
                code_changes.append(code_change)

            elif change['type'] == 'bugfix':
                code_change = self._generate_bugfix_code(change, context)
                code_changes.append(code_change)

            elif change['type'] == 'refactor':
                code_change = self._generate_refactor_code(change, context)
                code_changes.append(code_change)

        return code_changes

    def _generate_feature_code(self, change: Dict[str, Any], context: AgentContext) -> CodeChange:
        """Gera código para uma nova feature"""
        # Template básico de código
        code_template = '''"""
{description}
"""

from typing import Any, Dict, List
import logging


class NewFeature:
    """Implementação da nova feature"""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Executa a funcionalidade principal

        Args:
            **kwargs: Parâmetros da execução

        Returns:
            Resultado da execução
        """
        self.logger.info("Executando feature...")

        result = {{
            'status': 'success',
            'data': None
        }}

        return result
'''

        code = code_template.format(description=change['description'])

        return CodeChange(
            file_path=os.path.join(context.project_path, 'new_feature.py'),
            change_type='create',
            description=change['description'],
            code=code
        )

    def _generate_bugfix_code(self, change: Dict[str, Any], context: AgentContext) -> CodeChange:
        """Gera código para correção de bug"""
        return CodeChange(
            file_path='<to_be_determined>',
            change_type='modify',
            description=f"Bugfix: {change['description']}",
            code="# Código de correção seria gerado aqui baseado no bug específico"
        )

    def _generate_refactor_code(self, change: Dict[str, Any], context: AgentContext) -> CodeChange:
        """Gera código refatorado"""
        return CodeChange(
            file_path='<to_be_determined>',
            change_type='modify',
            description=f"Refactor: {change['description']}",
            code="# Código refatorado seria gerado aqui"
        )

    def _validate_changes(self, changes: List[CodeChange], context: AgentContext) -> Dict[str, Any]:
        """Valida as mudanças geradas"""
        validation = {
            'syntax_valid': True,
            'style_compliant': True,
            'issues': []
        }

        for change in changes:
            if change.code:
                # Valida sintaxe Python
                try:
                    ast.parse(change.code)
                except SyntaxError as e:
                    validation['syntax_valid'] = False
                    validation['issues'].append(f"Syntax error in {change.file_path}: {str(e)}")

                # Valida estilo (simplificado)
                if len(change.code.split('\n')) > 500:
                    validation['issues'].append(f"File {change.file_path} too long (>500 lines)")

        return validation

    def _generate_summary(self, changes: List[CodeChange]) -> str:
        """Gera um resumo das mudanças"""
        summary_parts = []

        created = len([c for c in changes if c.change_type == 'create'])
        modified = len([c for c in changes if c.change_type == 'modify'])
        deleted = len([c for c in changes if c.change_type == 'delete'])

        if created:
            summary_parts.append(f"{created} arquivo(s) criado(s)")
        if modified:
            summary_parts.append(f"{modified} arquivo(s) modificado(s)")
        if deleted:
            summary_parts.append(f"{deleted} arquivo(s) deletado(s)")

        return ", ".join(summary_parts) if summary_parts else "Nenhuma mudança"

    def _calculate_complexity(self, changes: List[CodeChange]) -> int:
        """Calcula score de complexidade das mudanças (1-10)"""
        score = 1

        # Mais arquivos = mais complexo
        score += min(len(changes), 5)

        # Mais linhas = mais complexo
        total_lines = sum(len(c.code.split('\n')) for c in changes if c.code)
        score += min(total_lines // 100, 3)

        return min(score, 10)

    def _identify_patterns(self, changes: List[CodeChange]) -> List[str]:
        """Identifica padrões de design utilizados"""
        patterns = []

        for change in changes:
            if change.code:
                if 'class' in change.code and '__init__' in change.code:
                    patterns.append('OOP')
                if 'ABC' in change.code or 'abstractmethod' in change.code:
                    patterns.append('Abstract Base Class')
                if 'def __enter__' in change.code:
                    patterns.append('Context Manager')

        return list(set(patterns))
