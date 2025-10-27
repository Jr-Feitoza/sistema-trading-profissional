# Sistema de Agentes de IA

Sistema completo de agentes de IA para automatizar tarefas de desenvolvimento, testes, revisão de código, documentação e análise.

## Visão Geral

Este sistema implementa uma arquitetura de múltiplos agentes especializados que trabalham em conjunto para executar workflows de desenvolvimento de software. Cada agente tem responsabilidades específicas e pode ser usado individualmente ou como parte de um workflow orquestrado.

## Agentes Disponíveis

### 1. Planner Agent (Planejador)
**Responsabilidades:**
- Analisar requisitos e criar planos de execução
- Quebrar tarefas complexas em subtarefas
- Estimar esforço e tempo
- Identificar dependências
- Definir ordem de execução
- Identificar riscos potenciais

**Exemplo de uso:**
```python
from agents import PlannerAgent, AgentContext

planner = PlannerAgent()
context = AgentContext(
    project_path="/caminho/projeto",
    task_description="Implementar sistema de cache"
)
result = planner.execute(context)
plan = result.output  # ExecutionPlan com todas as tarefas
```

### 2. Developer Agent (Desenvolvedor)
**Responsabilidades:**
- Implementar novas features
- Corrigir bugs
- Refatorar código
- Seguir padrões de código
- Escrever código limpo e manutenível
- Integrar com código existente

**Exemplo de uso:**
```python
from agents import DeveloperAgent, AgentContext

developer = DeveloperAgent()
result = developer.execute(context)
development = result.output  # DevelopmentResult com mudanças de código
```

### 3. Reviewer Agent (Revisor)
**Responsabilidades:**
- Revisar qualidade do código
- Identificar bugs potenciais
- Verificar padrões de código
- Analisar segurança
- Sugerir melhorias
- Calcular métricas de qualidade

**Exemplo de uso:**
```python
from agents import ReviewerAgent, AgentContext

reviewer = ReviewerAgent()
result = reviewer.execute(context)
review = result.output  # ReviewResult com issues e métricas
print(f"Quality Score: {review.quality_score}/100")
print(f"Approved: {review.approved}")
```

### 4. Tester Agent (Testador)
**Responsabilidades:**
- Criar testes unitários
- Criar testes de integração
- Executar suíte de testes
- Gerar relatórios de cobertura
- Identificar edge cases
- Sugerir testes adicionais

**Exemplo de uso:**
```python
from agents import TesterAgent, AgentContext

tester = TesterAgent(config={'save_tests': True})
result = tester.execute(context)
tests = result.output  # TestResult com testes criados e executados
print(f"Coverage: {tests.coverage}%")
```

### 5. Documenter Agent (Documentador)
**Responsabilidades:**
- Gerar documentação de código
- Criar READMEs
- Documentar APIs
- Criar guias de uso
- Gerar diagramas (texto)
- Manter documentação atualizada

**Exemplo de uso:**
```python
from agents import DocumenterAgent, AgentContext

documenter = DocumenterAgent()
result = documenter.execute(context)
docs = result.output  # DocumentationResult
print(f"Files created: {docs.files_created}")
```

### 6. Analyst Agent (Analista)
**Responsabilidades:**
- Analisar performance do sistema
- Calcular métricas de qualidade
- Identificar tendências
- Gerar insights acionáveis
- Criar relatórios
- Monitorar KPIs

**Exemplo de uso:**
```python
from agents import AnalystAgent, AgentContext

analyst = AnalystAgent()
result = analyst.execute(context)
analysis = result.output  # AnalysisResult
print(f"Metrics: {len(analysis.metrics)}")
print(f"Insights: {len(analysis.insights)}")
```

## Workflow Orchestrator

O `WorkflowOrchestrator` coordena a execução de múltiplos agentes em sequência, gerenciando dependências e passando contexto entre eles.

### Workflows Pré-definidos

#### 1. Full Development
Workflow completo de desenvolvimento:
```
Planner → Developer → Reviewer → Tester → Documenter → Analyst
```

```python
from agents import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
result = orchestrator.execute_workflow(
    task_description="Implementar feature X",
    project_path="/caminho/projeto",
    workflow_type="full_development"
)
```

#### 2. Code Review
Apenas revisão de código:
```
Reviewer → Analyst
```

```python
result = orchestrator.execute_workflow(
    task_description="Revisar código",
    project_path="/caminho/projeto",
    workflow_type="code_review"
)
```

#### 3. Testing Only
Apenas testes:
```
Tester → Analyst
```

```python
result = orchestrator.execute_workflow(
    task_description="Criar testes",
    project_path="/caminho/projeto",
    workflow_type="testing_only"
)
```

#### 4. Documentation
Apenas documentação:
```
Documenter
```

#### 5. Analysis
Apenas análise:
```
Analyst
```

#### 6. Quick Fix
Correção rápida:
```
Developer → Tester
```

### Workflow Customizado

Você pode criar workflows personalizados:

```python
from agents import WorkflowOrchestrator, AgentType

orchestrator = WorkflowOrchestrator()

# Define sequência customizada
custom_sequence = [
    AgentType.PLANNER,
    AgentType.DEVELOPER,
    AgentType.REVIEWER
]

result = orchestrator.execute_custom_workflow(
    task_description="Minha tarefa",
    project_path="/caminho/projeto",
    agent_sequence=custom_sequence
)
```

