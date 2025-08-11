"""
Base de Conhecimento de Culturas para Portugal
"""

CULTURAS_PORTUGAL = {
    # HORTÍCOLAS
    "tomate": {
        "nome": "Tomate",
        "categoria": "Hortícola",
        "tipo": "Fruto",
        "epoca_plantio": ["Março", "Abril", "Maio"],
        "tempo_crescimento": 90,  # dias
        "area_minima": 1,  # m²
        "custo_estimado_m2": 5.0,  # euros
        "rendimento_m2": 15,  # kg
        "dificuldade": "Média",
        "clima_ideal": "Temperado",
        "rega_frequencia": "Diária",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Necessita de suporte para trepar. Sensível a geadas.",
        "pragas_comuns": ["Míldio", "Traça do tomateiro", "Afídeos"],
        "usos_culinarios": ["Saladas", "Molhos", "Conservas", "Sopas"],
        "usos_medicinais": ["Antioxidante", "Rico em licopeno", "Vitamina C"],
        "compatibilidade": ["Manjericão", "Salsa", "Cebolinho"],
        "propagacao": "Semente",
        "icon": "🍅"
    },
    
    "alface": {
        "nome": "Alface",
        "categoria": "Hortícola",
        "tipo": "Folha",
        "epoca_plantio": ["Fevereiro", "Março", "Setembro", "Outubro"],
        "tempo_crescimento": 45,
        "area_minima": 0.5,
        "custo_estimado_m2": 2.0,
        "rendimento_m2": 8,
        "dificuldade": "Fácil",
        "clima_ideal": "Fresco",
        "rega_frequencia": "Dia sim, dia não",
        "sol_horas_min": 4,
        "solo_ph": [6.0, 7.5],
        "observacoes": "Cresce rapidamente. Ideal para iniciantes.",
        "pragas_comuns": ["Lesmas", "Caracóis", "Afídeos"],
        "usos_culinarios": ["Saladas", "Wraps", "Sanduíches"],
        "usos_medicinais": ["Digestivo", "Calmante", "Rico em folatos"],
        "compatibilidade": ["Cenoura", "Rabanete", "Cebola"],
        "propagacao": "Semente",
        "icon": "🥬"
    },
    
    "cenoura": {
        "nome": "Cenoura",
        "categoria": "Hortícola",
        "tipo": "Raiz",
        "epoca_plantio": ["Março", "Abril", "Julho", "Agosto"],
        "tempo_crescimento": 120,
        "area_minima": 1,
        "custo_estimado_m2": 3.0,
        "rendimento_m2": 12,
        "dificuldade": "Média",
        "clima_ideal": "Temperado",
        "rega_frequencia": "2-3 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Solo deve ser bem trabalhado e sem pedras.",
        "pragas_comuns": ["Mosca da cenoura", "Nematoides"],
        "usos_culinarios": ["Cozidos", "Sumos", "Saladas", "Bolos"],
        "usos_medicinais": ["Rico em betacaroteno", "Boa para visão", "Antioxidante"],
        "compatibilidade": ["Alface", "Cebola", "Alho-francês"],
        "propagacao": "Semente",
        "icon": "🥕"
    },
    
    "batata": {
        "nome": "Batata",
        "categoria": "Hortícola",
        "tipo": "Tubérculo",
        "epoca_plantio": ["Fevereiro", "Março", "Abril"],
        "tempo_crescimento": 100,
        "area_minima": 2,
        "custo_estimado_m2": 4.0,
        "rendimento_m2": 25,
        "dificuldade": "Fácil",
        "clima_ideal": "Temperado",
        "rega_frequencia": "2 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [5.5, 6.5],
        "observacoes": "Importante fazer a amontoa. Rica em amido.",
        "pragas_comuns": ["Escaravelho da batata", "Míldio"],
        "usos_culinarios": ["Cozida", "Frita", "Assada", "Purés"],
        "usos_medicinais": ["Rica em potássio", "Energética", "Digestiva"],
        "compatibilidade": ["Feijão", "Milho", "Repolho"],
        "propagacao": "Tubérculo-semente",
        "icon": "🥔"
    },
    
    "cebola": {
        "nome": "Cebola",
        "categoria": "Hortícola",
        "tipo": "Bolbo",
        "epoca_plantio": ["Setembro", "Outubro", "Novembro"],
        "tempo_crescimento": 180,
        "area_minima": 1,
        "custo_estimado_m2": 3.5,
        "rendimento_m2": 10,
        "dificuldade": "Média",
        "clima_ideal": "Temperado",
        "rega_frequencia": "2 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Plantio no outono para colheita no verão.",
        "pragas_comuns": ["Trips", "Mosca da cebola"],
        "usos_culinarios": ["Refogados", "Saladas", "Temperos", "Conservas"],
        "usos_medicinais": ["Antibacteriana", "Expetorante", "Rica em antioxidantes"],
        "compatibilidade": ["Cenoura", "Alface", "Tomate"],
        "propagacao": "Semente ou bolbinho",
        "icon": "🧅"
    },
    
    # AROMÁTICAS
    
  "alecrim": {
    "nome": "Alecrim",
    "categoria": "Aromática",
    "tipo": "Arbusto perene",
    "epoca_plantio": ["Março", "Abril", "Setembro"],
    "tempo_crescimento": 90,
    "area_minima": 0.5,
    "custo_estimado_m2": 2.0,
    "rendimento_m2": 1.5,
    "dificuldade": "Fácil",
    "clima_ideal": "Mediterrânico",
    "rega_frequencia": "1 vez por semana",
    "sol_horas_min": 6,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Atrai polinizadores. Não tolera encharcamento.",
    "pragas_comuns": ["Cochonilha", "Ácaros"],
    "usos_culinarios": ["Assados", "Batatas", "Pães"],
    "usos_medicinais": ["Estimulante", "Melhora a memória", "Tónico circulatório"],
    "compatibilidade": ["Repolho", "Cenoura"],
    "propagacao": "Estaca",
    "icon": "🌿"
  },
  "tomilho": {
    "nome": "Tomilho",
    "categoria": "Aromática",
    "tipo": "Arbusto rasteiro",
    "epoca_plantio": ["Março", "Abril"],
    "tempo_crescimento": 60,
    "area_minima": 0.3,
    "custo_estimado_m2": 1.8,
    "rendimento_m2": 1.2,
    "dificuldade": "Fácil",
    "clima_ideal": "Seco e ensolarado",
    "rega_frequencia": "1 vez por semana",
    "sol_horas_min": 6,
    "solo_ph": [6.0, 7.0],
    "observacoes": "Muito resistente. Ideal para solos pobres.",
    "pragas_comuns": ["Pulgões", "Mosca branca"],
    "usos_culinarios": ["Carnes", "Peixes", "Legumes assados"],
    "usos_medicinais": ["Antisséptico", "Expetorante", "Digestivo"],
    "compatibilidade": ["Repolho", "Batata", "Morangueiro"],
    "propagacao": "Divisão ou estaca",
    "icon": "🌱"
  },
  "hortela": {
    "nome": "Hortelã",
    "categoria": "Aromática",
    "tipo": "Erva rasteira",
    "epoca_plantio": ["Março", "Abril", "Setembro"],
    "tempo_crescimento": 45,
    "area_minima": 0.5,
    "custo_estimado_m2": 1.5,
    "rendimento_m2": 2.5,
    "dificuldade": "Fácil",
    "clima_ideal": "Húmido e fresco",
    "rega_frequencia": "3 vezes por semana",
    "sol_horas_min": 4,
    "solo_ph": [6.0, 7.0],
    "observacoes": "Invasiva. Cultivar em vasos ou com contenção.",
    "pragas_comuns": ["Pulgões", "Ferrugem"],
    "usos_culinarios": ["Chás", "Mojitos", "Sobremesas", "Saladas"],
    "usos_medicinais": ["Digestiva", "Refrescante", "Antiespasmódica"],
    "compatibilidade": ["Tomate", "Repolho", "Ervilha"],
    "propagacao": "Estolho ou divisão",
    "icon": "🌿"
  },
  "manjerico": {
    "nome": "Manjerico",
    "categoria": "Aromática",
    "tipo": "Erva anual",
    "epoca_plantio": ["Abril", "Maio"],
    "tempo_crescimento": 60,
    "area_minima": 0.2,
    "custo_estimado_m2": 1.5,
    "rendimento_m2": 1,
    "dificuldade": "Fácil",
    "clima_ideal": "Quente e seco",
    "rega_frequencia": "2 a 3 vezes por semana",
    "sol_horas_min": 5,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Símbolo dos Santos Populares. Aroma delicado.",
    "pragas_comuns": ["Pulgões", "Mosca branca"],
    "usos_culinarios": ["Molhos pesto", "Pizzas", "Massas", "Saladas"],
    "usos_medicinais": ["Anti-inflamatório", "Digestivo", "Calmante"],
    "compatibilidade": ["Tomate", "Pimento", "Beringela"],
    "propagacao": "Semente",
    "icon": "🌿"
  },
  "salsa": {
    "nome": "Salsa",
    "categoria": "Aromática",
    "tipo": "Erva bienal",
    "epoca_plantio": ["Março", "Setembro"],
    "tempo_crescimento": 70,
    "area_minima": 0.3,
    "custo_estimado_m2": 1.2,
    "rendimento_m2": 2,
    "dificuldade": "Fácil",
    "clima_ideal": "Temperado",
    "rega_frequencia": "2 a 3 vezes por semana",
    "sol_horas_min": 4,
    "solo_ph": [6.0, 7.0],
    "observacoes": "Melhor colhida antes da floração.",
    "pragas_comuns": ["Mosca da cenoura", "Pulgões"],
    "usos_culinarios": ["Tempero universal", "Sopas", "Molhos", "Saladas"],
    "usos_medicinais": ["Rica em vitamina C", "Diurética", "Digestiva"],
    "compatibilidade": ["Tomate", "Aspargo", "Milho"],
    "propagacao": "Semente",
    "icon": "🌿"
  },
  "coentros": {
    "nome": "Coentros",
    "categoria": "Aromática",
    "tipo": "Erva anual",
    "epoca_plantio": ["Março", "Outubro"],
    "tempo_crescimento": 50,
    "area_minima": 0.3,
    "custo_estimado_m2": 1.3,
    "rendimento_m2": 1.8,
    "dificuldade": "Média",
    "clima_ideal": "Fresco",
    "rega_frequencia": "2 a 3 vezes por semana",
    "sol_horas_min": 4,
    "solo_ph": [6.0, 7.0],
    "observacoes": "Rápida floração em tempo quente.",
    "pragas_comuns": ["Pulgões", "Oídio"],
    "usos_culinarios": ["Pratos asiáticos", "Saladas", "Sopas", "Caril"],
    "usos_medicinais": ["Digestivo", "Antioxidante", "Anti-inflamatório"],
    "compatibilidade": ["Espinafre", "Dill", "Aneto"],
    "propagacao": "Semente",
    "icon": "🌿"
  },
  "oregãos": {
    "nome": "Orégãos",
    "categoria": "Aromática",
    "tipo": "Arbusto rasteiro",
    "epoca_plantio": ["Março", "Abril"],
    "tempo_crescimento": 90,
    "area_minima": 0.4,
    "custo_estimado_m2": 2.0,
    "rendimento_m2": 1.5,
    "dificuldade": "Fácil",
    "clima_ideal": "Seco e ensolarado",
    "rega_frequencia": "1 vez por semana",
    "sol_horas_min": 6,
    "solo_ph": [6.0, 8.0],
    "observacoes": "Aroma intenso. Bom para secagem.",
    "pragas_comuns": ["Mosca branca", "Ácaros"],
    "usos_culinarios": ["Pizzas", "Massas", "Carnes", "Molhos de tomate"],
    "usos_medicinais": ["Antioxidante", "Antimicrobiano", "Digestivo"],
    "compatibilidade": ["Tomate", "Beringela", "Courgette"],
    "propagacao": "Divisão ou estaca",
    "icon": "🌿"
  },
  "erva_cidreira": {
    "nome": "Erva-cidreira",
    "categoria": "Aromática",
    "tipo": "Erva perene",
    "epoca_plantio": ["Março", "Abril"],
    "tempo_crescimento": 60,
    "area_minima": 0.5,
    "custo_estimado_m2": 1.8,
    "rendimento_m2": 2,
    "dificuldade": "Fácil",
    "clima_ideal": "Temperado",
    "rega_frequencia": "2 vezes por semana",
    "sol_horas_min": 4,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Boa para infusões calmantes.",
    "pragas_comuns": ["Pulgões", "Lesmas"],
    "usos_culinarios": ["Chás", "Sobremesas", "Licores", "Saladas de fruta"],
    "usos_medicinais": ["Calmante", "Digestiva", "Antiespasmódica"],
    "compatibilidade": ["Hortelã", "Melissa", "Camomila"],
    "propagacao": "Divisão ou estaca",
    "icon": "🍋"
  },
  "cebolinho": {
    "nome": "Cebolinho",
    "categoria": "Aromática",
    "tipo": "Erva perene",
    "epoca_plantio": ["Março", "Setembro"],
    "tempo_crescimento": 60,
    "area_minima": 0.2,
    "custo_estimado_m2": 1.2,
    "rendimento_m2": 2,
    "dificuldade": "Fácil",
    "clima_ideal": "Fresco",
    "rega_frequencia": "3 vezes por semana",
    "sol_horas_min": 4,
    "solo_ph": [6.0, 7.0],
    "observacoes": "Pode ser cultivado em vasos. Corta-se e volta a crescer.",
    "pragas_comuns": ["Mosca da cebola", "Trips"],
    "usos_culinarios": ["Omeletes", "Sopas", "Saladas", "Queijos cremosos"],
    "usos_medicinais": ["Rico em vitaminas", "Digestivo", "Estimulante do apetite"],
    "compatibilidade": ["Cenoura", "Tomate", "Rosa"],
    "propagacao": "Divisão ou semente",
    "icon": "🌱"
  },
  "louro": {
    "nome": "Louro",
    "categoria": "Aromática",
    "tipo": "Arbusto lenhoso",
    "epoca_plantio": ["Março", "Outubro"],
    "tempo_crescimento": 180,
    "area_minima": 1,
    "custo_estimado_m2": 2.5,
    "rendimento_m2": 3,
    "dificuldade": "Fácil",
    "clima_ideal": "Mediterrânico",
    "rega_frequencia": "Semanal",
    "sol_horas_min": 6,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Folhas usadas secas ou frescas. Muito resistente.",
    "pragas_comuns": ["Cochonilha", "Ácaros"],
    "usos_culinarios": ["Estufados", "Sopas", "Marinadas", "Arroz"],
    "usos_medicinais": ["Digestivo", "Anti-inflamatório", "Expetorante"],
    "compatibilidade": ["Feijão", "Lentilha", "Ervilha"],
    "propagacao": "Estaca ou semente",
    "icon": "🍃"
  },

    # CEREAIS

  "trigo": {
    "nome": "Trigo",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Novembro", "Dezembro"],
    "tempo_crescimento": 180,
    "area_minima": 3,
    "custo_estimado_m2": 2.8,
    "rendimento_m2": 6,
    "dificuldade": "Média",
    "clima_ideal": "Mediterrânico",
    "rega_frequencia": "Semanal (se necessário)",
    "sol_horas_min": 6,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Base alimentar tradicional. Pode ser cultivado em sequeiro.",
    "pragas_comuns": ["Ferrugem", "Gorgulho"],
    "usos_culinarios": ["Pão", "Massas", "Bolos", "Cerveja"],
    "usos_medicinais": ["Rico em fibra", "Energético", "Fonte de proteína"],
    "compatibilidade": ["Leguminosas", "Trevo", "Girassol"],
    "propagacao": "Semente",
    "icon": "🌾"
  },
  "milho": {
    "nome": "Milho",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Abril", "Maio"],
    "tempo_crescimento": 120,
    "area_minima": 2,
    "custo_estimado_m2": 3.0,
    "rendimento_m2": 10,
    "dificuldade": "Média",
    "clima_ideal": "Quente e húmido",
    "rega_frequencia": "3 vezes por semana",
    "sol_horas_min": 6,
    "solo_ph": [5.5, 7.0],
    "observacoes": "Exige boa irrigação e solos férteis.",
    "pragas_comuns": ["Lagarta do cartucho", "Pulgões"],
    "usos_culinarios": ["Cozido", "Pipocas", "Farinha", "Xarope"],
    "usos_medicinais": ["Rico em antioxidantes", "Sem glúten", "Energético"],
    "compatibilidade": ["Feijão", "Abóbora", "Batata"],
    "propagacao": "Semente",
    "icon": "�"
  },
  "arroz": {
    "nome": "Arroz",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Abril", "Maio"],
    "tempo_crescimento": 150,
    "area_minima": 5,
    "custo_estimado_m2": 4.0,
    "rendimento_m2": 8,
    "dificuldade": "Alta",
    "clima_ideal": "Quente e húmido",
    "rega_frequencia": "Submerso",
    "sol_horas_min": 6,
    "solo_ph": [5.5, 6.5],
    "observacoes": "Cultivado principalmente no Baixo Mondego e Ribatejo.",
    "pragas_comuns": ["Chinche", "Lagarta", "Ácaros"],
    "usos_culinarios": ["Cozido", "Risotto", "Sushi", "Doces"],
    "usos_medicinais": ["Sem glúten", "Digestivo", "Energético"],
    "compatibilidade": ["Pato (tradicional)", "Azuki", "Lotus"],
    "propagacao": "Semente (transplante)",
    "icon": "🍚"
  },
  "sorgo": {
    "nome": "Sorgo",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Maio", "Junho"],
    "tempo_crescimento": 110,
    "area_minima": 3,
    "custo_estimado_m2": 2.8,
    "rendimento_m2": 6,
    "dificuldade": "Média",
    "clima_ideal": "Quente e seco",
    "rega_frequencia": "1 a 2 vezes por semana",
    "sol_horas_min": 6,
    "solo_ph": [5.5, 7.5],
    "observacoes": "Excelente para zonas com pouca água. Forragem ou grão.",
    "pragas_comuns": ["Lagarta do sorgo", "Pulgões"],
    "usos_culinarios": ["Farinha", "Xarope", "Forragem", "Bebidas"],
    "usos_medicinais": ["Sem glúten", "Rico em antioxidantes", "Fibra"],
    "compatibilidade": ["Leguminosas", "Girassol", "Soja"],
    "propagacao": "Semente",
    "icon": "🌾"
  },
  "triticale": {
    "nome": "Triticale",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Outubro", "Novembro"],
    "tempo_crescimento": 180,
    "area_minima": 3,
    "custo_estimado_m2": 2.5,
    "rendimento_m2": 6,
    "dificuldade": "Média",
    "clima_ideal": "Temperado",
    "rega_frequencia": "Eventual",
    "sol_horas_min": 5,
    "solo_ph": [5.5, 7.5],
    "observacoes": "Híbrido de trigo e centeio. Usado para ração animal.",
    "pragas_comuns": ["Ferrugem", "Gorgulho"],
    "usos_culinarios": ["Farinha", "Ração animal", "Pão integral", "Cereais"],
    "usos_medicinais": ["Rico em proteína", "Fibra", "Resistente"],
    "compatibilidade": ["Trevo", "Ervilhaca", "Mostarda"],
    "propagacao": "Semente",
    "icon": "🌾"
  },
  "painço": {
    "nome": "Painço",
    "categoria": "Cereal",
    "tipo": "Grão",
    "epoca_plantio": ["Maio", "Junho"],
    "tempo_crescimento": 100,
    "area_minima": 2,
    "custo_estimado_m2": 2.0,
    "rendimento_m2": 4,
    "dificuldade": "Fácil",
    "clima_ideal": "Seco e quente",
    "rega_frequencia": "Baixa",
    "sol_horas_min": 6,
    "solo_ph": [5.5, 7.0],
    "observacoes": "Pouco comum, mas resistente à seca.",
    "pragas_comuns": ["Pássaros", "Gorgulho"],
    "usos_culinarios": ["Farinha", "Cereais", "Mingau", "Bolos"],
    "usos_medicinais": ["Sem glúten", "Rico em magnésio", "Digestivo"],
    "compatibilidade": ["Leguminosas", "Girassol", "Sorgo"],
    "propagacao": "Semente",
    "icon": "🌾"
  },
  "espelta": {
    "nome": "Espelta",
    "categoria": "Cereal",
    "tipo": "Grão antigo",
    "epoca_plantio": ["Outubro", "Novembro"],
    "tempo_crescimento": 200,
    "area_minima": 2,
    "custo_estimado_m2": 3.0,
    "rendimento_m2": 4,
    "dificuldade": "Média",
    "clima_ideal": "Fresco e húmido",
    "rega_frequencia": "Eventual",
    "sol_horas_min": 5,
    "solo_ph": [6.0, 7.5],
    "observacoes": "Grão rústico e nutritivo. Cultivo em expansão.",
    "pragas_comuns": ["Ferrugem", "Insetos armazenados"],
    "usos_culinarios": ["Pão", "Massas", "Cerveja artesanal", "Cereais"],
    "usos_medicinais": ["Rico em proteína", "Fibra", "Minerais"],
    "compatibilidade": ["Leguminosas", "Trevo", "Colza"],
    "propagacao": "Semente",
    "icon": "🌾"
  },


    # LEGUMINOSAS

    "feijao": {
        "nome": "Feijão",
        "categoria": "Leguminosa",
        "tipo": "Vagem",
        "epoca_plantio": ["Abril", "Maio", "Junho"],
        "tempo_crescimento": 90,
        "area_minima": 2,
        "custo_estimado_m2": 3.0,
        "rendimento_m2": 8,
        "dificuldade": "Fácil",
        "clima_ideal": "Temperado",
        "rega_frequencia": "2 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Fixa nitrogênio no solo. Boa rotação de culturas.",
        "pragas_comuns": ["Antracnose", "Mosca do feijão"],
        "usos_culinarios": ["Sopas", "Estufados", "Saladas", "Conservas"],
        "usos_medicinais": ["Rico em proteína", "Fibra", "Ferro"],
        "compatibilidade": ["Milho", "Abóbora", "Cenoura"],
        "propagacao": "Semente",
        "icon": "🫘"
    },
    "ervilha": {
        "nome": "Ervilha",
        "categoria": "Leguminosa",
        "tipo": "Vagem",
        "epoca_plantio": ["Fevereiro", "Março"],
        "tempo_crescimento": 70,
        "area_minima": 1.5,
        "custo_estimado_m2": 2.5,
        "rendimento_m2": 7,
        "dificuldade": "Fácil",
        "clima_ideal": "Fresco",
        "rega_frequencia": "2 a 3 vezes por semana",
        "sol_horas_min": 5,
        "solo_ph": [6.0, 7.5],
        "observacoes": "Boa para cultivo no fim do inverno e início da primavera.",
        "pragas_comuns": ["Pulgão", "Oídio"],
        "usos_culinarios": ["Cozidas", "Saladas", "Sopas", "Purés"],
        "usos_medicinais": ["Rica em proteína", "Vitamina K", "Ácido fólico"],
        "compatibilidade": ["Cenoura", "Rabanete", "Alface"],
        "propagacao": "Semente",
        "icon": "�"
    },
    "fava": {
        "nome": "Fava",
        "categoria": "Leguminosa",
        "tipo": "Vagem",
        "epoca_plantio": ["Outubro", "Novembro"],
        "tempo_crescimento": 150,
        "area_minima": 2,
        "custo_estimado_m2": 2.2,
        "rendimento_m2": 5,
        "dificuldade": "Média",
        "clima_ideal": "Fresco",
        "rega_frequencia": "Semanal, aumentando no florescimento",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Cresce bem em solos profundos e bem drenados.",
        "pragas_comuns": ["Pulgão preto", "Ferrugem"],
        "usos_culinarios": ["Cozidas", "Purés", "Saladas", "Conservas"],
        "usos_medicinais": ["Rica em proteína", "Ferro", "Magnésio"],
        "compatibilidade": ["Batata", "Milho", "Beterraba"],
        "propagacao": "Semente",
        "icon": "�"
    },
    "grao_de_bico": {
        "nome": "Grão-de-bico",
        "categoria": "Leguminosa",
        "tipo": "Semente",
        "epoca_plantio": ["Março", "Abril"],
        "tempo_crescimento": 100,
        "area_minima": 2,
        "custo_estimado_m2": 2.8,
        "rendimento_m2": 6,
        "dificuldade": "Média",
        "clima_ideal": "Mediterrânico",
        "rega_frequencia": "1 vez por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 8.0],
        "observacoes": "Tolera bem a seca. Evitar solos muito úmidos.",
        "pragas_comuns": ["Lagarta", "Pulgão"],
        "usos_culinarios": ["Cozido", "Hummus", "Faláfel", "Saladas"],
        "usos_medicinais": ["Rico em proteína", "Fibra", "Magnésio"],
        "compatibilidade": ["Cevada", "Trigo", "Linho"],
        "propagacao": "Semente",
        "icon": "�"
    },
    "lentilha": {
        "nome": "Lentilha",
        "categoria": "Leguminosa",
        "tipo": "Semente",
        "epoca_plantio": ["Fevereiro", "Março"],
        "tempo_crescimento": 110,
        "area_minima": 1.5,
        "custo_estimado_m2": 2.7,
        "rendimento_m2": 4,
        "dificuldade": "Difícil",
        "clima_ideal": "Seco e fresco",
        "rega_frequencia": "1 vez por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 8.0],
        "observacoes": "Muito sensível ao excesso de humidade. Pouco cultivada comercialmente em Portugal.",
        "pragas_comuns": ["Ferrugem", "Ácaros"],
        "usos_culinarios": ["Sopas", "Curries", "Saladas", "Purés"],
        "usos_medicinais": ["Rica em proteína", "Ferro", "Ácido fólico"],
        "compatibilidade": ["Cevada", "Centeio", "Mostarda"],
        "propagacao": "Semente",
        "icon": "🥣"
    },
    "alfafa": {
        "nome": "Alfafa",
        "categoria": "Leguminosa",
        "tipo": "Forrageira",
        "epoca_plantio": ["Março", "Setembro"],
        "tempo_crescimento": 75,
        "area_minima": 5,
        "custo_estimado_m2": 1.5,
        "rendimento_m2": 10,
        "dificuldade": "Média",
        "clima_ideal": "Temperado seco",
        "rega_frequencia": "2 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.5, 7.5],
        "observacoes": "Alta fixação de nitrogênio. Excelente para pastagens.",
        "pragas_comuns": ["Gorgulho", "Ácaros"],
        "usos_culinarios": ["Rebentos em saladas", "Sumo verde", "Chá", "Suplemento"],
        "usos_medicinais": ["Rica em vitaminas", "Detox", "Anti-inflamatório"],
        "compatibilidade": ["Gramíneas", "Trevo", "Azevém"],
        "propagacao": "Semente",
        "icon": "🌾"
    },
    "trevo_branco": {
        "nome": "Trevo-branco",
        "categoria": "Leguminosa",
        "tipo": "Forrageira",
        "epoca_plantio": ["Março", "Outubro"],
        "tempo_crescimento": 60,
        "area_minima": 4,
        "custo_estimado_m2": 1.2,
        "rendimento_m2": 9,
        "dificuldade": "Fácil",
        "clima_ideal": "Temperado húmido",
        "rega_frequencia": "1 a 2 vezes por semana",
        "sol_horas_min": 4,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Ideal para pastoreio. Resistente ao pisoteio.",
        "pragas_comuns": ["Lesmas", "Besouro-do-trevo"],
        "usos_culinarios": ["Flores comestíveis", "Chá", "Saladas", "Mel"],
        "usos_medicinais": ["Expetorante", "Anti-inflamatório", "Purificante"],
        "compatibilidade": ["Gramíneas", "Alfafa", "Azevém"],
        "propagacao": "Semente",
        "icon": "☘️"
    },
    "soja": {
        "nome": "Soja",
        "categoria": "Leguminosa",
        "tipo": "Semente",
        "epoca_plantio": ["Maio", "Junho"],
        "tempo_crescimento": 120,
        "area_minima": 2,
        "custo_estimado_m2": 3.2,
        "rendimento_m2": 6,
        "dificuldade": "Alta",
        "clima_ideal": "Temperado quente",
        "rega_frequencia": "3 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [6.0, 7.0],
        "observacoes": "Necessita controle rigoroso de pragas. Cultivo experimental em Portugal.",
        "pragas_comuns": ["Lagarta da soja", "Pulgões"],
        "usos_culinarios": ["Tofu", "Molho soja", "Leite vegetal", "Edamame"],
        "usos_medicinais": ["Proteína completa", "Isoflavonas", "Magnésio"],
        "compatibilidade": ["Milho", "Sorgo", "Girassol"],
        "propagacao": "Semente",
        "icon": "🌾"
    },
    "tremoço": {
        "nome": "Tremoço",
        "categoria": "Leguminosa",
        "tipo": "Semente",
        "epoca_plantio": ["Outubro", "Novembro"],
        "tempo_crescimento": 130,
        "area_minima": 2,
        "custo_estimado_m2": 2.5,
        "rendimento_m2": 4,
        "dificuldade": "Média",
        "clima_ideal": "Mediterrânico",
        "rega_frequencia": "Baixa",
        "sol_horas_min": 5,
        "solo_ph": [5.5, 7.0],
        "observacoes": "Tradicional em Portugal. Muito nutritivo.",
        "pragas_comuns": ["Gorgulho", "Míldio"],
        "usos_culinarios": ["Aperitivo", "Conserva", "Salmoura"],
        "usos_medicinais": ["Rico em proteína", "Fibra", "Alcalóides"],
        "compatibilidade": ["Cevada", "Aveia", "Centeio"],
        "propagacao": "Semente",
        "icon": "🌼"
    },
    "amendoim": {
        "nome": "Amendoim",
        "categoria": "Leguminosa",
        "tipo": "Semente subterrânea",
        "epoca_plantio": ["Maio", "Junho"],
        "tempo_crescimento": 110,
        "area_minima": 3,
        "custo_estimado_m2": 3.5,
        "rendimento_m2": 5,
        "dificuldade": "Alta",
        "clima_ideal": "Quente e seco",
        "rega_frequencia": "2 vezes por semana",
        "sol_horas_min": 6,
        "solo_ph": [5.5, 6.5],
        "observacoes": "Pouco comum em Portugal, mas possível em microclimas adequados.",
        "pragas_comuns": ["Nematóides", "Lagarta do cartucho"],
        "usos_culinarios": ["Torrado", "Pasta", "Óleo", "Doces"],
        "usos_medicinais": ["Gorduras saudáveis", "Proteína", "Niacina"],
        "compatibilidade": ["Milho", "Batata-doce", "Abóbora"],
        "propagacao": "Semente",
        "icon": "🥜"
    }
}

