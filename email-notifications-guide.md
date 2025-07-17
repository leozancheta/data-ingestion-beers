# 📧 Configuração de Notificações por Email no Airflow

## 🚨 Problema Identificado

As notificações por email não estão funcionando porque:
1. Configuração SMTP não estava no Docker Compose
2. Senha de aplicativo do Gmail não configurada
3. Fallbacks de notificação não implementados

## ✅ Soluções Implementadas

### 1. 🐳 Configuração Docker Atualizada

Adicionadas as seguintes variáveis no `docker-compose-simple.yaml`:

```yaml
# Configurações de email
AIRFLOW__EMAIL__EMAIL_BACKEND: airflow.utils.email.send_email_smtp
AIRFLOW__SMTP__SMTP_HOST: smtp.gmail.com
AIRFLOW__SMTP__SMTP_STARTTLS: 'true'
AIRFLOW__SMTP__SMTP_SSL: 'false'
AIRFLOW__SMTP__SMTP_PORT: 587
AIRFLOW__SMTP__SMTP_USER: leozancheta@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD: your_app_password_here
AIRFLOW__SMTP__SMTP_MAIL_FROM: leozancheta@gmail.com
```

### 2. 🔐 Configurar Senha de Aplicativo do Gmail

**IMPORTANTE**: Você precisa configurar uma senha de aplicativo no Gmail:

#### Passos para criar senha de aplicativo:

1. **Acesse**: https://myaccount.google.com/security
2. **Ative a verificação em 2 etapas** (se não estiver ativa)
3. **Vá em**: "Senhas de app"
4. **Selecione**: "Outro (nome personalizado)"
5. **Digite**: "Airflow Notifications"
6. **Copie a senha gerada** (16 caracteres)
7. **Substitua** `your_app_password_here` no docker-compose pela senha gerada

### 3. 🛠️ DAG Melhorada com Múltiplas Notificações

A DAG principal (`brewery_dag.py`) agora tem:

- ✅ **Logs detalhados** no console do Airflow
- ✅ **Notificação por email** (se SMTP configurado)
- ✅ **Fallback para arquivo** se email falhar
- ✅ **Callbacks de sucesso** também implementados

### 4. 🧪 DAG de Teste

Criada `test_notifications_dag.py` para testar o sistema:

- Task que executa com sucesso
- Task que falha intencionalmente
- Permite verificar se emails estão funcionando

## 🚀 Como Testar

### Passo 1: Configurar Senha de Aplicativo

1. Configure a senha de aplicativo do Gmail (ver acima)
2. Edite o `docker-compose-simple.yaml`
3. Substitua `your_app_password_here` pela senha real

### Passo 2: Reiniciar o Ambiente

```bash
# Parar containers
docker-compose -f docker-compose-simple.yaml down

# Subir com nova configuração
docker-compose -f docker-compose-simple.yaml up -d

# Verificar logs
docker-compose logs airflow-scheduler
```

### Passo 3: Testar Notificações

1. **Acesse**: http://localhost:8080
2. **Vá para**: DAGs
3. **Execute**: `test_notifications` (manual)
4. **Teste as duas tasks**:
   - `test_success_task` (deve executar com sucesso)
   - `test_failure_task` (deve falhar e enviar email)

### Passo 4: Verificar Resultados

#### Se o email funcionar:
- ✅ Você receberá email em leozancheta@gmail.com
- ✅ Logs mostrarão "Email enviado com sucesso"

#### Se o email não funcionar:
- ⚠️ Logs mostrarão o erro de email
- 📝 Notificação será salva em `/opt/airflow/data/failure_notifications_*.log`
- 🔍 Verifique logs do container para detalhes

## 🔍 Troubleshooting

### Email não enviado:

1. **Verificar senha de aplicativo**:
   ```bash
   # Ver configuração no container
   docker exec docker-airflow-scheduler-1 env | grep SMTP
   ```

2. **Verificar conectividade SMTP**:
   ```bash
   # Testar conexão dentro do container
   docker exec docker-airflow-scheduler-1 bash -c "telnet smtp.gmail.com 587"
   ```

3. **Verificar logs detalhados**:
   ```bash
   # Logs do scheduler
   docker logs docker-airflow-scheduler-1 | grep -i email
   
   # Logs da DAG específica
   # Vá para Airflow UI > DAGs > brewery_pipeline > Logs
   ```

### Arquivo de fallback:

Se emails não funcionarem, verifique:
```bash
# Ver arquivos de notificação
docker exec docker-airflow-scheduler-1 ls -la /opt/airflow/data/failure_notifications_*.log

# Ler conteúdo
docker exec docker-airflow-scheduler-1 cat /opt/airflow/data/failure_notifications_*.log
```

## 📊 Monitoramento

### Logs importantes para acompanhar:

1. **Logs do Airflow**: Interface web > DAGs > Task > Logs
2. **Logs do container**: `docker logs docker-airflow-scheduler-1`
3. **Arquivos de notificação**: `/opt/airflow/data/failure_notifications_*.log`

### Verificação de saúde:

```bash
# Status dos containers
docker ps

# Verificar configuração de email
docker exec docker-airflow-scheduler-1 python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print('✅ Conexão SMTP OK')
except Exception as e:
    print(f'❌ Erro SMTP: {e}')
"
```

## 🎯 Próximos Passos

1. **Configure a senha de aplicativo** do Gmail
2. **Reinicie o ambiente** Docker
3. **Execute a DAG de teste** para verificar funcionamento
4. **Se funcionar**: O sistema de produção está pronto
5. **Se não funcionar**: Verifique os logs e troubleshooting acima

---

*Implementado em Julho 2025 - Sistema de Notificações v2.0* 📧
