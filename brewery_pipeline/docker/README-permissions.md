# Configuração Automática de Permissões do Airflow

Este documento explica como configurar permissões automáticas (`chmod -R 777 /opt/airflow`) na subida dos containers Docker.

## 🚀 Solução Implementada (Recomendada)

### Arquivos Criados:

1. **`docker-compose.yaml`** - Versão completa com container de inicialização
2. **`init-airflow.sh`** - Script de inicialização do Airflow
3. **`entrypoint-webserver.sh`** - Script de entrada para o webserver
4. **`entrypoint-scheduler.sh`** - Script de entrada para o scheduler

### Como Funciona:

1. **Container `airflow-init`**: 
   - Executa primeiro, com usuário `root`
   - Configura permissões 777 em todos os diretórios
   - Inicializa o banco de dados
   - Cria usuário admin

2. **Webserver e Scheduler**:
   - Executam scripts de entrada que verificam permissões
   - Garantem que as permissões estão corretas antes de iniciar

### Comandos para Usar:

```bash
# Parar containers existentes
docker-compose down

# Subir com a nova configuração
docker-compose up -d

# Verificar logs
docker-compose logs airflow-init
docker-compose logs airflow-webserver
docker-compose logs airflow-scheduler
```

## 🔧 Solução Alternativa (Simples)

### Arquivo: `docker-compose-simple.yaml`

Esta versão usa comandos inline para configurar permissões:

```bash
# Usar a versão simples
docker-compose -f docker-compose-simple.yaml up -d
```

## 📋 Características das Soluções

### Versão Completa (Recomendada):
✅ Separação clara de responsabilidades
✅ Scripts reutilizáveis
✅ Inicialização adequada do banco
✅ Criação automática do usuário admin
✅ Melhor para produção

### Versão Simples:
✅ Configuração mais direta
✅ Menos arquivos
✅ Mais fácil de entender
✅ Boa para desenvolvimento

## 🔐 Credenciais de Acesso

Após a inicialização, você pode acessar o Airflow em:

- **URL**: http://localhost:8080
- **Usuário**: admin
- **Senha**: admin

## 🛠️ Permissões Configuradas Automaticamente

Os scripts configuram as seguintes permissões:

```bash
chmod -R 777 /opt/airflow/dags
chmod -R 777 /opt/airflow/scripts  
chmod -R 777 /opt/airflow/data
chmod -R 777 /opt/airflow/dataquality
```

E também configuram ownership:

```bash
chown -R airflow:root /opt/airflow/dags
chown -R airflow:root /opt/airflow/scripts
chown -R airflow:root /opt/airflow/data
chown -R airflow:root /opt/airflow/dataquality
```

## 🔍 Troubleshooting

### Se houver problemas de permissão:

1. **Verificar logs**:
   ```bash
   docker-compose logs airflow-init
   ```

2. **Executar manualmente**:
   ```bash
   docker-compose exec airflow-webserver bash
   chmod -R 777 /opt/airflow
   ```

3. **Reiniciar containers**:
   ```bash
   docker-compose restart
   ```

### Se o usuário admin não for criado:

```bash
docker-compose exec airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

## 📁 Estrutura de Arquivos

```
docker/
├── docker-compose.yaml           # Versão completa
├── docker-compose-simple.yaml    # Versão simples
├── init-airflow.sh              # Script de inicialização
├── entrypoint-webserver.sh      # Script do webserver
├── entrypoint-scheduler.sh      # Script do scheduler
└── README-permissions.md        # Esta documentação
```
