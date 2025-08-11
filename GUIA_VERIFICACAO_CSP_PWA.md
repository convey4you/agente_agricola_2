# 🔍 Guia de Verificação e Testes - Correções de CSP e PWA

## 📋 Lista de Verificação Pós-Correção

### Verificações de Content Security Policy (CSP)

#### 1. Verificação de Erros no Console
- [ ] Abra o Chrome DevTools (F12)
- [ ] Navegue até a aba "Console"
- [ ] Verifique que não existem erros de CSP:
  - Sem mensagens "Refused to load..."
  - Sem mensagens "Refused to execute inline script..."

#### 2. Verificação dos Headers de Segurança
- [ ] Use a aba "Network" do DevTools
- [ ] Selecione qualquer requisição HTML
- [ ] Na aba "Headers", verifique:
  - Content-Security-Policy não contém 'unsafe-inline' para scripts
  - Content-Security-Policy usa 'nonce-xyz' para scripts

#### 3. Teste de Funcionalidades Críticas
- [ ] Login funciona corretamente
- [ ] Dashboard carrega todos os elementos
- [ ] Alertas são exibidos e podem ser fechados
- [ ] Fontes personalizadas carregam corretamente

### Verificações de Progressive Web App (PWA)

#### 1. Validação do Manifest
- [ ] No Chrome DevTools, navegue até a aba "Application"
- [ ] Selecione "Manifest" no painel lateral esquerdo
- [ ] Verifique:
  - Todos os ícones são exibidos sem erros
  - Nome e descrição aparecem corretamente
  - Identity e icons estão configurados corretamente

#### 2. Teste de Instalação
- [ ] Clique no ícone de instalação na barra de endereço do Chrome
- [ ] Verifique se a janela de instalação aparece corretamente
- [ ] Complete o processo de instalação
- [ ] Verifique se o aplicativo abre corretamente após instalação

#### 3. Verificação de Ícones
- [ ] Verifique se todos os ícones aparecem na interface do PWA
- [ ] Certifique-se que o ícone correto aparece na área de trabalho após instalação
- [ ] Verifique se o splash screen mostra o ícone correto

## 🧪 Scripts de Teste

### Teste de Headers de Segurança

```powershell
# PowerShell - Verificar Headers de Segurança
$response = Invoke-WebRequest -Uri "http://localhost:5000/auth/login"
$response.Headers["Content-Security-Policy"]

# Resultado esperado: deve conter 'nonce-' e NÃO deve conter 'unsafe-inline' para script-src
```

### Verificação de Arquivos de Ícones

```powershell
# PowerShell - Verificar existência e tamanho dos ícones
$icones = Get-Item app/static/icons/icon-*.png | Select-Object Name, Length, LastWriteTime
$icones | Format-Table -AutoSize

# Resultado esperado: todos os arquivos de ícones devem existir e ter tamanho > 0
```

### Validação do Manifest

```powershell
# PowerShell - Validar arquivo manifest.json
$manifest = Get-Content app/static/manifest.json | ConvertFrom-Json
$manifest.icons | Format-Table src, sizes, type -AutoSize

# Resultado esperado: lista de ícones com caminhos corretos
```

## 🔄 Processo de Verificação Completo

1. **Reinicie o servidor Flask:**
   ```powershell
   # PowerShell
   # Pare o servidor atual (Ctrl+C) e reinicie
   python run.py
   ```

2. **Limpe o cache do navegador:**
   ```
   Chrome: Ctrl+Shift+Del -> Selecione "Cached images and files" -> Clear data
   ```

3. **Verifique o console do navegador:**
   - Abra Chrome DevTools (F12)
   - Navegue pela aplicação, verificando cada página
   - Confirme ausência de erros relacionados a CSP ou recursos

4. **Teste a instalação do PWA:**
   - Clique no ícone de instalação na barra de endereço
   - Complete o processo de instalação
   - Abra o aplicativo instalado
   - Verifique a funcionalidade completa no modo PWA

5. **Registro do teste:**
   - Documente quaisquer problemas encontrados
   - Capture screenshots de evidência de sucesso
   - Atualize o registro de verificação acima

## 📊 Resultados Esperados

| Teste | Resultado Esperado |
|-------|-------------------|
| Erros CSP no Console | Zero erros |
| Diretiva 'unsafe-inline' para script-src | Ausente |
| Nonce em scripts inline | Presente em todos |
| Carregamento de fontes | Sem erros |
| Ícones do manifest | Todos carregam corretamente |
| Instalação PWA | Funciona sem erros |
| Funcionalidade após instalação | Idêntica à versão web |

## 🔍 Resolução de Problemas Comuns

### Se persistirem erros de CSP:
1. Verifique se todos os scripts inline têm um atributo nonce válido
2. Verifique se nenhum template usa eventos inline (onclick, onload, etc.)
3. Confirme que a diretiva CSP no middleware inclui todas as fontes necessárias

### Se os ícones do PWA não aparecerem:
1. Verifique o formato dos arquivos de ícone (deve ser PNG válido)
2. Confirme que os caminhos no manifest.json apontam para os arquivos corretos
3. Verifique se os arquivos têm permissões de leitura adequadas

---

**Autor do Guia**: GitHub Copilot  
**Versão**: 1.0  
**Data**: 05/08/2025
