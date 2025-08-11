# 🐳 DOCKER SETUP - AGROTECH 1.0

## 📋 **DOCKERFILE CRIADO**

### **Especificação Seguida:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "run.py"]
```

## 🚀 **COMO USAR**

### 1. **Build da Imagem**
```bash
# Build básico
docker build -t agrotech-app .

# Build com tag de versão
docker build -t agrotech-app:1.0 .
```

### 2. **Executar Container**
```bash
# Execução básica
docker run -p 5000:5000 agrotech-app

# Com variáveis de ambiente
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///app.db \
  agrotech-app

# Com arquivo .env
docker run -p 5000:5000 --env-file .env agrotech-app
```

### 3. **Desenvolvimento com Volume**
```bash
# Para desenvolvimento (code reload)
docker run -p 5000:5000 \
  -v $(pwd):/app \
  -e FLASK_ENV=development \
  agrotech-app
```

## 📁 **ARQUIVOS CRIADOS**

### ✅ **Dockerfile**
- Baseado em Python 3.11-slim
- Instala dependências via requirements.txt
- Executa run.py como comando principal

### ✅ **.dockerignore**
- Exclui arquivos desnecessários do build
- Otimiza tempo de build e tamanho da imagem
- Evita copiar logs, cache, etc.

## 🔧 **OTIMIZAÇÕES IMPLEMENTADAS**

### **Build Eficiente:**
- ✅ Python 3.11-slim (imagem leve)
- ✅ .dockerignore (build rápido)
- ✅ Cópia de todo código (simplicidade)

### **Execução:**
- ✅ Comando direto: `python run.py`
- ✅ Compatível com Railway/Heroku
- ✅ Porta 5000 padrão

## 🌐 **DEPLOYMENT**

### **Railway:**
```bash
# Railway detecta automaticamente o Dockerfile
railway login
railway init
railway up
```

### **Heroku:**
```bash
# Heroku também suporta Dockerfile
heroku create your-app-name
git push heroku main
```

### **Docker Compose (opcional):**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secret-key
    volumes:
      - ./instance:/app/instance
```

## 🔍 **VERIFICAÇÃO**

### **Teste Local:**
```bash
# 1. Build
docker build -t agrotech-test .

# 2. Run
docker run -p 5000:5000 agrotech-test

# 3. Acesse
curl http://localhost:5000
```

### **Debug:**
```bash
# Executar bash no container
docker run -it --entrypoint bash agrotech-app

# Ver logs
docker logs <container-id>
```

## ✅ **BENEFÍCIOS**

### **Portabilidade:**
- ✅ Funciona em qualquer ambiente
- ✅ Dependências isoladas
- ✅ Versão Python garantida

### **Deployment:**
- ✅ Build consistente
- ✅ Compatível com clouds
- ✅ Fácil escalabilidade

### **Desenvolvimento:**
- ✅ Ambiente padronizado
- ✅ Fácil setup para novos devs
- ✅ Consistência entre dev/prod

---

**📦 Dockerfile:** Simples e eficiente  
**🚀 Deploy:** Railway/Heroku ready  
**🔧 Manutenção:** Fácil e direta
