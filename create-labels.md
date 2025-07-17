# 🏷️ Criação de Labels para o Repositório

## Como criar as labels necessárias no GitHub

### 1. Via Interface Web do GitHub

Acesse: `https://github.com/leozancheta/data-ingestion-beers/labels`

Clique em "New label" e crie as seguintes:

#### 📋 Labels Necessárias:

1. **automated-pr**
   - Cor: `#0e8a16` (verde)
   - Descrição: `Pull request criada automaticamente`

2. **tests-passed** 
   - Cor: `#28a745` (verde claro)
   - Descrição: `Todos os testes unitários passaram`

3. **ready-for-review**
   - Cor: `#0075ca` (azul)
   - Descrição: `Pronto para revisão de código`

4. **do-not-auto-merge**
   - Cor: `#d93f0b` (vermelho)
   - Descrição: `Não fazer merge automático - requer revisão manual`

### 2. Via GitHub CLI (após instalar e fazer login)

```bash
# Fazer login no GitHub CLI
gh auth login --web

# Criar as labels
gh label create "automated-pr" --description "Pull request criada automaticamente" --color "0e8a16"
gh label create "tests-passed" --description "Todos os testes unitários passaram" --color "28a745"
gh label create "ready-for-review" --description "Pronto para revisão de código" --color "0075ca"
gh label create "do-not-auto-merge" --description "Não fazer merge automático - requer revisão manual" --color "d93f0b"
```

### 3. Status Atual dos Workflows

✅ **python-test.yaml**: Corrigido para usar label padrão `enhancement`
✅ **auto-pr.yaml**: Corrigido para usar label padrão `enhancement`

Os workflows agora funcionam mesmo sem as labels personalizadas, mas se você quiser o visual completo, crie as labels usando o método 1 ou 2 acima.

### 4. Como Verificar se Funcionou

Depois de criar as labels, faça um commit em uma branch feature:

```bash
git add .
git commit -m "test: verificando labels nas PRs automáticas"
git push origin feature/ajusts
```

O workflow deve rodar sem erros e aplicar as labels corretamente.
