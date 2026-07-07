from crewai import Agent, Task, Crew, Process
from app.config import settings

# Placeholder tools that wrap our local functions if needed
def orchestrate_end_of_month():
    """
    Usa CrewAI para orquestrar o pipeline de fechamento mensal.
    O Productivity Tracker roda primeiro, depois Labor Forecaster, ROI e Burnout.
    """
    if not settings.openai_api_key and not settings.anthropic_api_key:
        print("Aviso: Chaves LLM não configuradas. Orquestrador CrewAI usando mock / skipping LLM tasks.")
        
    # Agent 1: Workforce Analyst
    workforce_analyst = Agent(
        role="Workforce Financial Analyst",
        goal="Analisar a receita por colaborador, projetar os custos e rankear a performance (ROI).",
        backstory="Um especialista financeiro que extrai métricas do SQLite e cruza com a receita real.",
        verbose=True,
        allow_delegation=False
    )
    
    # Agent 2: HR Health Monitor
    hr_monitor = Agent(
        role="HR Health Monitor",
        goal="Analisar NLP de logs para detectar burnout e sugerir escalas ideais para evitar fadiga.",
        backstory="Especialista em bem-estar ocupacional usando NLP e Otimização Linear.",
        verbose=True,
        allow_delegation=False
    )
    
    # Tasks (Neste exemplo, apenas definimos a estrutura abstrata da Crew.
    # Em produção, essas tasks utilizariam 'tools' que apontam para as funcões:
    # calculate_roi_and_revenue, forecast_labor_costs, etc.)
    
    t1 = Task(
        description="Executar o productivity tracker e atualizar o db com as métricas do mês.",
        agent=workforce_analyst,
        expected_output="Relatório de ROI salvo no banco."
    )
    
    t2 = Task(
        description="Avaliar os logs de trabalho para detecção de exaustão usando Sentence-BERT.",
        agent=hr_monitor,
        expected_output="Lista de alertas de burnout (se houver) salva no banco."
    )
    
    crew = Crew(
        agents=[workforce_analyst, hr_monitor],
        tasks=[t1, t2],
        process=Process.sequential
    )
    
    # return crew.kickoff() 
    # Comentado para evitar falha se a API_KEY for invalida na demo.
    return {"status": "success", "message": "Orquestração concluída (mocked)."}