## Configuração

Cada agente pode ser configurado individualmente:

```python
config = {
    'tester': {
        'save_tests': True,
        'run_coverage': True
    },
    'documenter': {
        'format': 'markdown',
        'include_diagrams': True
    },
    'reviewer': {
        'strict_mode': False
    }
}

orchestrator = WorkflowOrchestrator(config=config)
```

## Arquitetura

### Classes Base

- **BaseAgent**: Classe abstrata base para todos os agentes
- **AgentContext**: Contexto compartilhado entre agentes
- **AgentResult**: Resultado da execução de um agente

### Tipos

- **AgentType**: Enum com tipos de agentes
- **AgentStatus**: Status do agente durante execução
- **TaskPriority**: Prioridade de tarefas
- **WorkflowStage**: Estágios do workflow

### Fluxo de Dados

```
Context (entrada)
    ↓
Agent.execute()
    ↓
Agent._execute_logic()  [implementação específica]
    ↓
AgentResult (saída)
    ↓
Context.shared_data (próximo agente)
```

## Exemplos Práticos

Execute o arquivo `examples.py` para ver exemplos práticos:

```bash
python agents/examples.py
```

Exemplos incluídos:
1. Workflow completo de desenvolvimento
2. Revisão de código
3. Workflow de testes
4. Workflow customizado
5. Agentes individuais
6. Configuração personalizada
7. Tratamento de erros
8. Comparação de workflows

## Integração com Claude Code

Este sistema foi desenvolvido para trabalhar em conjunto com o Claude Code. Você pode:

1. **Usar agentes para planejar** antes de implementar
2. **Revisar código automaticamente** após mudanças
3. **Gerar testes** para novo código
4. **Documentar automaticamente** após desenvolvimento
5. **Analisar qualidade** continuamente

### Exemplo de Integração

```python
# 1. Planejar tarefa
planner = PlannerAgent()
plan = planner.execute(context).output

# 2. Claude Code implementa baseado no plano
# (implementação manual ou via Claude)

# 3. Revisar código automaticamente
reviewer = ReviewerAgent()
review = reviewer.execute(context).output

if not review.approved:
    print("Código precisa de melhorias:")
    for issue in review.issues:
        print(f"  - {issue.description}")

# 4. Gerar testes
tester = TesterAgent()
tests = tester.execute(context).output

# 5. Documentar
documenter = DocumenterAgent()
docs = documenter.execute(context).output

# 6. Analisar
analyst = AnalystAgent()
analysis = analyst.execute(context).output
```

## Estrutura de Arquivos

```
agents/
├── __init__.py                 # Exporta todos os componentes
├── agent_types.py             # Enums e tipos
├── base_agent.py              # Classe base dos agentes
├── planner_agent.py           # Agente planejador
├── developer_agent.py         # Agente desenvolvedor
├── reviewer_agent.py          # Agente revisor
├── tester_agent.py            # Agente testador
├── documenter_agent.py        # Agente documentador
├── analyst_agent.py           # Agente analista
├── workflow_orchestrator.py   # Orquestrador de workflows
├── examples.py                # Exemplos de uso
└── README.md                  # Esta documentação
```

## Extensibilidade

### Criar Novo Agente

Para criar um novo agente:

```python
from agents.base_agent import BaseAgent, AgentContext
from agents.agent_types import AgentType

class MyCustomAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(
            agent_type=AgentType.CUSTOM,  # Adicionar ao enum
            name="MyCustomAgent",
            description="Descrição do agente",
            config=config
        )

    def _execute_logic(self, context: AgentContext):
        # Implementar lógica específica
        result = self._do_something(context)
        return result
```

### Criar Novo Workflow

```python
def _create_custom_workflow(self) -> List[WorkflowStep]:
    return [
        WorkflowStep(
            agent_type=AgentType.AGENT1,
            agent=self.agents[AgentType.AGENT1],
            depends_on=[]
        ),
        WorkflowStep(
            agent_type=AgentType.AGENT2,
            agent=self.agents[AgentType.AGENT2],
            depends_on=[AgentType.AGENT1.value]
        )
    ]
```

## Melhores Práticas

1. **Sempre use contexto compartilhado** para passar dados entre agentes
2. **Valide entradas** antes da execução
3. **Trate erros apropriadamente** em agentes opcionais
4. **Use logging** para debug e monitoramento
5. **Configure agentes** conforme necessidade do projeto
6. **Teste workflows** antes de usar em produção

## Roadmap

Funcionalidades planejadas:
- [ ] Agente de Deploy
- [ ] Agente de Monitoramento
- [ ] Agente de Otimização de Performance
- [ ] Interface Web para visualização
- [ ] Integração com CI/CD
- [ ] Métricas em tempo real
- [ ] Machine Learning para melhorar decisões

## Contribuindo

Para contribuir:
1. Crie novos agentes seguindo o padrão
2. Adicione testes para novos componentes
3. Documente novos workflows
4. Atualize exemplos

## Licença

Este código faz parte do sistema de trading profissional.

---

**Desenvolvido com Claude Code** 🤖
