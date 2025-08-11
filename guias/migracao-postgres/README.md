# 🗄️ MIGRAÇÃO POSTGRESQL - GUIAS E SCRIPTS

Guias completos para migração de banco de dados PostgreSQL em produção no Railway.

## 📋 **ARQUIVOS NESTE DIRETÓRIO**

### 📖 **Documentação**
- **`GUIA_MIGRACAO_POSTGRESQL_PRODUCAO.md`** - Guia completo com estratégias detalhadas

### 🛠️ **Scripts Executáveis**
- **`migration_script.py`** - Executa migrações diretamente no PostgreSQL
- **`validation_script.py`** - Valida migrações pós-execução  
- **`diagnostic_script.py`** - Diagnostica problemas comuns
- **`exemplo_uso.py`** - Demonstração interativa do workflow

---

## 🚀 **INÍCIO RÁPIDO**

### **Migração de Emergência**
```bash
export DATABASE_URL="postgresql://..."
python migration_script.py
python validation_script.py
```

### **Primeira Vez**
```bash
python exemplo_uso.py
```

### **Diagnosticar Problemas**
```bash
python diagnostic_script.py
```

---

## 📊 **BASEADO EM EXPERIÊNCIA REAL**

Estes guias foram criados baseados na correção real da tabela `alerts` em produção:
- ✅ 3 iterações de correção (commits c55d072 → d20e8b0 → 7e83125)
- ✅ 13 colunas adicionadas com sucesso
- ✅ 100% de uptime mantido
- ✅ API funcionando perfeitamente

---

## 💡 **DICAS**

1. **Sempre começar** com diagnóstico: `python diagnostic_script.py`
2. **Configurar DATABASE_URL** antes de executar migrações
3. **Validar sempre** após migração: `python validation_script.py`
4. **Consultar o guia completo** em `GUIA_MIGRACAO_POSTGRESQL_PRODUCAO.md`

---

**Criado:** Agosto 2025 | **Status:** Testado em produção | **Sucesso:** 100%
