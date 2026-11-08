# Roteiro de teste com usuários

Tempo: cerca de 10 minutos por pessoa. Quem testa: **5 pessoas de fora do grupo** (PCP pede no mínimo 3 pessoas e 10 atendimentos; PAI pede 5 pessoas cronometradas). As mesmas 5 pessoas servem para os dois.

Regras: não anote nome, telefone nem documento (use P1 a P5). Não ajude a pessoa durante a tarefa. Dê um cronômetro (celular) a quem anota.

## Parte A: terminal (vale para PCP e ERS)

1. Abra o terminal na pasta do projeto e rode `python main.py`.
2. Peça à pessoa que faça **3 perguntas com as palavras dela**, sobre documentos ou direitos. Peça que uma das perguntas seja sobre **conta de luz ou economia de energia** (isso é o registro de teste do ERS).
3. Ao sair (opção 0), o programa pede a nota de facilidade de 1 a 5. A pessoa digita.
4. O programa grava tudo sozinho em `data/historico.json` e `data/atendimentos.csv`. Com 5 pessoas e 3 perguntas cada, são 15 atendimentos.

## Parte B: cronometrado (vale para PAI)

Abra `Abrir_Aurora_Cidada.html`, aba **Assistente**. Peça à pessoa que cumpra as 3 tarefas, uma de cada vez, e cronometre do início até ela achar a resposta.

| Tarefa | O que a pessoa deve descobrir |
|---|---|
| 1 | O que levar para a 2ª via do RG em caso de perda |
| 2 | Quanto custa e quanto tempo leva a 2ª via da certidão de nascimento pelo portal |
| 3 | Se outra pessoa pode retirar a certidão e o que ela precisa apresentar |

Anote em `folha_pai.csv`, uma linha por pessoa: tempo em segundos de cada tarefa (`tarefa1_s`...), se concluiu (`s` ou `n`) e as 5 notas do questionário.

## Questionário (notas de 1 a 5, depois do teste)

1. Foi fácil começar a usar?
2. As respostas foram claras?
3. Você confiaria nessa informação, sabendo que o assistente não é canal oficial?
4. Achou o que procurava rápido?
5. Usaria de novo?

## Depois dos testes

1. Veja as perguntas que não foram resolvidas (aparecem em "dúvidas sem solução" no fim do `main.py`). **Faça uma melhoria de verdade** a partir delas, por exemplo, uma palavra-chave nova em `data/base_conhecimento.json`. O PCP exige uma melhoria feita a partir do teste.
2. Rode, na pasta do projeto:

   `python testes_usuarios/resumo_testes.py --pessoas 5 --melhoria "descreva a melhoria que você fez"`

   Isso atualiza a seção 5 do README e cria `testes_usuarios/PAI_resultados.md` com a tabela e os indicadores do relatório de PAI.
3. Passe os números de `PAI_resultados.md` para o relatório de PAI (seção 6) e gere o PDF de novo.
