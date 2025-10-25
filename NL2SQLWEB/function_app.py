import sys
import asyncio

# CRITICAL: Force event loop policy BEFORE Azure Functions framework loads
if sys.platform == "win32":
    try:
        # Close any existing event loop
        try:
            loop = asyncio.get_running_loop()
            if hasattr(loop, 'close'):
                loop.close()
        except RuntimeError:
            pass  # No running loop
        
        # Force the correct policy
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Create new event loop with correct policy
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        
        print("Forced WindowsSelectorEventLoopPolicy and new event loop for Azure Functions")
    except Exception as e:
        print(f"Error setting event loop policy: {e}")

import azure.functions as func
import json
import logging
import os
import dotenv

from nl2sql import AutoGenText2SqlRunner  # Provided by NL2SQL library

dotenv.load_dotenv(override=False)

# Instantiate once (warm start reuse)
runner = AutoGenText2SqlRunner(use_case=os.getenv("NL2SQL_USE_CASE", "query Rubicon product data"))

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def ensure_json_serializable(obj):
    """Recursively ensure all data is JSON serializable and properly encoded"""
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [ensure_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(k): ensure_json_serializable(v) for k, v in obj.items()}
    else:
        return str(obj)


def _json_response(status: int, body: dict) -> func.HttpResponse:
    # Ensure the body is completely JSON serializable
    safe_body = ensure_json_serializable(body)
    
    return func.HttpResponse(
        json.dumps(safe_body, ensure_ascii=False, indent=2),  # Added indent for better readability
        status_code=status,
        mimetype="application/json; charset=utf-8",  # Explicitly set charset
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@app.function_name(name="ProcessUserMessage")
@app.route(route="nl2sql", methods=["POST"])
async def process_user_message(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except ValueError:
        return _json_response(400, {"error": "Invalid JSON"})

    message = body.get("message")
    thread_id = body.get("thread_id", "default")

    if not message or not isinstance(message, str):
        return _json_response(400, {"error": "'message' must be a non-empty string"})

    logging.info("Received request thread_id=%s message=%s", thread_id, message)

    try:
        result = await runner.run(thread_id=thread_id, message=message)
        
        # Comment out logging to avoid large outputs
        # logging.info(f"Runner result: {result}")

        
        if result.get("final") is None:
            # Pipeline ended without a final answer
            return _json_response(
                500, {"error": "No final payload produced", "updates": result.get("updates", [])}
            )
        
        # Extract components from result
        final = result.get("final", {})
        sql_results_raw = result.get("sql_results")  # This is already extracted by nl2sql_run.py
        
        # Ensure SQL results are properly serializable
        sql_results = ensure_json_serializable(sql_results_raw) if sql_results_raw else None
        
        # Comment out logging to avoid large outputs
        # logging.info(f"SQL results from runner: {sql_results}")
        
        # Initialize response data with the extracted SQL results
        response_data = {
            "thread_id": str(result["thread_id"]),
            "message": str(message),
            "answer": "",
            "sql_results": sql_results,  # Use the cleaned results
            "success": False
        }
        
        # Extract the human-readable answer if available
        payload_type = final.get("payloadType")
        logging.info(f"Payload type: {payload_type}")
        
        if payload_type == "answer_with_sources":
            body_data = final.get("body", {})
            answer_text = body_data.get("answer", "")
            response_data["answer"] = str(answer_text) if answer_text else ""
            # Comment out logging to avoid large outputs
            # logging.info(f"Extracted answer: {response_data['answer']}")
        elif final.get("payload_type") == "answer_with_sources":  # Try snake_case too
            body_data = final.get("body", {})
            answer_text = body_data.get("answer", "")
            response_data["answer"] = str(answer_text) if answer_text else ""
            # Comment out logging to avoid large outputs
            # logging.info(f"Extracted answer (snake_case): {response_data['answer']}")
        else:
            # If we can't get the answer from the expected structure, try to extract it from any text content
            logging.warning(f"Unexpected payload type: {payload_type}")
            
            # Look for answer in various places
            if isinstance(final, dict):
                # Check if there's an answer field directly
                if "answer" in final:
                    response_data["answer"] = str(final["answer"])
                # Check if there's a body with answer
                elif "body" in final and isinstance(final["body"], dict) and "answer" in final["body"]:
                    response_data["answer"] = str(final["body"]["answer"])
                # Check for any string that looks like an answer
                elif "content" in final:
                    response_data["answer"] = str(final["content"])
        
        # Set success based on whether we have SQL results with actual data
        if sql_results and isinstance(sql_results, dict):
            rows = sql_results.get("rows", [])
            queries = sql_results.get("queries", [])
            response_data["success"] = len(rows) > 0 and len(queries) > 0
        
        # Final cleanup to ensure everything is JSON serializable
        response_data = ensure_json_serializable(response_data)

        # Comment out logging to avoid large outputs
        # logging.info(f"Final response data: {response_data}")

        # Log the types to debug serialization
        if response_data.get("sql_results"):
            logging.info(f"SQL queries type: {type(response_data['sql_results'].get('queries'))}")
            logging.info(f"SQL rows type: {type(response_data['sql_results'].get('rows'))}")
        
        return _json_response(200, response_data)
        
    except Exception as e:
        logging.exception("Unhandled error in NL2SQL Function")
        return _json_response(500, {"error": str(e)})
