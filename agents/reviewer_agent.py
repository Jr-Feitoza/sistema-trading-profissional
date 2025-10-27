"""
Agente de Revisão - Revisa código e qualidade
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import ast
import re
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType


@dataclass
class ReviewIssue:
    """Representa um problema encontrado na revisão"""
    severity: str  # 'critical', 'major', 'minor', 'info'
    category: str  # 'bug', 'security', 'performance', 'style', 'maintainability'
    file_path: str
    line_number: int
    description: str
    suggestion: str


@dataclass
class ReviewMetrics:
    """Métricas da revisão de código"""
    lines_of_code: int
    complexity_score: int
    maintainability_index: float
    test_coverage: float
    code_smells: int
    duplications: int


@dataclass
class ReviewResult:
    """Resultado da revisão de código"""
    approved: bool
    issues: List[ReviewIssue]
    metrics: ReviewMetrics
    summary: str
    recommendations: List[str]
    quality_score: float  # 0-100


class ReviewerAgent(BaseAgent):
    """
    Agente de Revisão de Código

    Responsabilidades:
    - Revisar qualidade do código
    - Identificar bugs potenciais
    - Verificar padrões de código
    - Analisar segurança
    - Sugerir melhorias
    - Calcular métricas de qualidade
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.REVIEWER,
            name="ReviewerAgent",
            description="Revisa código e identifica problemas de qualidade",
            config=config
        )
        self.severity_weights = {
            'critical': 10,
            'major': 5,
            'minor': 2,
            'info': 0
        }

    def _execute_logic(self, context: AgentContext) -> ReviewResult:
        """
        Executa revisão completa do código

        Args:
            context: Contexto com código para revisar

        Returns:
            ReviewResult com análise completa
        """
        self.logger.info("Iniciando revisão de código...")

        # Identifica arquivos para revisar
        files_to_review = self._identify_files(context)

        # Executa revisão em cada arquivo
        all_issues = []
        for file_path in files_to_review:
            issues = self._review_file(file_path, context)
            all_issues.extend(issues)

        # Calcula métricas
        metrics = self._calculate_metrics(files_to_review, context)

        # Gera recomendações
        recommendations = self._generate_recommendations(all_issues, metrics)

        # Calcula score de qualidade
        quality_score = self._calculate_quality_score(all_issues, metrics)

        # Decide se aprova
        approved = self._should_approve(all_issues, quality_score)

        # Gera resumo
        summary = self._generate_summary(all_issues, metrics, approved)

        result = ReviewResult(
            approved=approved,
            issues=all_issues,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations,
            quality_score=quality_score
        )

        self.logger.info(f"Revisão concluída: {len(all_issues)} issues encontradas")
        return result

    def _identify_files(self, context: AgentContext) -> List[str]:
        """Identifica arquivos para revisar"""
        files = []

        # Se há arquivos específicos no contexto
        if 'files' in context.shared_data:
            return context.shared_data['files']

        # Caso contrário, revisa arquivos Python no projeto
        if os.path.exists(context.project_path):
            for root, dirs, filenames in os.walk(context.project_path):
                # Ignora diretórios comuns
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]

                for filename in filenames:
                    if filename.endswith('.py'):
                        files.append(os.path.join(root, filename))

        return files[:10]  # Limita a 10 arquivos para não sobrecarregar

    def _review_file(self, file_path: str, context: AgentContext) -> List[ReviewIssue]:
        """Revisa um arquivo específico"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Análise sintática
            issues.extend(self._check_syntax(file_path, content))

            # Análise de estilo
            issues.extend(self._check_style(file_path, lines))

            # Análise de complexidade
            issues.extend(self._check_complexity(file_path, content))

            # Análise de segurança
            issues.extend(self._check_security(file_path, content))

            # Análise de melhores práticas
            issues.extend(self._check_best_practices(file_path, content, lines))

        except Exception as e:
            self.logger.error(f"Erro ao revisar {file_path}: {str(e)}")
            issues.append(ReviewIssue(
                severity='major',
                category='bug',
                file_path=file_path,
                line_number=0,
                description=f"Erro ao processar arquivo: {str(e)}",
                suggestion="Verificar encoding e estrutura do arquivo"
            ))

        return issues

    def _check_syntax(self, file_path: str, content: str) -> List[ReviewIssue]:
        """Verifica erros de sintaxe"""
        issues = []

        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append(ReviewIssue(
                severity='critical',
                category='bug',
                file_path=file_path,
                line_number=e.lineno or 0,
                description=f"Erro de sintaxe: {e.msg}",
                suggestion="Corrigir erro de sintaxe antes de continuar"
            ))

        return issues

    def _check_style(self, file_path: str, lines: List[str]) -> List[ReviewIssue]:
        """Verifica padrões de estilo"""
        issues = []

        for i, line in enumerate(lines, 1):
            # Linha muito longa
            if len(line) > 120:
                issues.append(ReviewIssue(
                    severity='minor',
                    category='style',
                    file_path=file_path,
                    line_number=i,
                    description="Linha muito longa (>120 caracteres)",
                    suggestion="Quebrar linha em múltiplas linhas"
                ))

            # Trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                issues.append(ReviewIssue(
                    severity='minor',
                    category='style',
                    file_path=file_path,
                    line_number=i,
                    description="Espaços em branco no final da linha",
                    suggestion="Remover espaços em branco desnecessários"
                ))

        return issues

    def _check_complexity(self, file_path: str, content: str) -> List[ReviewIssue]:
        """Verifica complexidade do código"""
        issues = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Conta complexidade ciclomática simplificada
                    complexity = self._calculate_cyclomatic_complexity(node)

                    if complexity > 10:
                        issues.append(ReviewIssue(
                            severity='major',
                            category='maintainability',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"Função '{node.name}' muito complexa (complexidade: {complexity})",
                            suggestion="Refatorar função em funções menores"
                        ))

        except Exception as e:
            self.logger.debug(f"Erro ao analisar complexidade: {str(e)}")

        return issues

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calcula complexidade ciclomática de uma função"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Cada decisão aumenta a complexidade
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _check_security(self, file_path: str, content: str) -> List[ReviewIssue]:
        """Verifica problemas de segurança"""
        issues = []

        # Padrões inseguros comuns
        security_patterns = [
            (r'eval\(', 'Uso de eval() é inseguro', 'critical'),
            (r'exec\(', 'Uso de exec() é inseguro', 'critical'),
            (r'pickle\.loads?\(', 'Pickle pode ser inseguro com dados não confiáveis', 'major'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Senha hardcoded no código', 'critical'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'API key hardcoded no código', 'critical'),
        ]

        for pattern, description, severity in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                issues.append(ReviewIssue(
                    severity=severity,
                    category='security',
                    file_path=file_path,
                    line_number=line_number,
                    description=description,
                    suggestion="Remover dados sensíveis do código e usar variáveis de ambiente"
                ))

        return issues

    def _check_best_practices(self, file_path: str, content: str, lines: List[str]) -> List[ReviewIssue]:
        """Verifica melhores práticas"""
        issues = []

        # Verifica docstrings
        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append(ReviewIssue(
                            severity='minor',
                            category='maintainability',
                            file_path=file_path,
                            line_number=node.lineno,
                            description=f"{'Função' if isinstance(node, ast.FunctionDef) else 'Classe'} '{node.name}' sem docstring",
                            suggestion="Adicionar docstring explicando propósito e parâmetros"
                        ))

        except Exception as e:
            self.logger.debug(f"Erro ao verificar best practices: {str(e)}")

        return issues

    def _calculate_metrics(self, files: List[str], context: AgentContext) -> ReviewMetrics:
        """Calcula métricas de código"""
        total_lines = 0
        total_complexity = 0
        code_smells = 0

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_lines += len([l for l in lines if l.strip()])

                    # Calcula complexidade
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_complexity += self._calculate_cyclomatic_complexity(node)

                    # Identifica code smells
                    if len(lines) > 500:
                        code_smells += 1  # Arquivo muito grande
                    if content.count('TODO') + content.count('FIXME') > 5:
                        code_smells += 1  # Muitos TODOs

            except Exception as e:
                self.logger.debug(f"Erro ao calcular métricas para {file_path}: {str(e)}")

        avg_complexity = total_complexity / max(len(files), 1)

        # Calcula maintainability index (simplificado)
        # Formula: 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # V = volume, G = complexidade, LOC = linhas de código
        import math
        maintainability = max(0, min(100, 171 - 0.23 * avg_complexity - 16.2 * math.log(max(total_lines, 1))))

        return ReviewMetrics(
            lines_of_code=total_lines,
            complexity_score=int(avg_complexity),
            maintainability_index=round(maintainability, 2),
            test_coverage=0.0,  # Seria calculado com ferramentas de coverage
            code_smells=code_smells,
            duplications=0  # Seria calculado com análise mais profunda
        )

    def _generate_recommendations(self, issues: List[ReviewIssue], metrics: ReviewMetrics) -> List[str]:
        """Gera recomendações baseadas nos issues e métricas"""
        recommendations = []

        # Recomendações baseadas em issues críticos
        critical_issues = [i for i in issues if i.severity == 'critical']
        if critical_issues:
            recommendations.append(f"URGENTE: Corrigir {len(critical_issues)} issue(s) crítico(s) antes de fazer deploy")

        # Recomendações baseadas em segurança
        security_issues = [i for i in issues if i.category == 'security']
        if security_issues:
            recommendations.append(f"Revisar {len(security_issues)} problema(s) de segurança identificado(s)")

        # Recomendações baseadas em métricas
        if metrics.complexity_score > 15:
            recommendations.append("Considerar refatoração para reduzir complexidade")

        if metrics.maintainability_index < 50:
            recommendations.append("Índice de manutenibilidade baixo - melhorar estrutura e documentação")

        if metrics.code_smells > 5:
            recommendations.append(f"Identificados {metrics.code_smells} code smells - revisar design")

        if not recommendations:
            recommendations.append("Código em boa qualidade! Continue assim.")

        return recommendations

    def _calculate_quality_score(self, issues: List[ReviewIssue], metrics: ReviewMetrics) -> float:
        """Calcula score de qualidade (0-100)"""
        score = 100.0

        # Penaliza por issues
        for issue in issues:
            score -= self.severity_weights.get(issue.severity, 1)

        # Penaliza por métricas ruins
        if metrics.complexity_score > 10:
            score -= (metrics.complexity_score - 10) * 2

        if metrics.code_smells > 0:
            score -= metrics.code_smells * 3

        # Bonus por métricas boas
        if metrics.maintainability_index > 80:
            score += 5

        return max(0.0, min(100.0, score))

    def _should_approve(self, issues: List[ReviewIssue], quality_score: float) -> bool:
        """Decide se deve aprovar o código"""
        # Não aprova se há issues críticos
        if any(i.severity == 'critical' for i in issues):
            return False

        # Não aprova se score é muito baixo
        if quality_score < 60:
            return False

        # Não aprova se há muitos issues de segurança
        security_issues = [i for i in issues if i.category == 'security']
        if len(security_issues) > 2:
            return False

        return True

    def _generate_summary(self, issues: List[ReviewIssue], metrics: ReviewMetrics, approved: bool) -> str:
        """Gera resumo da revisão"""
        status = "APROVADO ✓" if approved else "REPROVADO ✗"

        summary_parts = [
            f"Status: {status}",
            f"Issues encontradas: {len(issues)}",
            f"  - Críticas: {len([i for i in issues if i.severity == 'critical'])}",
            f"  - Maiores: {len([i for i in issues if i.severity == 'major'])}",
            f"  - Menores: {len([i for i in issues if i.severity == 'minor'])}",
            f"Linhas de código: {metrics.lines_of_code}",
            f"Complexidade média: {metrics.complexity_score}",
            f"Índice de manutenibilidade: {metrics.maintainability_index}"
        ]

        return "\n".join(summary_parts)
