# SISTEMA DE ALERTAS - AGENTE AGRÍCOLA
## Documentação Completa para Impressão

**Data:** 07 de Agosto de 2025  
**Versão:** 1.0  
**Sistema:** Agente Agrícola - Plataforma de Monitoramento Agrícola

---

## RESUMO EXECUTIVO

O Sistema de Alertas do Agente Agrícola é uma solução automatizada que monitora condições climáticas, status das culturas e cronogramas de manutenção, gerando notificações proativas para auxiliar na tomada de decisões agrícolas.

### ARQUITETURA DO SISTEMA
- **Serviço Principal:** AlertService (app/services/alert_service.py)
- **Integração:** DashboardService para visualização unificada
- **API:** Endpoints REST para comunicação com frontend
- **Banco de Dados:** SQLite com tabela de alertas persistentes

---

## CATEGORIAS DE ALERTAS

### 1. ALERTAS CLIMÁTICOS (Weather Alerts)

#### 1.1 ALERTAS DE TEMPERATURA
- **Temperaturas Extremas**
  - Trigger: Temperatura > 35°C ou < 5°C
  - Prioridade: High
  - Ação: Proteção das culturas contra estresse térmico

- **Previsão de Geada**
  - Trigger: Previsão < 0°C nas próximas 24h
  - Prioridade: Critical
  - Ação: Proteção imediata contra geada

- **Ondas de Calor**
  - Trigger: Temperatura > 30°C por períodos prolongados
  - Prioridade: High
  - Ação: Aumento da irrigação e sombreamento

#### 1.2 ALERTAS DE UMIDADE
- **Umidade Muito Baixa**
  - Trigger: Umidade < 30%
  - Prioridade: Medium
  - Risco: Estresse hídrico nas plantas

- **Umidade Muito Alta**
  - Trigger: Umidade > 90%
  - Prioridade: Medium
  - Risco: Desenvolvimento de fungos e doenças

#### 1.3 ALERTAS DE VENTO
- **Ventos Fortes**
  - Trigger: Velocidade > 15 m/s
  - Prioridade: High
  - Risco: Danos físicos às culturas

#### 1.4 ALERTAS DE PRECIPITAÇÃO
- **Chuva Forte Prevista**
  - Trigger: Previsão > 20mm nas próximas 24h
  - Prioridade: Medium
  - Ação: Preparação para excesso de água

- **Risco de Encharcamento**
  - Trigger: Acúmulo excessivo de água
  - Prioridade: High
  - Risco: Danos às raízes por excesso de umidade

---

### 2. ALERTAS DE CULTURAS (Culture Alerts)

#### 2.1 ALERTAS DE IRRIGAÇÃO
Sistema baseado no tipo de cultura e tempo desde última irrigação:

- **Hortaliças:** Alerta após 2 dias sem irrigação
- **Frutas:** Alerta após 3 dias sem irrigação
- **Grãos:** Alerta após 5 dias sem irrigação
- **Outras culturas:** Alerta após 4 dias sem irrigação

**Prioridade:** Medium a High (dependendo do tempo decorrido)

#### 2.2 ALERTAS DE COLHEITA
- **Tempo Ideal de Colheita**
  - Baseado no ciclo específico de cada cultura
  - Prioridade: Medium
  - Ação: Planejamento da colheita

- **Colheita Atrasada**
  - Trigger: Passou do tempo ideal
  - Prioridade: Critical
  - Ação: Colheita imediata necessária

#### 2.3 ALERTAS DE SAÚDE DAS CULTURAS
- **Problemas Críticos (health_status = 'poor')**
  - Prioridade: Critical
  - Ação: Investigação imediata necessária

- **Atenção Necessária (health_status = 'fair')**
  - Prioridade: Medium
  - Ação: Monitoramento aumentado

---

### 3. ALERTAS DE TAREFAS (Task Alerts)

#### 3.1 MANUTENÇÃO PROGRAMADA
- **Verificação Semanal**
  - Trigger: A cada 7 dias após plantio
  - Prioridade: Medium
  - Atividades: Inspeção geral da cultura

