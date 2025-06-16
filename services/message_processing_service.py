from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, Any
import json

from database import models
from database.database import get_db
from api.schemas import MessageLogCreate, MessageLog
from api.schemas import Employee
from services.message_log_service import MessageLogService, get_message_log_service
from services.employee_service import EmployeeService, get_employee_service
from services.query_interpreter_service import QueryInterpreterService
from services.database_query_builder_service import DatabaseQueryBuilder

from fastapi import Depends


class MessageProcessingService:
    def __init__(self, db: Session,
                 message_log_service: MessageLogService,
                 employee_service: EmployeeService):
        """
        Initializes the MessageProcessingService with a db-session
        and dependencies to other services.
        """

        self.db = db
        self.message_log_service = message_log_service
        self.employee_service = employee_service
        self.query_interpreter = QueryInterpreterService()
        self.db_query_builder = DatabaseQueryBuilder(db)


    async def process_inbound_message(
        self,
        employee_id: Optional[UUID],
        raw_message_content: str,
        phone_number: Optional[str]
    ) -> MessageLog:
        """
        Processes an inbound message.
        Saves message to MessageLog Table.
        """

        system_response_content : Optional[str] = None  # This will hold the bot's final response

        # 1. Get employee info for personalized responses
        employee_name_for_response = "there"
        if employee_id:
            employee_orm = self.employee_service.get_employee_by_id(employee_id)
            if employee_orm and employee_orm.name:
                employee_name_for_response = employee_orm.name.split(' ')[0]

        # 2. Ask the LLM to interpret the user's query
        llm_query_intent = await self.query_interpreter.interpret_query(raw_message_content)

        # 3. Check if the LLM reported an error
        if "error" in llm_query_intent and llm_query_intent["error"]:
            system_response_content = f"Sorry {employee_name_for_response}, I couldn't understand your request: {llm_query_intent['error']}"
        else:
            # 4. Execute database query based on the LLM's intent
            try:
                db_results = self.db_query_builder.execute_query(llm_query_intent)

                if db_results and isinstance(db_results, list) and db_results and isinstance(db_results[0], dict) and "error" in db_results[0]:
                    system_response_content = f"Sorry {employee_name_for_response}, an error occurred while querying the database: {db_results[0]['error']}"

                # Special handling for counting requests
                # Checks whether it was the intent to gett all ID's for counting
                elif llm_query_intent.get("action") == "get_data" and \
                     llm_query_intent.get("columns") == ["id"] and \
                     llm_query_intent.get("filters") == {}:
                    # counting of actual length of returned results
                    count = len(db_results)
                    # Formatting of response
                    system_response_content = f"There are {count} {llm_query_intent.get('table', 'items').rstrip('s')}s in the database, {employee_name_for_response}."

                # General handling when nothing was found (for all requests)
                elif not db_results:
                    system_response_content = f"Sorry {employee_name_for_response}, I couldn't find any information matching your request."

                elif db_results:
                    formatted_results = []
                    for item in db_results:
                        item_str = ", ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in item.items())
                        formatted_results.append(item_str)

                    system_response_content = f"Here is the information you requested, {employee_name_for_response}:\n" + "\n".join(
                        formatted_results)

                else:
                    system_response_content = f"Sorry {employee_name_for_response}, I couldn't find any information matching your request."

            except Exception as e:
                print(f"ERROR: Unexpected error during database lookup: {e}")
                system_response_content = f"Sorry {employee_name_for_response}, an unexpected error occurred during the database lookup: {e}"

        # 5. Save the inbound message AND the generated system response to the database
        # This creates ONE log entry containing both parts of the interaction.
        message_log_data = MessageLogCreate(
            employee_id=employee_id,
            direction=models.MessageDirection.inbound,
            raw_message_content=raw_message_content,
            status=models.MessageStatus.received,
            phone_number=phone_number,
            system_response_content=system_response_content
        )

        db_message_log = self.message_log_service.create_message_log(message_log_data=message_log_data)

        print(f"Inbound message logged (ID: {db_message_log.id}): '{raw_message_content}'")
        print(f"System response generated: '{system_response_content}'")

        return db_message_log

# Dependency for FastAPI-Router or Bot
def get_message_processing_service(
    db: Session = Depends(get_db),
    message_log_service: MessageLogService = Depends(get_message_log_service),
    employee_service: EmployeeService = Depends(get_employee_service)
) -> MessageProcessingService:
    """
    Dependency that returns an instance of MessageProcessingService.
    """
    return MessageProcessingService(db=db,
                                    message_log_service=message_log_service,
                                    employee_service=employee_service)