# Categorias de culturas
CATEGORIAS = {
    "Hortícola": {
        "descricao": "Vegetais para consumo direto",
        "cor": "#10B981",  # Verde
        "icon": "🥬"
    },
    "Aromática": {
        "descricao": "Plantas aromáticas e condimentares",
        "cor": "#8B5CF6",  # Roxo
        "icon": "🌿"
    },
    "Cereal": {
        "descricao": "Grãos e cereais",
        "cor": "#F59E0B",  # Amarelo
        "icon": "🌾"
    },
    "Leguminosa": {
        "descricao": "Plantas da família das leguminosas",
        "cor": "#EF4444",  # Vermelho
        "icon": "🫘"
    }
}

# Dificuldades
DIFICULDADES = {
    "Fácil": {
        "descricao": "Ideal para iniciantes",
        "cor": "#10B981",
        "pontos": 1
    },
    "Média": {
        "descricao": "Requer alguma experiência",
        "cor": "#F59E0B",
        "pontos": 2
    },
    "Difícil": {
        "descricao": "Para agricultores experientes",
        "cor": "#EF4444",
        "pontos": 3
    }
}

def buscar_cultura(nome):
    """
    Busca informações sobre uma cultura
    
    Args:
        nome (str): Nome da cultura
        
    Returns:
        dict: Dados da cultura ou None se não encontrada
    """
    nome_clean = nome.lower().strip()
    
    # Busca exata na base principal
    if nome_clean in CULTURAS_PORTUGAL:
        return CULTURAS_PORTUGAL[nome_clean]
    
    # Busca exata na base dinâmica (IA)
    if nome_clean in CULTURAS_DINAMICAS:
        return CULTURAS_DINAMICAS[nome_clean]
    
    # Busca parcial na base principal
    for cultura_key, cultura_data in CULTURAS_PORTUGAL.items():
        if nome_clean in cultura_key or cultura_key in nome_clean:
            return cultura_data
    
    # Busca parcial na base dinâmica (IA)
    for cultura_key, cultura_data in CULTURAS_DINAMICAS.items():
        if nome_clean in cultura_key or cultura_key in nome_clean:
            return cultura_data
    
    # *** NOVA FUNCIONALIDADE: BUSCAR NO BANCO DE DADOS ***
    try:
        # Importar dentro do try para evitar problemas de contexto
        from app.models.culture import CultureType
        from app import db
        
        # Debug: adicionar logs para ver o que está acontecendo
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Buscando '{nome_clean}' no banco de dados...")
        
        # BUSCA SIMPLIFICADA E MAIS ROBUSTA
        culture_type = None
        
        # Tentar diferentes variações do nome
        name_variations = [
            nome_clean,
            nome_clean.capitalize(), 
            nome_clean.title(),
            nome_clean.upper(),
            nome_clean.lower()
        ]
        
        for name_var in name_variations:
            # Busca exata primeiro
            culture_type = CultureType.query.filter_by(name=name_var).first()
            if culture_type:
                logger.info(f"Encontrado com busca exata: '{name_var}' -> {culture_type.name}")
                break
                
            # Busca parcial
            culture_type = CultureType.query.filter(
                CultureType.name.like(f'%{name_var}%')
            ).first()
            if culture_type:
                logger.info(f"Encontrado com busca parcial: '%{name_var}%' -> {culture_type.name}")
                break
        
        # Se ainda não encontrou, usar SQL direto
        if not culture_type:
            from sqlalchemy import text
            sql = text("SELECT * FROM culture_types WHERE LOWER(name) LIKE LOWER(:pattern)")
            result = db.session.execute(sql, {'pattern': f'%{nome_clean}%'}).fetchone()
            
            if result:
                # Converter resultado para objeto CultureType
                culture_type = CultureType.query.get(result[0])  # result[0] é o ID
                logger.info(f"Encontrado com SQL direto: {culture_type.name if culture_type else 'Erro na conversão'}")
        
        if culture_type:
            logger.info(f"✅ CULTURA ENCONTRADA: {culture_type.name}")
            
            # Converter do banco para formato da base de conhecimento
            cultura_formatada = {
                "nome": culture_type.name,
                "categoria": culture_type.category.capitalize() if culture_type.category else "Hortícola",
                "tipo": culture_type.category or "hortalica",
                "tempo_crescimento": culture_type.days_to_harvest or 90,
                "dificuldade": "Média",  # padrão
                "clima_ideal": "Temperado",
                "rega_frequencia": "Regular",
                "sol_horas_min": 6,
                "solo_ph": [culture_type.soil_ph_min or 6.0, culture_type.soil_ph_max or 7.0],
                "observacoes": f"Descoberta via IA. Espaçamento: {culture_type.spacing_cm or 30}cm.",
                "pragas_comuns": [],
                "icon": "🌱",
                "fonte": "banco",  # marcar origem CORRETA
                "epoca_plantio": [culture_type.growing_season or "Primavera"],
                "area_minima": 1.0,
                "custo_estimado_m2": 3.0,
                "rendimento_m2": 10
            }
            
            # Adicionar à memória para próximas consultas
            CULTURAS_DINAMICAS[nome_clean] = cultura_formatada
            logger.info(f"Cultura {culture_type.name} carregada do banco para memória")
            
            return cultura_formatada
        else:
            logger.info("❌ CULTURA NÃO ENCONTRADA no banco")
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao buscar no banco de dados: {e}")
        import traceback
        logger.error(traceback.format_exc())
        # Continuar normalmente se der erro
    
    return None

