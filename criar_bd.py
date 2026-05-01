import sqlite3

# 1. Conecta ao banco (cria o arquivo se não existir) e ativa chaves estrangeiras
conn = sqlite3.connect("bulas.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# 2. Criação das Tabelas
cursor.execute("""
CREATE TABLE IF NOT EXISTS medicamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    laboratorio TEXT NOT NULL,
    indicacao TEXT,
    bula_pdf TEXT NOT NULL,
    resumo TEXT,
    UNIQUE(nome, laboratorio)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    medicamento_id INTEGER NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY(medicamento_id) REFERENCES medicamentos(id),
    UNIQUE(usuario_id, medicamento_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS nomes_comerciais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicamento_id INTEGER NOT NULL,
    nome_comercial TEXT NOT NULL,
    FOREIGN KEY(medicamento_id) REFERENCES medicamentos(id),
    UNIQUE(medicamento_id, nome_comercial)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS informacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicamento_id INTEGER NOT NULL,
    detalhes TEXT NOT NULL,
    FOREIGN KEY(medicamento_id) REFERENCES medicamentos(id),
    UNIQUE(medicamento_id)
)
""")

# 3. Inserção dos 10 medicamentos principais
medicamentos = [
    ("Losartana Potássica", "EMS", "Hipertensão",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=102350810",
     "Indicado para hipertensão; contraindicado em gravidez; pode causar tontura."),
    ("Dipirona Sódica", "Sanofi (Novalgina) / Neo Química", "Dor e febre",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=183260110",
     "Indicado para dor e febre; contraindicado em alergia a pirazolonas; pode causar reações alérgicas."),
    ("Metformina", "EMS / Medley", "Diabetes tipo 2",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=102350659",
     "Indicado para diabetes tipo 2; contraindicado em insuficiência renal; pode causar desconforto gastrointestinal."),
    ("Omeprazol", "Neo Química / Medley", "Problemas gástricos",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=183260248",
     "Indicado para refluxo e úlceras; contraindicado em alergia a benzimidazóis; pode causar dor de cabeça."),
    ("Sinvastatina", "EMS", "Colesterol alto",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=102350487",
     "Indicado para hipercolesterolemia; contraindicado em doença hepática ativa; pode causar dor muscular."),
    ("Paracetamol", "EMS / Sanofi", "Dor e febre",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=102350764",
     "Indicado para dor e febre; contraindicado em insuficiência hepática grave; pode causar lesão hepática em altas doses."),
    ("Ibuprofeno", "Medley", "Dor e inflamação",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=183260484",
     "Indicado para dor e inflamação; contraindicado em úlcera ativa; pode causar irritação gástrica."),
    ("Amoxicilina", "EMS / Medley", "Infecções bacterianas",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=102350665",
     "Indicado para infecções bacterianas; contraindicado em alergia a penicilinas; pode causar diarreia."),
    ("Clonazepam", "Blanver (Rivotril) / Genéricos", "Ansiedade e epilepsia",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=115240011",
     "Indicado para ansiedade e epilepsia; contraindicado em insuficiência respiratória grave; pode causar sonolência."),
    ("Sertralina", "Viatris (Zoloft) / Genéricos", "Depressão e ansiedade",
     "https://consultas.anvisa.gov.br/#/bulario/q/?numeroRegistro=188300078",
     "Indicado para depressão e ansiedade; contraindicado em uso concomitante com IMAO; pode causar náusea.")
]

for med in medicamentos:
    cursor.execute("""
        INSERT OR IGNORE INTO medicamentos (nome, laboratorio, indicacao, bula_pdf, resumo)
        VALUES (?, ?, ?, ?, ?)
    """, med)

# 4. Inserção de Nomes Comerciais
nomes_comerciais_dict = {
    "Losartana Potássica": ["Aradois", "Cozaar", "Losar"],
    "Dipirona Sódica": ["Novalgina", "Anador", "Magnopyrol"],
    "Metformina": ["Glifage", "Dimefor", "Metfor"],
    "Omeprazol": ["Losec", "Gastrozol", "Peprazol"],
    "Sinvastatina": ["Zocor", "Sinvex", "Vastatina"],
    "Paracetamol": ["Tylenol", "Paracet", "Pacemol"],
    "Ibuprofeno": ["Alivium", "Ibupril", "Brufen"],
    "Amoxicilina": ["Amoxil", "Velamox", "Moxilin"],
    "Clonazepam": ["Rivotril", "Clonotril", "Clopam"],
    "Sertralina": ["Zoloft", "Serenata", "Sertralin"]
}

for nome, comerciais in nomes_comerciais_dict.items():
    cursor.execute("SELECT id FROM medicamentos WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()
    if resultado:
        med_id = resultado[0]
        for nc in comerciais:
            cursor.execute("""
                INSERT OR IGNORE INTO nomes_comerciais (medicamento_id, nome_comercial)
                VALUES (?, ?)
            """, (med_id, nc))

# 5. Inserção de Informações Detalhadas
informacoes_detalhadas = {
    "Losartana Potássica": "Indicado para hipertensão arterial. Contraindicado em gravidez. Pode causar tontura.",
    "Dipirona Sódica": "Indicado para dor e febre. Contraindicado em alergia a pirazolonas. Risco de agranulocitose.",
    "Metformina": "Indicado para diabetes tipo 2. Tomar preferencialmente com as refeições.",
    "Omeprazol": "Indicado para problemas gástricos. Tomar em jejum, pela manhã.",
    "Sinvastatina": "Indicado para colesterol alto. Tomar preferencialmente à noite.",
    "Paracetamol": "Indicado para dor e febre. Não exceder a dose diária por risco hepático.",
    "Ibuprofeno": "Anti-inflamatório. Evitar em caso de suspeita de dengue ou úlceras gástricas.",
    "Amoxicilina": "Antibiótico. Requer receita controlada. Finalizar o ciclo completo do tratamento.",
    "Clonazepam": "Benzodiazepínico para ansiedade. Pode causar dependência e sonolência severa.",
    "Sertralina": "Antidepressivo. O efeito terapêutico completo pode levar algumas semanas."
}

for nome, detalhe in informacoes_detalhadas.items():
    cursor.execute("SELECT id FROM medicamentos WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()
    if resultado:
        med_id = resultado[0]
        cursor.execute("""
            INSERT OR IGNORE INTO informacoes (medicamento_id, detalhes)
            VALUES (?, ?)
        """, (med_id, detalhe))

# 6. Salva as alterações e fecha a conexão
conn.commit()
conn.close()

print("Banco de dados 'bulas.db' criado com sucesso!")