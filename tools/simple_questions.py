"""Responde perguntas simples sem precisar de LLM."""
import re
from datetime import datetime
from typing import Optional

# Coordenadas padrão (São Paulo) para clima
DEFAULT_LAT = -23.5505
DEFAULT_LON = -46.6333


def _normalize(msg: str) -> str:
    """Normaliza a mensagem para comparação."""
    return msg.lower().strip()


def _match_keywords(msg: str, keywords: list[str]) -> bool:
    """Verifica se a mensagem contém alguma das palavras-chave."""
    n = _normalize(msg)
    return any(kw in n for kw in keywords)


def get_current_datetime() -> str:
    """Retorna data e hora atual formatadas."""
    now = datetime.now()
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    dia_semana = dias[now.weekday()]
    mes = meses[now.month - 1]
    return f"Hoje é {dia_semana}, {now.day} de {mes} de {now.year}. São {now.hour:02d}:{now.minute:02d}."


def get_weather(cidade: Optional[str] = None) -> str:
    """Obtém temperatura e previsão via Open-Meteo (gratuito, sem API key)."""
    try:
        import urllib.request
        import json

        lat, lon = DEFAULT_LAT, DEFAULT_LON
        if cidade:
            # Geocoding para obter coordenadas
            city_clean = cidade.replace(" ", "%20")
            url_geo = f"https://geocoding-api.open-meteo.com/v1/search?name={city_clean}&count=1"
            with urllib.request.urlopen(url_geo, timeout=5) as r:
                geo = json.loads(r.read())
            if geo.get("results"):
                lat = geo["results"][0]["latitude"]
                lon = geo["results"][0]["longitude"]
                cidade = geo["results"][0].get("name", cidade)

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,precipitation&hourly=temperature_2m&forecast_days=2"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())

        current = data.get("current", {})
        temp = current.get("temperature_2m")
        code = current.get("weather_code", 0)
        prec = current.get("precipitation", 0)

        # Descrição do tempo baseada no código WMO
        descricoes = {
            0: "céu limpo", 1: "predominantemente limpo", 2: "parcialmente nublado",
            3: "nublado", 45: "neblina", 48: "neblina", 51: "garoa leve",
            53: "garoa", 55: "garoa intensa", 61: "chuva leve", 63: "chuva",
            65: "chuva forte", 80: "pancadas de chuva", 81: "pancadas de chuva",
            82: "pancadas fortes", 95: "trovoada", 96: "trovoada com granizo",
        }
        desc = descricoes.get(code, "variável")

        loc = f" em {cidade}" if cidade else " (São Paulo)"
        return f"Temperatura{loc}: {temp}°C. Previsão: {desc}. Chuva: {prec} mm."
    except Exception as e:
        return f"Não foi possível obter a previsão: {e}"


def get_news(web_tool) -> str:
    """Busca notícias via pesquisa web."""
    if not web_tool:
        return "Pesquisa não disponível."
    return web_tool.search("notícias hoje Brasil", max_results=5)


def answer_simple_question(message: str, web_tool=None) -> Optional[str]:
    """
    Tenta responder perguntas simples. Retorna a resposta ou None se não reconhecer.
    """
    msg = _normalize(message)

    # Data / dia / hora
    if _match_keywords(msg, ["que dia", "qual dia", "data de hoje", "que data", "dia é hoje", "dia hoje", "qual a data", "que dia e hoje"]):
        return get_current_datetime()

    if _match_keywords(msg, ["que horas", "qual hora", "horário", "que horário", "horas são", "que horas são", "que horas sao"]):
        now = datetime.now()
        return f"São {now.hour:02d}:{now.minute:02d}."

    # Clima / temperatura / previsão
    if _match_keywords(msg, ["temperatura", "clima", "previsão", "previsao", "tempo", "faz calor", "faz frio", "como está o tempo", "vai chover", "chover", "previsão do tempo"]):
        # Tentar extrair cidade
        cidade = None
        for c in ["em ", "de ", "em ", "na ", "no "]:
            m = re.search(rf"{c}(\w+(?:\s+\w+)?)", msg, re.I)
            if m:
                cidade = m.group(1).strip()
                break
        return get_weather(cidade)

    # Notícias
    if _match_keywords(msg, ["notícias", "noticias", "notícia", "últimas notícias", "ultimas noticias", "quais as notícias", "quais noticias"]):
        return get_news(web_tool)

    return None
