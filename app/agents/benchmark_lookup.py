def lookup_industry_benchmark(naics_code: str):
    """
    Simula uma busca na BLS API para obter benchmarks de Revenue per Employee por setor.
    Para v1.0 sem chave de API do BLS, retornamos um dado sintético.
    """
    benchmarks = {
        "541511": 250000.0, # Custom Computer Programming
        "541211": 180000.0, # Offices of Certified Public Accountants
        "default": 150000.0
    }
    return benchmarks.get(naics_code, benchmarks["default"])