def listar_culturas_por_categoria(categoria=None):
    """
    Lista culturas por categoria
    
    Args:
        categoria (str): Categoria desejada
        
    Returns:
        list: Lista de culturas
    """
    if categoria:
        return [
            {**dados, 'id': nome} 
            for nome, dados in CULTURAS_PORTUGAL.items() 
            if dados['categoria'] == categoria
        ]
    
    return [
        {**dados, 'id': nome} 
        for nome, dados in CULTURAS_PORTUGAL.items()
    ]

def sugerir_culturas_epoca(mes_atual):
    """
    Sugere culturas adequadas para a época atual
    
    Args:
        mes_atual (str): Mês atual (ex: "Março")
        
    Returns:
        list: Lista de culturas adequadas
    """
    culturas_epoca = []
    
    for nome, dados in CULTURAS_PORTUGAL.items():
        if mes_atual in dados['epoca_plantio']:
            culturas_epoca.append({
                **dados,
                'id': nome,
                'recomendacao': 'Época ideal para plantio'
            })
    
    return culturas_epoca

def calcular_custos_estimados(cultura_nome, area_m2):
    """
    Calcula custos estimados para uma cultura
    
    Args:
        cultura_nome (str): Nome da cultura
        area_m2 (float): Área em metros quadrados
        
    Returns:
        dict: Custos estimados
    """
    cultura = buscar_cultura(cultura_nome)
    if not cultura:
        return None
    
    custo_total = cultura['custo_estimado_m2'] * area_m2
    rendimento_total = cultura['rendimento_m2'] * area_m2
    
    # Preços médios de venda em Portugal (euros/kg)
    precos_venda = {
        'tomate': 2.50,
        'alface': 1.80,
        'cenoura': 1.20,
        'batata': 1.00,
        'cebola': 1.30,
        'manjericão': 8.00,
        'salsa': 6.00,
        'milho': 0.80,
        'trigo': 0.60,
        'feijão': 3.50,
        'ervilha': 4.00
    }
    
    preco_kg = precos_venda.get(cultura_nome.lower(), 2.00)
    receita_estimada = rendimento_total * preco_kg
    lucro_estimado = receita_estimada - custo_total
    
    return {
        'custo_total': round(custo_total, 2),
        'rendimento_kg': round(rendimento_total, 1),
        'receita_estimada': round(receita_estimada, 2),
        'lucro_estimado': round(lucro_estimado, 2),
        'roi_percentual': round((lucro_estimado / custo_total * 100) if custo_total > 0 else 0, 1),
        'preco_venda_kg': preco_kg
    }

