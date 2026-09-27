import os
import logging
import traceback

import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler

from dotenv import load_dotenv
load_dotenv()

from groq import Groq


# ============================================================
# CONFIGURAÇÃO DA GROQ
# ============================================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """
Você é o Kai Inteligente, um assistente pessoal usado através da Alexa.
Responda sempre em português brasileiro.
As respostas serão faladas pela Alexa.
Não use Markdown, emojis, tabelas ou símbolos desnecessários.
Seja natural, claro e direto.
"""


# ============================================================
# LOG
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# FUNÇÃO PARA PERGUNTAR À GROQ
# ============================================================

def perguntar_groq(pergunta):

    try:
        logger.info("Pergunta recebida: %s", pergunta)

        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": pergunta}
            ],
            temperature=1,
            max_completion_tokens=500,
            top_p=1,
            stream=False
        )

        resposta = completion.choices[0].message.content

        if not resposta:
            return "Desculpe, não consegui obter uma resposta."

        logger.info("Resposta recebida com sucesso.")
        return resposta.strip()

    except Exception as erro:
        logger.exception("Erro ao consultar a Groq: %s", erro)
        # Temporariamente devolvendo o erro real, pra debug
        return f"Erro na Groq: {type(erro).__name__}: {erro}"[:400]


# ============================================================
# ABRIR A SKILL
# ============================================================

class LaunchRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        mensagem = "Olá! Aqui é o Kai Inteligente. Pode fazer sua pergunta."
        return (
            handler_input.response_builder
            .speak(mensagem)
            .ask("Qual é a sua pergunta?")
            .response
        )


# ============================================================
# INTENT DA PERGUNTA
# ============================================================

class GeminiIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GeminiIntent")(handler_input)

    def handle(self, handler_input):
        pergunta = ask_utils.get_slot_value(handler_input, "query")

        if not pergunta:
            return (
                handler_input.response_builder
                .speak("Não entendi sua pergunta. Pode repetir?")
                .ask("Qual é a sua pergunta?")
                .response
            )

        resposta = perguntar_groq(pergunta)

        return (
            handler_input.response_builder
            .speak(resposta)
            .set_should_end_session(True)
            .response
        )


# ============================================================
# HELP
# ============================================================

class HelpIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        mensagem = "Você pode me fazer uma pergunta sobre qualquer assunto."
        return (
            handler_input.response_builder
            .speak(mensagem)
            .ask("Qual é a sua pergunta?")
            .response
        )


# ============================================================
# CANCELAR / PARAR
# ============================================================

class CancelOrStopIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return (
            ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
            or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)
        )

    def handle(self, handler_input):
        return (
            handler_input.response_builder
            .speak("Até mais!")
            .response
        )


# ============================================================
# SESSÃO ENCERRADA
# ============================================================

class SessionEndedRequestHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


# ============================================================
# CAPTURADOR DE ERROS GERAL (COM DETALHE DO ERRO, TEMPORÁRIO)
# ============================================================

class CatchAllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(traceback.format_exc())
        mensagem = f"Erro: {type(exception).__name__}: {exception}"[:400]
        return (
            handler_input.response_builder
            .speak(mensagem)
            .response
        )


# ============================================================
# CONSTRUÇÃO DA SKILL
# ============================================================

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GeminiIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()