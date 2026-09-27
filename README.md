# Kai Inteligente — Assistente por Voz na Alexa

Alexa Skill que funciona como um assistente pessoal por voz: o usuário faz uma pergunta falando com a Alexa, e a skill responde usando um modelo de linguagem (LLM) via API da Groq.

## Como funciona

```
Usuário fala com a Alexa
        ↓
Alexa Skills Kit (reconhece o intent e a pergunta)
        ↓
AWS Lambda (Python) — lambda_function.py
        ↓
API da Groq (LLM: openai/gpt-oss-120b)
        ↓
Resposta é falada de volta pela Alexa
```

1. O usuário abre a skill e faz uma pergunta.
2. O modelo de interação (`interactionModels/custom/pt-BR.json`) reconhece a intenção (`GeminiIntent`) e captura a pergunta como slot.
3. A função Lambda envia a pergunta para a API da Groq, com um prompt de sistema que define o tom das respostas (direto, sem markdown, adequado para ser falado).
4. A resposta do modelo é devolvida como fala pela Alexa.

## Tecnologias utilizadas

- **Python** — linguagem principal da skill
- **ASK SDK (Alexa Skills Kit)** — framework oficial para construção de skills
- **AWS Lambda** — hospeda e executa a lógica da skill (serverless)
- **Groq API** — inferência do modelo de linguagem que gera as respostas
- **boto3 / Amazon S3** — geração de URLs pré-assinadas para acesso a arquivos
- **python-dotenv** — gerenciamento de variáveis de ambiente em desenvolvimento local

## Estrutura do projeto

```
kai-inteligente-alexa-skill/
├── interactionModels/
│   └── custom/
│       └── pt-BR.json       # Modelo de interação (intents, slots, utterances)
├── lambda/
│   ├── lambda_function.py   # Handlers da skill e integração com a Groq
│   ├── utils.py             # Funções auxiliares (ex.: URLs pré-assinadas do S3)
│   ├── requirements.txt     # Dependências Python
│   └── .env.example         # Variáveis de ambiente necessárias (sem valores reais)
├── skill.json                # Manifest da skill (metadados, categoria, permissões)
└── README.md
```

## Como rodar / testar

1. Crie uma skill no [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask) e importe o modelo de interação em `interactionModels/custom/pt-BR.json`.
2. Crie uma função no AWS Lambda com o código de `lambda/lambda_function.py` e `lambda/utils.py`.
3. Instale as dependências listadas em `lambda/requirements.txt` na Lambda (via camada/layer ou pacote de deploy).
4. Configure as variáveis de ambiente da Lambda com base no `lambda/.env.example`:
   - `GROQ_API_KEY` — chave de API da [Groq](https://console.groq.com)
   - `S3_PERSISTENCE_REGION` — região do bucket S3 usado
   - `S3_PERSISTENCE_BUCKET` — nome do bucket S3 usado
5. Vincule o ARN da função Lambda ao endpoint da skill no Alexa Developer Console.
6. Teste pelo simulador do próprio console ou em um dispositivo Alexa habilitado para testes.

## Possíveis melhorias futuras

- Tratar erros com mensagens genéricas para o usuário final, mantendo o log técnico apenas nos logs do CloudWatch.
- Adicionar suporte a sessão contínua (permitir perguntas de acompanhamento sem reabrir a skill).
- Expandir os testes automatizados dos handlers.

---

Projeto desenvolvido por [Robson Ramos](https://github.com/kaia-boo) como parte de estudos em automação, APIs e integração com serviços em nuvem (AWS).
