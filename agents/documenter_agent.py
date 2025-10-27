"""
Agente de Documentação - Gera documentação automática
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import os
import ast
import re
from datetime import datetime
from .base_agent import BaseAgent, AgentContext
from .agent_types import AgentType


@dataclass
class DocumentationSection:
    """Seção de documentação"""
    title: str
    content: str
    level: int  # 1 = #, 2 = ##, etc.
    subsections: List['DocumentationSection'] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class APIReference:
    """Referência de API"""
    name: str
    type: str  # 'class', 'function', 'method'
    signature: str
    docstring: str
    parameters: List[Dict[str, str]]
    returns: str
    examples: List[str]


@dataclass
class DocumentationResult:
    """Resultado da geração de documentação"""
    files_created: List[str]
    api_references: List[APIReference]
    sections: List[DocumentationSection]
    summary: str
    format: str  # 'markdown', 'rst', 'html'


class DocumenterAgent(BaseAgent):
    """
    Agente de Documentação

    Responsabilidades:
    - Gerar documentação de código
    - Criar READMEs
    - Documentar APIs
    - Criar guias de uso
    - Gerar diagramas (texto)
    - Manter documentação atualizada
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            agent_type=AgentType.DOCUMENTER,
            name="DocumenterAgent",
            description="Gera documentação completa do projeto",
            config=config
        )

    def _execute_logic(self, context: AgentContext) -> DocumentationResult:
        """
        Gera documentação completa

        Args:
            context: Contexto do projeto

        Returns:
            DocumentationResult com toda documentação gerada
        """
        self.logger.info("Iniciando geração de documentação...")

        # Analisa código para documentar
        code_analysis = self._analyze_code(context)

        # Gera referência de API
        api_references = self._generate_api_reference(code_analysis)

        # Cria seções de documentação
        sections = self._create_documentation_sections(context, code_analysis, api_references)

        # Gera arquivos de documentação
        files_created = self._generate_documentation_files(sections, context)

        # Gera resumo
        summary = self._generate_summary(files_created, api_references)

        result = DocumentationResult(
            files_created=files_created,
            api_references=api_references,
            sections=sections,
            summary=summary,
            format='markdown'
        )

        self.logger.info(f"Documentação gerada: {len(files_created)} arquivo(s)")
        return result

    def _analyze_code(self, context: AgentContext) -> Dict[str, Any]:
        """Analisa código para extrair informações"""
        analysis = {
            'classes': [],
            'functions': [],
            'modules': [],
            'dependencies': []
        }

        if os.path.exists(context.project_path):
            for root, dirs, files in os.walk(context.project_path):
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv']]

                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_analysis = self._analyze_python_file(file_path)

                        analysis['classes'].extend(file_analysis.get('classes', []))
                        analysis['functions'].extend(file_analysis.get('functions', []))
                        analysis['modules'].append({
                            'path': file_path,
                            'name': os.path.splitext(file)[0]
                        })

        return analysis

    def _analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analisa um arquivo Python"""
        analysis = {
            'classes': [],
            'functions': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or "Sem documentação",
                        'methods': [],
                        'file': file_path,
                        'line': node.lineno
                    }

                    # Extrai métodos
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append({
                                'name': item.name,
                                'docstring': ast.get_docstring(item) or "Sem documentação"
                            })

                    analysis['classes'].append(class_info)

                elif isinstance(node, ast.FunctionDef):
                    # Ignora métodos de classe (já foram processados)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        func_info = {
                            'name': node.name,
                            'docstring': ast.get_docstring(node) or "Sem documentação",
                            'file': file_path,
                            'line': node.lineno,
                            'args': [arg.arg for arg in node.args.args]
                        }
                        analysis['functions'].append(func_info)

        except Exception as e:
            self.logger.debug(f"Erro ao analisar {file_path}: {str(e)}")

        return analysis

    def _generate_api_reference(self, analysis: Dict[str, Any]) -> List[APIReference]:
        """Gera referência de API"""
        references = []

        # Documenta classes
        for class_info in analysis['classes']:
            ref = APIReference(
                name=class_info['name'],
                type='class',
                signature=f"class {class_info['name']}",
                docstring=class_info['docstring'],
                parameters=[],
                returns="",
                examples=[]
            )
            references.append(ref)

        # Documenta funções
        for func_info in analysis['functions']:
            args_str = ', '.join(func_info.get('args', []))
            ref = APIReference(
                name=func_info['name'],
                type='function',
                signature=f"def {func_info['name']}({args_str})",
                docstring=func_info['docstring'],
                parameters=[{'name': arg, 'type': 'Any', 'description': ''} for arg in func_info.get('args', [])],
                returns="Any",
                examples=[]
            )
            references.append(ref)

        return references

    def _create_documentation_sections(
        self,
        context: AgentContext,
        analysis: Dict[str, Any],
        api_references: List[APIReference]
    ) -> List[DocumentationSection]:
        """Cria seções de documentação"""
        sections = []

        # Seção: Visão Geral
        overview = DocumentationSection(
            title="Visão Geral",
            content=self._generate_overview(context, analysis),
            level=1
        )
        sections.append(overview)

        # Seção: Instalação
        installation = DocumentationSection(
            title="Instalação",
            content=self._generate_installation_guide(context),
            level=1
        )
        sections.append(installation)

        # Seção: Uso Rápido
        quickstart = DocumentationSection(
            title="Uso Rápido",
            content=self._generate_quickstart(context, analysis),
            level=1
        )
        sections.append(quickstart)

        # Seção: API Reference
        api_section = DocumentationSection(
            title="Referência da API",
            content=self._generate_api_documentation(api_references),
            level=1
        )
        sections.append(api_section)

        # Seção: Arquitetura
        architecture = DocumentationSection(
            title="Arquitetura",
            content=self._generate_architecture_doc(analysis),
            level=1
        )
        sections.append(architecture)

        return sections

    def _generate_overview(self, context: AgentContext, analysis: Dict[str, Any]) -> str:
        """Gera visão geral do projeto"""
        project_name = os.path.basename(context.project_path)

        overview = f"""