def validar_condicoes_cultura(cultura_nome, dados_condicoes):
    """
    Valida se as condições são adequadas para a cultura
    
    Args:
        cultura_nome (str): Nome da cultura
        dados_condicoes (dict): Condições disponíveis
        
    Returns:
        dict: Resultado da validação
    """
    cultura = buscar_cultura(cultura_nome)
    if not cultura:
        return {'valido': False, 'erro': 'Cultura não encontrada'}
    
    alertas = []
    pontuacao = 100  # Começa com 100%
    
    # Verificar área mínima
    if dados_condicoes.get('area', 0) < cultura['area_minima']:
        alertas.append(f"Área muito pequena. Mínimo recomendado: {cultura['area_minima']}m²")
        pontuacao -= 20
    
    # Verificar época de plantio
    mes_atual = dados_condicoes.get('mes_plantio')
    if mes_atual and mes_atual not in cultura['epoca_plantio']:
        alertas.append(f"Época não ideal. Melhores meses: {', '.join(cultura['epoca_plantio'])}")
        pontuacao -= 15
    
    # Verificar horas de sol
    horas_sol = dados_condicoes.get('horas_sol', 6)
    if horas_sol < cultura['sol_horas_min']:
        alertas.append(f"Pouca luz solar. Mínimo: {cultura['sol_horas_min']} horas/dia")
        pontuacao -= 10
    
    # Verificar pH do solo
    ph_solo = dados_condicoes.get('ph_solo')
    if ph_solo and (ph_solo < cultura['solo_ph'][0] or ph_solo > cultura['solo_ph'][1]):
        alertas.append(f"pH do solo inadequado. Ideal: {cultura['solo_ph'][0]}-{cultura['solo_ph'][1]}")
        pontuacao -= 10
    
    return {
        'valido': pontuacao >= 70,
        'pontuacao': max(0, pontuacao),
        'alertas': alertas,
        'recomendacoes': cultura.get('observacoes', ''),
        'dificuldade': cultura['dificuldade']
    }


