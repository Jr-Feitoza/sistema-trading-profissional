"""
Exemplos de uso do sistema de agentes de IA
"""

import logging
from agents import (
    WorkflowOrchestrator,
    AgentType,
    PlannerAgent,
    DeveloperAgent,
    ReviewerAgent,
    TesterAgent,
    DocumenterAgent,
    AnalystAgent,
    AgentContext
)


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_full_development_workflow():
    """
    Exemplo 1: Workflow completo de desenvolvimento

    Executa todos os agentes em sequência:
    Planner -> Developer -> Reviewer -> Tester -> Documenter -> Analyst
    """
    print("\n" + "="*80)
    print("EXEMPLO 1: Workflow Completo de Desenvolvimento")
    print("="*80 + "\n")

    # Inicializa orquestrador
    orchestrator = WorkflowOrchestrator()

    # Executa workflow completo
    result = orchestrator.execute_workflow(
        task_description="Criar sistema de notificações para alertas de trading",
        project_path="/home/user/sistema-trading-profissional",
        workflow_type="full_development"
    )

    # Exibe resultados
    print(result.summary)
    print(f"\nSucesso: {result.success}")
    print(f"Duração: {result.total_duration:.2f}s")
    print(f"Passos concluídos: {', '.join(result.steps_completed)}")

    if result.steps_failed:
        print(f"Passos falhos: {', '.join(result.steps_failed)}")


def example_2_code_review_only():
    """
    Exemplo 2: Apenas revisão de código

    Executa apenas Reviewer e Analyst para revisar código existente
    """
    print("\n" + "="*80)
    print("EXEMPLO 2: Revisão de Código")
    print("="*80 + "\n")

    orchestrator = WorkflowOrchestrator()

    result = orchestrator.execute_workflow(
        task_description="Revisar qualidade do código existente",
        project_path="/home/user/sistema-trading-profissional",
        workflow_type="code_review"
    )

    print(result.summary)

    # Exibe detalhes da revisão
    if 'reviewer' in result.agent_results:
        review_result = result.agent_results['reviewer']
        print(f"\nQualidade do código: {review_result.output.quality_score:.1f}/100")
        print(f"Aprovado: {review_result.output.approved}")
        print(f"Issues encontradas: {len(review_result.output.issues)}")


def example_3_testing_workflow():
    """
    Exemplo 3: Workflow de testes

    Cria e executa testes automatizados
    """
    print("\n" + "="*80)
    print("EXEMPLO 3: Workflow de Testes")
    print("="*80 + "\n")

    orchestrator = WorkflowOrchestrator()

    result = orchestrator.execute_workflow(
        task_description="Criar e executar testes para estratégias de trading",
        project_path="/home/user/sistema-trading-profissional",
        workflow_type="testing_only"
    )

    print(result.summary)

    # Exibe resultados dos testes
    if 'tester' in result.agent_results:
        test_result = result.agent_results['tester']
        print(f"\nTestes criados: {len(test_result.output.tests_created)}")
        print(f"Testes executados: {test_result.output.total_tests}")
        print(f"Passaram: {test_result.output.passed}")
        print(f"Falharam: {test_result.output.failed}")
        print(f"Cobertura: {test_result.output.coverage:.1f}%")


def example_4_custom_workflow():
    """
    Exemplo 4: Workflow customizado

    Define uma sequência personalizada de agentes
    """
    print("\n" + "="*80)
    print("EXEMPLO 4: Workflow Customizado")
    print("="*80 + "\n")

    orchestrator = WorkflowOrchestrator()

    # Define sequência customizada: Planner -> Developer -> Tester
    custom_sequence = [
        AgentType.PLANNER,
        AgentType.DEVELOPER,
        AgentType.TESTER
    ]

    result = orchestrator.execute_custom_workflow(
        task_description="Adicionar validação de parâmetros nas estratégias",
        project_path="/home/user/sistema-trading-profissional",
        agent_sequence=custom_sequence
    )

    print(result.summary)


def example_5_individual_agents():
    """
    Exemplo 5: Usando agentes individualmente

    Executa agentes de forma independente
    """
    print("\n" + "="*80)
    print("EXEMPLO 5: Agentes Individuais")
    print("="*80 + "\n")

    # Cria contexto
    context = AgentContext(
        project_path="/home/user/sistema-trading-profissional",
        task_description="Analisar performance do sistema de trading"
    )

    # 1. Usar Planner Agent
    print("1. Executando Planner Agent...")
    planner = PlannerAgent()
    plan_result = planner.execute(context)

    if plan_result.is_success():
        plan = plan_result.output
        print(f"   ✓ Plano criado com {len(plan.tasks)} tarefas")
        print(f"   Tempo estimado: {plan.estimated_total_time}")
        print(f"   Riscos identificados: {len(plan.risks)}")

    # 2. Usar Analyst Agent
    print("\n2. Executando Analyst Agent...")
    analyst = AnalystAgent()
    analysis_result = analyst.execute(context)

    if analysis_result.is_success():
        analysis = analysis_result.output
        print(f"   ✓ Análise concluída")
        print(f"   Métricas coletadas: {len(analysis.metrics)}")
        print(f"   Insights gerados: {len(analysis.insights)}")
        print(f"   Relatório: {analysis.report_path}")

    # 3. Usar Documenter Agent
    print("\n3. Executando Documenter Agent...")
    documenter = DocumenterAgent()
    doc_result = documenter.execute(context)

    if doc_result.is_success():
        docs = doc_result.output
        print(f"   ✓ Documentação gerada")
        print(f"   Arquivos criados: {len(docs.files_created)}")
        print(f"   APIs documentadas: {len(docs.api_references)}")


