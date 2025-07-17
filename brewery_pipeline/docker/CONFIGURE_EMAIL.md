# 🔐 Instruções para Configurar Senha de Email

## 📋 PASSOS OBRIGATÓRIOS

### 1. Criar Senha de Aplicativo no Gmail

1. **Acesse**: https://myaccount.google.com/security
2. **Verifique**: Se a verificação em 2 etapas está ATIVA
   - Se não estiver, ative primeiro
3. **Procure**: "Senhas de app" ou "App passwords"
4. **Clique**: "Gerar nova senha" ou "Generate"
5. **Selecione**: "Outro (nome personalizado)" ou "Other"
6. **Digite**: `Airflow Notifications`
7. **Copie**: A senha gerada (formato: `abcd efgh ijkl mnop`)

### 2. Substituir no Docker Compose

No arquivo `docker-compose-simple.yaml`, substitua **AMBAS** as ocorrências de:

```
AIRFLOW__SMTP__SMTP_PASSWORD: your_app_password_here
```

Por:

```
AIRFLOW__SMTP__SMTP_PASSWORD: SUA_SENHA_DE_APLICATIVO_AQUI
```

**ATENÇÃO**: São 2 lugares para substituir:
- Linha ~28 (airflow-webserver)
- Linha ~65 (airflow-scheduler)

### 3. Exemplo de Substituição

**ANTES**:
```yaml
AIRFLOW__SMTP__SMTP_PASSWORD: your_app_password_here
```

**DEPOIS** (exemplo com senha fictícia):
```yaml
AIRFLOW__SMTP__SMTP_PASSWORD: abcd efgh ijkl mnop
```

## 🚀 Após Configurar

1. **Salve o arquivo**
2. **Reinicie o ambiente**:
   ```bash
   docker-compose -f docker-compose-simple.yaml down
   docker-compose -f docker-compose-simple.yaml up -d
   ```

3. **Teste o sistema**:
   - Acesse: http://localhost:8080
   - Execute a DAG: `test_notifications`
   - Verifique se recebe o email

## ⚠️ IMPORTANTE

- **NÃO use sua senha normal do Gmail**
- **USE APENAS a senha de aplicativo gerada**
- **A senha tem 16 caracteres com espaços**
- **Mantenha esta senha segura**

## 🔍 Verificar se Funcionou

Após reiniciar, execute:

```bash
# Ver logs para verificar configuração
docker logs docker-airflow-scheduler-1 | grep -i smtp

# Testar conectividade
docker exec docker-airflow-scheduler-1 python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print('✅ SMTP conectado com sucesso')
except Exception as e:
    print(f'❌ Erro SMTP: {e}')
"
```

## 📧 Testando Email

1. **Acesse Airflow**: http://localhost:8080
2. **Vá para DAGs**
3. **Execute**: `test_notifications`
4. **Execute a task**: `test_failure_task`
5. **Verifique**: Se recebeu email de teste

Se tudo estiver correto, você receberá um email de teste!