- **Inspeção de Rotina**
  - Verificação de pragas
  - Verificação de doenças
  - Avaliação de necessidades de irrigação
  - Monitoramento de crescimento

---

## SISTEMA DE PRIORIDADES

### CRITICAL (Crítico)
- Geada prevista
- Colheita atrasada
- Problemas graves de saúde das culturas
- **Ação:** Intervenção imediata necessária

### HIGH (Alto)
- Temperaturas extremas
- Ventos fortes
- Risco de encharcamento
- **Ação:** Atenção prioritária nas próximas horas

### MEDIUM (Médio)
- Necessidade de irrigação
- Umidade inadequada
- Verificações semanais
- Tempo ideal de colheita
- **Ação:** Atenção nas próximas 24-48 horas

### LOW (Baixo)
- Informações gerais
- Lembretes de rotina
- **Ação:** Quando conveniente

---

## ESTADOS DOS ALERTAS

### PENDING (Pendente)
- Alertas novos aguardando visualização
- Status padrão para alertas recém-criados
- Contabilizados como "não lidos"

### READ (Lido)
- Alertas visualizados pelo usuário
- Ainda ativos, mas já conhecidos
- Não contabilizados como "não lidos"

### RESOLVED (Resolvido)
- Alertas tratados/solucionados
- Não aparecem em listagens ativas
- Mantidos para histórico

---

## DADOS CONTEXTUAIS DOS ALERTAS

### INFORMAÇÕES INCLUÍDAS
- **Nome da Cultura:** Identificação específica
- **Valores Medidos:** Temperatura, umidade, velocidade do vento
- **Tempo Decorrido:** Dias desde plantio, última irrigação
- **Status de Saúde:** Estado atual da cultura
- **Localização:** Coordenadas geográficas (quando disponível)

### RECOMENDAÇÕES AUTOMÁTICAS
- **harvest_immediately:** Colher imediatamente
- **increase_irrigation:** Aumentar irrigação
- **protect_from_frost:** Proteger contra geada
- **investigate_health_issues:** Investigar problemas de saúde
- **increase_monitoring:** Aumentar monitoramento

---

## INTEGRAÇÃO TÉCNICA

### API ENDPOINTS
- **GET /api/alerts/widget:** Dados para widget do dashboard
- **POST /api/alerts/{id}/read:** Marcar como lido
- **POST /api/alerts/{id}/resolve:** Resolver alerta

### MÉTODOS PRINCIPAIS
- **generate_all_alerts():** Gera todos os tipos de alertas
- **generate_weather_alerts():** Alertas climáticos específicos
- **generate_culture_alerts():** Alertas por cultura
- **generate_task_alerts():** Alertas de tarefas
- **get_active_alerts():** Recupera alertas ativos
- **get_unread_alerts():** Recupera alertas não lidos

### ESTATÍSTICAS DISPONÍVEIS
- **Total de Alertas Ativos**
- **Alertas Não Lidos**
- **Alertas Críticos**
- **Alertas Resolvidos**

---

## BENEFÍCIOS DO SISTEMA

### PREVENÇÃO
- Antecipa problemas antes que causem perdas
- Monitora condições climáticas adversas
- Alerta sobre cronogramas de manutenção

### OTIMIZAÇÃO
- Melhora o timing de irrigação
- Otimiza períodos de colheita
- Reduz perdas por condições inadequadas

### PRODUTIVIDADE
- Interface unificada para todos os alertas
- Priorização automática por importância
- Recomendações específicas para cada situação

---

## CONSIDERAÇÕES TÉCNICAS

### PERFORMANCE
- Alertas gerados sob demanda
- Cache de dados climáticos
- Otimização de consultas ao banco

### ESCALABILIDADE
- Suporte a múltiplos usuários
- Alertas específicos por cultura
- Sistema modular e extensível

### CONFIABILIDADE
- Tratamento de erros robusto
- Logs detalhados para debugging
- Fallbacks para dados indisponíveis

---

**Documento gerado automaticamente pelo Sistema de Alertas do Agente Agrícola**  
**Para suporte técnico:** Consulte a documentação completa no repositório do projeto