# CULTURAS EXPANDIDAS DINAMICAMENTE (via IA)
CULTURAS_DINAMICAS = {}


def adicionar_cultura_dinamica(cultura_info):
    """
    Adiciona uma nova cultura à base de conhecimento dinamicamente
    E PERSISTE NO BANCO DE DADOS
    
    Args:
        cultura_info (dict): Informações da cultura obtidas via IA
        
    Returns:
        bool: True se adicionou com sucesso
    """
    try:
        nome_key = cultura_info.get('nome', '').lower()
        if not nome_key:
            return False
        
        # Converter formato da IA para formato da base de conhecimento
        cultura_formatada = {
            "nome": cultura_info.get('nome'),
            "nome_cientifico": cultura_info.get('nome_cientifico', ''),
            "categoria": _mapear_tipo_para_categoria(cultura_info.get('tipo', 'hortalica')),
            "tipo": cultura_info.get('tipo', 'hortalica'),
            "epoca_plantio": _processar_epoca_plantio(cultura_info.get('epoca_plantio', '')),
            "tempo_crescimento": _extrair_numero(cultura_info.get('ciclo_dias', '90')),
            "area_minima": 1.0,  # padrão
            "custo_estimado_m2": 3.0,  # padrão
            "rendimento_m2": 10,  # padrão
            "dificuldade": cultura_info.get('dificuldade', 'Média').capitalize(),
            "clima_ideal": "Temperado",  # padrão para Portugal
            "rega_frequencia": cultura_info.get('irrigacao', 'Regular'),
            "sol_horas_min": 6,  # padrão
            "solo_ph": _processar_ph_solo(cultura_info.get('ph_solo', '6.0-7.0')),
            "observacoes": f"{cultura_info.get('espacamento', '')}. {cultura_info.get('profundidade_plantio', '')}. {cultura_info.get('temperatura_ideal', '')}".strip('. '),
            "pragas_comuns": cultura_info.get('pragas_comuns', []),
            "icon": "🌱",  # padrão
            "fonte": "IA",  # marcar origem
            "variedade": cultura_info.get('variedade', ''),
            "luz_solar": cultura_info.get('luz_solar', ''),
            "fertilizacao": cultura_info.get('fertilizacao', ''),
            "colheita_indicadores": cultura_info.get('colheita_indicadores', ''),
            "regiao_adaptacao": cultura_info.get('regiao_adaptacao', '')
        }
        
        # 1. Adicionar à base dinâmica (memória)
        CULTURAS_DINAMICAS[nome_key] = cultura_formatada
        
        # 2. PERSISTIR NO BANCO DE DADOS
        try:
            from app import db
            from app.models.culture import CultureType
            
            # Verificar se já existe no banco
            existing_type = CultureType.query.filter_by(name=cultura_formatada['nome']).first()
            
            if not existing_type:
                # Criar novo CultureType no banco - VERSÃO SIMPLIFICADA
                culture_type = CultureType()
                culture_type.name = cultura_formatada['nome']
                culture_type.category = cultura_formatada['categoria'].lower()
                culture_type.growing_season = 'spring'
                culture_type.planting_depth_cm = 2.0
                culture_type.spacing_cm = 30.0
                culture_type.days_to_germination = 15
                culture_type.days_to_harvest = cultura_formatada['tempo_crescimento']
                culture_type.water_requirements = 'medium'
                culture_type.sunlight_requirements = 'full_sun'
                culture_type.soil_ph_min = 6.0
                culture_type.soil_ph_max = 7.0
                
                db.session.add(culture_type)
                db.session.commit()
                
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Cultura {cultura_formatada['nome']} persistida no banco de dados via IA")
            
        except Exception as db_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao persistir no banco (mas continuando com memória): {db_error}")
            # Continuar mesmo se der erro no banco
        
        return True
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao adicionar cultura dinâmica: {e}")
        return False


