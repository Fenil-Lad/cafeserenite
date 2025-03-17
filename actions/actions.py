# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List
import json
from typing import Dict, Text, Any, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

logger = logging.getLogger(__name__)


class handleInformationQueries(Action):
    def name(self) -> Text:
        return "handle_information_queries"
    
    def run(self, dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest user intent
        latest_intent = tracker.latest_message.get("intent", {}).get("name")
        logger.info(f"Latest user intent: {latest_intent}")
        
        # Path to the JSON file
        file_path = "info.json"
        
        try:
            logger.info(f"Attempting to read JSON file: {file_path}")
            with open(file_path, "r") as file:
                info_data = json.load(file)
            logger.info("JSON file read successfully.")
            
            # Extract cafe information
            cafe_info = info_data.get("cafe_info", {})
            intents_info = cafe_info.get("intents", {})
            
            # Check if the intent exists in the JSON
            if latest_intent in intents_info:
                intent_data = intents_info[latest_intent]
                response = self.format_response(latest_intent, intent_data)
                
                # Ensure the response is not empty or None
                if response and isinstance(response, str):
                    logger.info(f"Sending response: {response}")
                    dispatcher.utter_message(text=response)
                else:
                    logger.error("Generated response is empty or invalid.")
                    dispatcher.utter_message(text="Sorry, I couldn't generate a valid response.")
            else:
                logger.warning(f"Intent '{latest_intent}' not found in JSON.")
                dispatcher.utter_message(text="I'm not sure how to help with that. Can you please rephrase?")
        
        except FileNotFoundError:
            logger.error("The info file was not found.")
            dispatcher.utter_message(text="The info file was not found.")
        except json.JSONDecodeError:
            logger.error("The info file is not valid JSON.")
            dispatcher.utter_message(text="The info file is not valid JSON.")
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")
        
        return []
    
    def format_response(self, intent: Text, intent_data: Dict[Text, Any]) -> Text:
        """
        Formats the response based on the intent and its data.
        """
        try:
            if intent == "ask_menu":
                categories = intent_data.get("categories", {})
                response = "Here's our menu:\n"
                for category, items in categories.items():
                    response += f"- {category.capitalize()}: {', '.join(items)}\n"
                return response.strip()
            
            elif intent == "ask_recommendations":
                popular_items = intent_data.get("popular_items", [])
                seasonal_special = intent_data.get("seasonal_special", "")
                response = f"Customer favorites: {', '.join(popular_items)}\n"
                response += f"Seasonal special: {seasonal_special}"
                return response.strip()
            
            elif intent == "ask_dietary_options":
                options = intent_data.get("available_options", [])
                note = intent_data.get("note", "")
                response = f"We offer the following dietary options: {', '.join(options)}\n"
                response += f"Note: {note}"
                return response.strip()
            
            elif intent == "place_order":
                methods = intent_data.get("methods", [])
                delivery_minimum = intent_data.get("delivery_minimum", "")
                response = f"You can place an order using the following methods:\n"
                response += "\n".join([f"- {method}" for method in methods]) + "\n"
                response += f"Delivery minimum: {delivery_minimum}"
                return response.strip()
            
            elif intent == "customize_order":
                options = intent_data.get("options", [])
                response = "You can customize your order with the following options:\n"
                response += "\n".join([f"- {option}" for option in options])
                return response.strip()
            
            elif intent == "ask_hours":
                hours = intent_data.get("hours", {})
                response = "Our operating hours are:\n"
                response += f"- Weekdays: {hours.get('weekdays', 'N/A')}\n"
                response += f"- Weekends: {hours.get('weekends', 'N/A')}\n"
                response += f"- Holidays: {hours.get('holidays', 'N/A')}"
                return response.strip()
            
            elif intent == "ask_location":
                address = intent_data.get("address", "N/A")
                landmark = intent_data.get("landmark", "N/A")
                response = f"Find us at: {address}\n"
                response += f"Landmark: {landmark}"
                return response.strip()
            
            elif intent == "ask_discounts":
                offers = intent_data.get("offers", [])
                response = "Current promotions and deals:\n"
                response += "\n".join([f"- {offer}" for offer in offers])
                return response.strip()
            
            elif intent == "reserve_table":
                methods = intent_data.get("methods", [])
                group_limit = intent_data.get("group_limit", "")
                response = "You can reserve a table using the following methods:\n"
                response += "\n".join([f"- {method}" for method in methods]) + "\n"
                response += f"Group limit: {group_limit}"
                return response.strip()
            
            elif intent == "payment_methods":
                methods = intent_data.get("methods", [])
                response = "We accept the following payment methods:\n"
                response += "\n".join([f"- {method}" for method in methods])
                return response.strip()
            
            elif intent == "delivery_options":
                partners = intent_data.get("partners", [])
                radius = intent_data.get("radius", "")
                response = "We offer delivery through the following partners:\n"
                response += "\n".join([f"- {partner}" for partner in partners]) + "\n"
                response += f"Delivery radius: {radius}"
                return response.strip()
            
            elif intent == "report_issue":
                contact = intent_data.get("contact", {})
                response = "If you have any issues, please contact us:\n"
                response += f"- Phone: {contact.get('phone', 'N/A')}\n"
                response += f"- Email: {contact.get('email', 'N/A')}\n"
                response += f"Response time: {contact.get('response_time', 'N/A')}"
                return response.strip()
            
            else:
                return "I'm not sure how to help with that. Can you please rephrase?"
        
        except Exception as e:
            logger.error(f"Error formatting response for intent '{intent}': {str(e)}")
            return None


class HandleMenuQueries(Action):
    def name(self) -> Text:
        return "handle_menu_queries"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Path to the JSON file
        file_path = "menu.json"
        
        try:
            # Open and read the JSON file
            with open(file_path, "r") as file:
                menu_data = json.load(file)
            
            # Convert the JSON data to a formatted string
            formatted_menu = json.dumps(menu_data, indent=4)
            
            # Send the formatted JSON as a message
            dispatcher.utter_message(text=formatted_menu)
        
        except FileNotFoundError:
            dispatcher.utter_message(text="The menu file was not found.")
        except json.JSONDecodeError:
            dispatcher.utter_message(text="The menu file is not valid JSON.")
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {str(e)}")
        
        return []
    
    
class HandleTrackOrder(Action):
    def name(self) -> str:
        return "handle_track_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Log the entities in the tracker to debug
        logger.info("Entities in the tracker: %s", tracker.latest_message['entities'])

        # Get the order number entity
        order_number = next(tracker.get_latest_entity_values("order_number"), None)

        if order_number:
            order_status = "On its way!"  # Example status
            dispatcher.utter_message(text=f"Your order {order_number} is {order_status}.")
        else:
            dispatcher.utter_message(text="I couldn't find your order number. Can you please provide it again?")

        return []

    
class HandleReportIssue(Action):
    def name(self) -> str:
        return "handle_report_issue"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        # Retrieve the values from the slots
        order_number = tracker.get_slot("order_number")
        issue = tracker.get_slot("issue")
        contact_method = tracker.get_slot("contact_method")

        # You can replace this with your system or API call to process the issue
        # For now, we'll send a confirmation message
        dispatcher.utter_message(
            text=f"Thank you for reporting the issue. Here's a summary of your report:\n"
                 f"Order Number: {order_number}\n"
                 f"Issue: {issue}\n"
                 f"Contact Method: {contact_method}\n"
                 "We will look into it and get back to you soon."
        )

        return []
    
class ActionCaptureFullMessage(Action):
    def name(self) -> str:
        return "action_capture_full_message"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
        # Capture the entire user message
        full_message = tracker.latest_message.get('text')
        # Store the full message in the slot
        return [SlotSet("full_message", full_message)]