# {project_name}

{context.task_description}

## Estatísticas do Projeto

- Classes: {len(analysis['classes'])}
- Funções: {len(analysis['functions'])}
- Módulos: {len(analysis['modules'])}

## Características Principais

- Sistema modular e extensível
- Arquitetura orientada a objetos
- Testes automatizados
- Documentação completa
"""
        return overview.strip()

    def _generate_installation_guide(self, context: AgentContext) -> str:
        """Gera guia de instalação"""
        guide = """
## Requisitos

- Python 3.8+
- pip

## Instalação

```bash
# Clone o repositório
git clone <repository-url>

# Entre no diretório
cd """ + os.path.basename(context.project_path) + """

# Instale dependências
pip install -r requirements.txt
```
"""
        return guide.strip()

    def _generate_quickstart(self, context: AgentContext, analysis: Dict[str, Any]) -> str:
        """Gera guia de início rápido"""
        quickstart = """
## Exemplo Básico

```python
# Importe as classes necessárias
from main import Main

# Inicialize o sistema
system = Main()

# Execute a funcionalidade principal
result = system.run()
print(result)
```

## Próximos Passos

- Consulte a [Referência da API](#referência-da-api) para detalhes completos
- Veja exemplos em `examples/`
- Leia a documentação de arquitetura
"""
        return quickstart.strip()

    def _generate_api_documentation(self, api_references: List[APIReference]) -> str:
        """Gera documentação da API"""
        doc_parts = []

        # Agrupa por tipo
        classes = [r for r in api_references if r.type == 'class']
        functions = [r for r in api_references if r.type == 'function']

        if classes:
            doc_parts.append("## Classes\n")
            for ref in classes:
                doc_parts.append(f"### {ref.name}\n")
                doc_parts.append(f"```python\n{ref.signature}\n```\n")
                doc_parts.append(f"{ref.docstring}\n")

        if functions:
            doc_parts.append("## Funções\n")
            for ref in functions:
                doc_parts.append(f"### {ref.name}\n")
                doc_parts.append(f"```python\n{ref.signature}\n```\n")
                doc_parts.append(f"{ref.docstring}\n")

                if ref.parameters:
                    doc_parts.append("**Parâmetros:**\n")
                    for param in ref.parameters:
                        doc_parts.append(f"- `{param['name']}`: {param.get('description', 'N/A')}\n")

                if ref.returns:
                    doc_parts.append(f"\n**Retorna:** {ref.returns}\n")

        return "\n".join(doc_parts)

    def _generate_architecture_doc(self, analysis: Dict[str, Any]) -> str:
        """Gera documentação de arquitetura"""
        doc = """
## Estrutura do Projeto

```
project/
├── agents/          # Sistema de agentes de IA
├── connectors/      # Conectores externos
├── engine/          # Engine principal
├── indicators/      # Indicadores
├── strategies/      # Estratégias
├── tests/           # Testes automatizados
└── utils/           # Utilitários
```

## Componentes Principais

"""

        # Lista módulos principais
        for module in analysis['modules'][:10]:
            module_name = module['name']
            doc += f"- **{module_name}**: Módulo responsável por...\n"

        return doc.strip()

    def _generate_documentation_files(self, sections: List[DocumentationSection], context: AgentContext) -> List[str]:
        """Gera arquivos de documentação"""
        files_created = []

        # Gera README.md principal
        readme_path = os.path.join(context.project_path, 'docs', 'AI_AGENTS_README.md')
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)

        readme_content = self._compile_sections_to_markdown(sections)

        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            files_created.append(readme_path)
        except Exception as e:
            self.logger.error(f"Erro ao criar README: {str(e)}")

        return files_created

    def _compile_sections_to_markdown(self, sections: List[DocumentationSection]) -> str:
        """Compila seções em markdown"""
        markdown_parts = []

        # Header
        markdown_parts.append("# Documentação do Projeto\n")
        markdown_parts.append(f"*Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        markdown_parts.append("---\n")

        # Conteúdo das seções
        for section in sections:
            markdown_parts.append(section.content)
            markdown_parts.append("\n---\n")

        return "\n".join(markdown_parts)

    def _generate_summary(self, files_created: List[str], api_references: List[APIReference]) -> str:
        """Gera resumo da documentação"""
        summary = f"""
Documentação gerada com sucesso!

Arquivos criados: {len(files_created)}
APIs documentadas: {len(api_references)}

Arquivos:
"""
        for file in files_created:
            summary += f"  - {file}\n"

        return summary.strip()
