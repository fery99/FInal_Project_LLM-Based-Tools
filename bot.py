
from langchain.agents import agent_types, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Replicate
from langchain_core.tools import tool

import requests
from dotenv import load_dotenv
import os

def parse_input(input_str):
    parts = input_str.split(";")
    return dict(part.split("=") for part in parts)


# ============================
#        TOOLS
# ============================

@tool
def cek_harga_mobil(input: str) -> str:
    """
    Cek harga mobil berdasarkan model.
    Input format: 'model=Avanza'
    """
    try:
        model = parse_input(input)["model"].lower()
        database = {
            "avanza": 250_000_000,
            "agya": 180_000_000,
            "fortuner": 575_000_000,
            "pajero": 600_000_000,
            "civic": 520_000_000
        }

        if model in database:
            return f"Harga {model.capitalize()} adalah Rp {database[model]:,}"
        else:
            return "Model tidak ditemukan di database harga."
    except Exception as e:
        return f"Error cek harga: {e}"


@tool
def cek_stok_mobil(input: str) -> str:
    """
    Mengecek stok mobil berdasarkan model.
    Input format: 'model=Avanza'
    """
    try:
        model = parse_input(input)["model"].lower()
        stok = {
            "avanza": 5,
            "agya": 12,
            "fortuner": 3,
            "pajero": 2,
            "civic": 4
        }

        if model in stok:
            jumlah = stok[model]
            return f"Stok {model.capitalize()} tersedia: {jumlah} unit."
        else:
            return "Model tidak ditemukan di database stok."
    except Exception as e:
        return f"Error cek stok: {e}"


@tool
def hitung_cicilan(input: str) -> str:
    """
    Hitung cicilan mobil.
    Input format: 'harga=250000000;dp=50000000;tenor=60'
    """
    try:
        data = parse_input(input)
        harga = float(data["harga"])
        dp = float(data["dp"])
        tenor = int(data["tenor"])

        pokok = harga - dp
        bunga = 0.07  # 7% per tahun rata-rata
        cicilan_bulanan = (pokok * (1 + bunga)) / tenor

        return f"Cicilan per bulan: Rp {cicilan_bulanan:,.0f}"
    except Exception as e:
        return f"Error hitung cicilan: {e}"


@tool
def lokasi_dealer(input: str) -> str:
    """
    Mendapatkan dealer mobil terdekat.
    Input format: 'kota=Jakarta'
    """
    try:
        kota = parse_input(input)["kota"].capitalize()

        dealer = {
            "Jakarta": "Toyota Astrido Sunter, Jakarta Utara",
            "Bandung": "Toyota Auto2000 Soekarno-Hatta",
            "Surabaya": "Auto2000 Kenjeran",
            "Medan": "Agung Toyota Medan Krakatau",
        }

        if kota in dealer:
            return f"Dealer terdekat di {kota}: {dealer[kota]}"
        else:
            return "Dealer untuk kota tersebut tidak ditemukan."
    except Exception as e:
        return f"Error cari dealer: {e}"


# ============================
#        BUILD AGENT
# ============================

def build_agent():
    load_dotenv()

    llm = Replicate(model="anthropic/claude-3.5-sonnet")

    system_message = """
    Kamu adalah BOT PELAYANAN PEMBELIAN MOBIL.
    Gaya bahasa: formal, sopan, profesional.
    Tugas:
    - Memberikan informasi mobil, harga, stok, dealer, dan cicilan.
    - Menggunakan tool jika diperlukan.
    - Berbicara seperti sales marketing berpengalaman.

    Jangan mengada-ada. Jika tidak tahu, gunakan tool.
    """

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    tools = [
        cek_harga_mobil,
        cek_stok_mobil,
        hitung_cicilan,
        lokasi_dealer
    ]

    agent_executor = initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={"system_message": system_message},
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True
    )

    return agent_executor
