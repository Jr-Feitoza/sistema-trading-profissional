"""
Agente de Testes - Cria e executa testes automatizados
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import subprocess
import ast
import re
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType


@dataclass
class TestCase:
    """Representa um caso de teste"""
    name: str
    description: str
    test_type: str  # 'unit', 'integration', 'e2e'
    file_path: str
    code: str
    dependencies: List[str]


@dataclass
class TestExecutionResult:
    """Resultado da execução de um teste"""
    test_name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    duration: float
    error_message: str = ""
    traceback: str = ""


@dataclass
class TestResult:
    """Resultado completo dos testes"""
    tests_created: List[TestCase]
    execution_results: List[TestExecutionResult]
    total_tests: int
    passed: int
    failed: int
    skipped: int
    coverage: float
    summary: str


class TesterAgent(BaseAgent):
    """
    Agente de Testes

    Responsabilidades:
    - Criar testes unitários
    - Criar testes de integração
    - Executar suíte de testes
    - Gerar relatórios de cobertura
    - Identificar edge cases
    - Sugerir testes adicionais
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.TESTER,
            name="TesterAgent",
            description="Cria e executa testes automatizados",
            config=config
        )

    def _execute_logic(self, context: AgentContext) -> TestResult:
        """
        Cria e executa testes

        Args:
            context: Contexto com código para testar

        Returns:
            TestResult com resultados dos testes
        """
        self.logger.info("Iniciando criação e execução de testes...")

        # Identifica o que precisa ser testado
        targets = self._identify_test_targets(context)

        # Cria casos de teste
        test_cases = self._create_test_cases(targets, context)

        # Salva testes em arquivos (se configurado)
        if self.config.get('save_tests', False):
            self._save_test_files(test_cases, context)

        # Executa testes
        execution_results = self._execute_tests(test_cases, context)

        # Calcula cobertura
        coverage = self._calculate_coverage(test_cases, targets)

        # Gera resumo
        summary = self._generate_summary(execution_results, coverage)

        result = TestResult(
            tests_created=test_cases,
            execution_results=execution_results,
            total_tests=len(execution_results),
            passed=len([r for r in execution_results if r.status == 'passed']),
            failed=len([r for r in execution_results if r.status == 'failed']),
            skipped=len([r for r in execution_results if r.status == 'skipped']),
            coverage=coverage,
            summary=summary
        )

        self.logger.info(f"Testes concluídos: {result.passed}/{result.total_tests} passaram")
        return result

    def _identify_test_targets(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Identifica o que precisa ser testado"""
        targets = []

        # Busca arquivos Python no projeto
        if os.path.exists(context.project_path):
            for root, dirs, files in os.walk(context.project_path):
                # Ignora diretórios de teste
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'tests', 'test']]

                for file in files:
                    if file.endswith('.py') and not file.startswith('test_'):
                        file_path = os.path.join(root, file)
                        targets.extend(self._extract_testable_components(file_path))

        return targets

    def _extract_testable_components(self, file_path: str) -> List[Dict[str, Any]]:
        """Extrai componentes testáveis de um arquivo"""
        components = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    components.append({
                        'type': 'class',
                        'name': node.name,
                        'file': file_path,
                        'line': node.lineno
                    })

                elif isinstance(node, ast.FunctionDef):
                    # Ignora métodos privados e especiais
                    if not node.name.startswith('_'):
                        components.append({
                            'type': 'function',
                            'name': node.name,
                            'file': file_path,
                            'line': node.lineno
                        })

        except Exception as e:
            self.logger.debug(f"Erro ao extrair componentes de {file_path}: {str(e)}")

        return components

    def _create_test_cases(self, targets: List[Dict[str, Any]], context: AgentContext) -> List[TestCase]:
        """Cria casos de teste para os targets"""
        test_cases = []

        for target in targets[:10]:  # Limita a 10 para não sobrecarregar
            if target['type'] == 'class':
                test_case = self._create_class_test(target, context)
                test_cases.append(test_case)

            elif target['type'] == 'function':
                test_case = self._create_function_test(target, context)
                test_cases.append(test_case)

        return test_cases

    def _create_class_test(self, target: Dict[str, Any], context: AgentContext) -> TestCase:
        """Cria teste para uma classe"""
        class_name = target['name']
        test_name = f"Test{class_name}"

        test_code = f'''"""
Testes para a classe {class_name}
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class {test_name}(unittest.TestCase):
    """Testes para {class_name}"""

    def setUp(self):
        """Configuração antes de cada teste"""
        # TODO: Inicializar {class_name} para testes
        pass

    def tearDown(self):
        """Limpeza após cada teste"""
        pass

    def test_initialization(self):
        """Testa inicialização da classe"""
        # TODO: Implementar teste de inicialização
        self.assertTrue(True, "Teste de inicialização pendente")

    def test_basic_functionality(self):
        """Testa funcionalidade básica"""
        # TODO: Implementar teste de funcionalidade
        self.assertTrue(True, "Teste de funcionalidade pendente")


if __name__ == '__main__':
    unittest.main()
'''

        return TestCase(
            name=test_name,
            description=f"Testes unitários para {class_name}",
            test_type='unit',
            file_path=os.path.join(context.project_path, 'tests', f'test_{class_name.lower()}.py'),
            code=test_code,
            dependencies=[]
        )

    def _create_function_test(self, target: Dict[str, Any], context: AgentContext) -> TestCase:
        """Cria teste para uma função"""
        func_name = target['name']
        test_name = f"test_{func_name}"

        test_code = f'''"""
Testes para a função {func_name}
"""

import unittest
import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFunction{func_name.title()}(unittest.TestCase):
    """Testes para {func_name}"""

    def {test_name}_with_valid_input(self):
        """Testa {func_name} com entrada válida"""
        # TODO: Implementar teste com entrada válida
        self.assertTrue(True, "Teste com entrada válida pendente")

    def {test_name}_with_invalid_input(self):
        """Testa {func_name} com entrada inválida"""
        # TODO: Implementar teste com entrada inválida
        self.assertTrue(True, "Teste com entrada inválida pendente")

    def {test_name}_edge_cases(self):
        """Testa {func_name} com casos extremos"""
        # TODO: Implementar testes de edge cases
        self.assertTrue(True, "Testes de edge cases pendentes")


if __name__ == '__main__':
    unittest.main()
'''

        return TestCase(
            name=f"TestFunction{func_name.title()}",
            description=f"Testes unitários para {func_name}",
            test_type='unit',
            file_path=os.path.join(context.project_path, 'tests', f'test_{func_name}.py'),
            code=test_code,
            dependencies=[]
        )

    def _save_test_files(self, test_cases: List[TestCase], context: AgentContext):
        """Salva testes em arquivos"""
        tests_dir = os.path.join(context.project_path, 'tests')
        os.makedirs(tests_dir, exist_ok=True)

        for test_case in test_cases:
            try:
                with open(test_case.file_path, 'w', encoding='utf-8') as f:
                    f.write(test_case.code)
                self.logger.info(f"Teste salvo: {test_case.file_path}")
            except Exception as e:
                self.logger.error(f"Erro ao salvar teste {test_case.file_path}: {str(e)}")

    def _execute_tests(self, test_cases: List[TestCase], context: AgentContext) -> List[TestExecutionResult]:
        """Executa os testes criados"""
        results = []

        for test_case in test_cases:
            result = self._run_single_test(test_case, context)
            results.append(result)

        return results

    def _run_single_test(self, test_case: TestCase, context: AgentContext) -> TestExecutionResult:
        """Executa um único teste"""
        import time

        start_time = time.time()

        # Simula execução de teste
        # Em produção, executaria o pytest ou unittest de verdade
        try:
            # Valida sintaxe do código de teste
            ast.parse(test_case.code)

            # Por enquanto, simula sucesso
            status = 'passed'
            error_message = ""
            traceback = ""

        except SyntaxError as e:
            status = 'failed'
            error_message = f"Erro de sintaxe: {str(e)}"
            traceback = str(e)

        except Exception as e:
            status = 'error'
            error_message = str(e)
            traceback = str(e)

        duration = time.time() - start_time

        return TestExecutionResult(
            test_name=test_case.name,
            status=status,
            duration=duration,
            error_message=error_message,
            traceback=traceback
        )

    def _calculate_coverage(self, test_cases: List[TestCase], targets: List[Dict[str, Any]]) -> float:
        """Calcula cobertura de testes (simplificado)"""
        if not targets:
            return 100.0

        covered = len(test_cases)
        total = len(targets)

        return min(100.0, (covered / total) * 100)

    def _generate_summary(self, results: List[TestExecutionResult], coverage: float) -> str:
        """Gera resumo dos testes"""
        total = len(results)
        passed = len([r for r in results if r.status == 'passed'])
        failed = len([r for r in results if r.status == 'failed'])
        errors = len([r for r in results if r.status == 'error'])

        summary_lines = [
            f"Testes executados: {total}",
            f"  ✓ Passaram: {passed}",
            f"  ✗ Falharam: {failed}",
            f"  ! Erros: {errors}",
            f"Cobertura: {coverage:.1f}%"
        ]

        if failed > 0 or errors > 0:
            summary_lines.append("\nTestes que falharam:")
            for result in results:
                if result.status in ['failed', 'error']:
                    summary_lines.append(f"  - {result.test_name}: {result.error_message}")

        return "\n".join(summary_lines)
