# -*- coding: utf-8 -*-
import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import boto3


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ProductsList')

# Handler for CheckProductAvailabilityIntent
class CheckProductAvailabilityIntentHandler(AbstractRequestHandler):
    """Handler for CheckProductAvailabilityIntent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CheckProductAvailabilityIntent")(handler_input)

    def handle(self, handler_input):
        product_name = handler_input.request_envelope.request.intent.slots['ProductName'].value
        locale = handler_input.request_envelope.request.locale
        response = table.get_item(Key={'ProductName': product_name})
        try:
            if 'Item' in response:
                brand = response['Item'].get('Brand', 'unknown brand')
                quantity = response['Item'].get('Quantity', 'unknown quantity')
                category = response['Item'].get('Category', 'unknown category')
                if locale.startswith("pt"):
                    speech_text = f"sim, temos {quantity} unidades {product_name} disponíveis, da marca {brand} , categoria {category}"
                else:
                    speech_text = f"Yes, {product_name} is available. It is from {brand}, we have {quantity} units in the {category} category."
            else:
                if locale.startswith("pt"):
                    speech_text = f"Desculpa, {product_name} não está disponível no estoque"
                else:
                    speech_text = f"Sorry, {product_name} is not available in the store."
        except Exception as e:
            if locale.startswith("pt"):
                speech_text = f"erro verificando {product_name}."
            else:
                speech_text = f"An error occurred while checking availability for {product_name}."
        return handler_input.response_builder.speak(speech_text).response

# Handler for ListAllProductsIntent
class ListAllProductsIntentHandler(AbstractRequestHandler):
    """Handler for ListAllProductsIntent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ListAllProductsIntent")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        # Scan the table for all products
        try:
            response = table.scan()
            items = response.get('Items', [])

            if items:
                product_names = [item['ProductName'] for item in items]
                product_list = ', '.join(product_names)
                if locale.startswith("pt"):
                    speech_text = f"Os produtos disponíveis são: {product_list}."
                else:
                    speech_text = f"The available products are: {product_list}."
            else:
                if locale.startswith("pt"):
                    speech_text = "Não há produtos disponíveis no momento"
                else:
                    speech_text = "There are no products available at the moment."

        except Exception as e:
            logger.error(e, exc_info=True)
            if locale.startswith("pt"):
                speech_text = "Ops, deu erro"
            else:
                speech_text = "An error occurred while listing the products."

        return handler_input.response_builder.speak(speech_text).response

# Handler for LaunchRequest (initial welcome message)
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        speak_output = self.get_speak_output(locale)
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

    def get_speak_output(self, locale):
        if locale.startswith("en"):
            return "Welcome to Store. You can ask for a specific item, category or brand."
        elif locale.startswith("pt"):
            return "Bem vindo à loja"
        # Add more languages as needed
        else:
            return "Welcome to Store. You can ask for a specific item, category or brand."


# General SkillBuilder configuration
sb = SkillBuilder()

# Add custom handlers for intents
sb.add_request_handler(CheckProductAvailabilityIntentHandler())
sb.add_request_handler(ListAllProductsIntentHandler())
sb.add_request_handler(LaunchRequestHandler())

# Add exception handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        locale = handler_input.request_envelope.request.locale
        logger.error(exception, exc_info=True)
        if locale.startswith("en"):
            speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        if locale.startswith("pt"):
            speak_output = "Desculpa, não consegui entender. Tente novamente, por favor."
        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

sb.add_exception_handler(CatchAllExceptionHandler())

# The actual handler for the Lambda function
handler = sb.lambda_handler()