def _mapear_tipo_para_categoria(tipo):
    """Mapeia tipo da IA para categoria da base de conhecimento"""
    mapeamento = {
        'hortalica': 'Hortícola',
        'arvore_frutifera': 'Frutífera',
        'erva_aromatica': 'Aromática',
        'cereal': 'Cereal',
        'leguminosa': 'Leguminosa',
        'tuberculo': 'Tubérculo'
    }
    return mapeamento.get(tipo, 'Hortícola')


def _processar_epoca_plantio(epoca_texto):
    """Processa texto de época de plantio para lista de meses"""
    if not epoca_texto:
        return ["Primavera"]
    
    meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    epoca_lower = epoca_texto.lower()
    meses_encontrados = []
    
    for mes in meses:
        if mes.lower() in epoca_lower:
            meses_encontrados.append(mes)
    
    if not meses_encontrados:
        if 'primavera' in epoca_lower:
            return ["Março", "Abril", "Maio"]
        elif 'verão' in epoca_lower or 'verao' in epoca_lower:
            return ["Junho", "Julho", "Agosto"]
        elif 'outono' in epoca_lower:
            return ["Setembro", "Outubro", "Novembro"]
        elif 'inverno' in epoca_lower:
            return ["Dezembro", "Janeiro", "Fevereiro"]
        else:
            return ["Primavera"]
    
    return meses_encontrados


def _extrair_numero(texto):
    """Extrai número de dias de um texto"""
    if isinstance(texto, (int, float)):
        return int(texto)
    
    import re
    numeros = re.findall(r'\d+', str(texto))
    return int(numeros[0]) if numeros else 90


def _processar_ph_solo(ph_texto):
    """Processa texto de pH para lista [min, max]"""
    if not ph_texto:
        return [6.0, 7.0]
    
    import re
    numeros = re.findall(r'\d+\.?\d*', str(ph_texto))
    
    if len(numeros) >= 2:
        return [float(numeros[0]), float(numeros[1])]
    elif len(numeros) == 1:
        ph = float(numeros[0])
        return [ph - 0.5, ph + 0.5]
    else:
        return [6.0, 7.0]
