# Avaliação do Uso de LLMs para Resolução de Issues no GitHub.

## Autores
- Ana Lucia Oliveira de Paula  
- Eduarda Mendes Pinto Barbosa  
- Frederico Dolher Souza Baker  
- Lucas Silva Viana  
- Pedro Henrique Freitas Guedes Oliveira  

## Objetivo
Nosso objetivo é investigar como modelos de linguagem podem auxiliar na manutenção e evolução de software*, especialmente na resolução de issues de projetos reais. Desejamos verificar se as LLMs conseguem produzir alterações de código com qualidade comparável à de desenvolvedores experientes, bem como analisar eventuais limitações.

## Metodologia

### Modelo de Linguagem
Utilizaremos o [Cline](https://github.com/cline/cline), um *wrapper* que integra a API de uma LLM (GPT-4, no nosso caso) e oferece recursos para lidar com contextos extensos, múltiplos arquivos e testes. Ele se destaca pela forma como gerencia o contexto de um projeto:
1. **Análise automática**: vasculha a estrutura do repositório, lê arquivos relevantes e mapeia dependências.  
2. **Interação direta com o usuário**: permite fornecer arquivos específicos, documentações e anotações adicionais.  

O Cline também possibilita rodar testes localmente após fazer alterações sugeridas pela LLM, o que facilita avaliar se uma solução realmente corrige o problema.

### Dataset
Para avaliar a efetividade do modelo, usaremos o [SWE-bench](https://www.swebench.com) ([paper](https://arxiv.org/abs/2310.06770)), lançado em 10 de outubro de 2023. Trata-se de um *benchmark* com 2294 *issues* extraídas de 12 repositórios Python populares, cada *issue* é acompanhada de um *pull request* que a solucionou. No paper, o melhor resultado reportado até então foi do modelo Claude 2, que resolveu apenas 1,96% das *issues* de forma totalmente automática.  
Ao aplicarmos o GPT-4 por meio do Cline, esperamos verificar se resultados mais expressivos podem ser obtidos, considerando que o GPT-4 possui capacidades avançadas de raciocínio e geração de código.

### Exemplos de *Prompts*
O *prompt* padrão que enviaremos ao Cline incluirá:
- Descrição da *issue*.  
- Contexto do projeto selecionado automaticamente pelo Cline (arquivos, trechos de código relevantes).  
- Instruções para modificar o código a fim de corrigir a *issue* ou melhorar o projeto.  

Exemplo (resumido):
```
[Arquivos e contexto reunidos pelo Cline]

Issue: "Enable quiet mode/no-verbose in CLI for use in pre-commit hook
There seems to be only an option to increase the level of verbosity when using SQLFluff..."
```
O Cline, então, gera alterações no código, podendo até compilar e rodar testes para validar suas sugestões.

### Avaliação Quantitativa
Depois de aplicarmos as alterações sugeridas pela LLM, vamos executar toda a suite de testes do repositório para verificar se:
 - A issue em questão foi efetivamente corrigida, fazendo com que testes anteriormente quebrados (ou criados especificamente para a correção) sejam aprovados.
 - Não houve regressão em outros componentes, ou seja, os testes que já passavam continuam passando.
Dessa forma, o número de testes que passam (em relação ao estado anterior às alterações) é um indicador objetivo da eficácia da proposta gerada pela LLM.

### Avaliação Qualitativa
1. **Amostragem manual**: escolheremos algumas *issues* para comparar a proposta do modelo com a solução do desenvolvedor real.  
2. **Critérios de análise**:  
   - Clareza do código gerado;  
   - Segue boas práticas;  
   - Possíveis regressões ou problemas de performance;  
   - Se aprovaríamos o PR.