def example_6_with_configuration():
    """
    Exemplo 6: Workflow com configuração customizada

    Passa configurações específicas para os agentes
    """
    print("\n" + "="*80)
    print("EXEMPLO 6: Workflow com Configuração")
    print("="*80 + "\n")

    # Configuração personalizada
    config = {
        'tester': {
            'save_tests': True,  # Salva testes em arquivos
            'run_coverage': True
        },
        'documenter': {
            'format': 'markdown',
            'include_diagrams': True
        },
        'reviewer': {
            'strict_mode': False,
            'auto_fix': False
        }
    }

    orchestrator = WorkflowOrchestrator(config=config)

    result = orchestrator.execute_workflow(
        task_description="Implementar cache para dados de mercado",
        project_path="/home/user/sistema-trading-profissional",
        workflow_type="full_development",
        context_metadata={
            'priority': 'high',
            'deadline': '2025-11-01',
            'author': 'Development Team'
        }
    )

    print(result.summary)


def example_7_error_handling():
    """
    Exemplo 7: Tratamento de erros

    Demonstra como o sistema lida com falhas
    """
    print("\n" + "="*80)
    print("EXEMPLO 7: Tratamento de Erros")
    print("="*80 + "\n")

    orchestrator = WorkflowOrchestrator()

    # Tenta executar em caminho inválido
    result = orchestrator.execute_workflow(
        task_description="Teste de tratamento de erros",
        project_path="/caminho/inexistente",
        workflow_type="analysis"
    )

    print(result.summary)
    print(f"\nSucesso: {result.success}")

    # Verifica erros
    for agent_name, agent_result in result.agent_results.items():
        if agent_result.errors:
            print(f"\nErros em {agent_name}:")
            for error in agent_result.errors:
                print(f"  - {error}")


def example_8_workflow_comparison():
    """
    Exemplo 8: Comparação de workflows

    Lista todos os workflows disponíveis
    """
    print("\n" + "="*80)
    print("EXEMPLO 8: Workflows Disponíveis")
    print("="*80 + "\n")

    orchestrator = WorkflowOrchestrator()

    workflows = orchestrator.list_available_workflows()

    print("Workflows disponíveis:\n")
    for workflow in workflows:
        print(f"  - {workflow}")

        # Mostra passos do workflow
        steps = orchestrator.create_workflow(workflow)
        agent_names = [step.agent_type.value for step in steps]
        print(f"    Agentes: {' -> '.join(agent_names)}")

    print("\nUse qualquer um destes workflows ou crie um customizado!")


def main():
    """Executa todos os exemplos"""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                   SISTEMA DE AGENTES DE IA - EXEMPLOS                        ║
║                                                                              ║
║  Este módulo demonstra como usar o sistema de agentes para automatizar      ║
║  tarefas de desenvolvimento, testes, revisão e análise.                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Executar exemplos
    try:
        example_8_workflow_comparison()  # Começar mostrando opções disponíveis

        # Perguntar ao usuário qual exemplo executar
        print("\n\nEscolha um exemplo para executar:")
        print("1 - Workflow Completo de Desenvolvimento")
        print("2 - Revisão de Código")
        print("3 - Workflow de Testes")
        print("4 - Workflow Customizado")
        print("5 - Agentes Individuais")
        print("6 - Workflow com Configuração")
        print("7 - Tratamento de Erros")
        print("0 - Executar todos os exemplos")

        choice = input("\nDigite o número (ou Enter para sair): ").strip()

        examples = {
            '1': example_1_full_development_workflow,
            '2': example_2_code_review_only,
            '3': example_3_testing_workflow,
            '4': example_4_custom_workflow,
            '5': example_5_individual_agents,
            '6': example_6_with_configuration,
            '7': example_7_error_handling,
        }

        if choice == '0':
            # Executar todos
            for example_func in examples.values():
                example_func()
                print("\n" + "-"*80 + "\n")
        elif choice in examples:
            examples[choice]()
        elif choice:
            print("Opção inválida!")

        print("\n\n✓ Exemplos concluídos!")

    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
    except Exception as e:
        print(f"\n\nErro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
