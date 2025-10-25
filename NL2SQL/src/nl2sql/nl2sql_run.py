from .autogen_nl2sql import AutoGenText2Sql, UserMessagePayload
from .autogen_nl2sql.state_store import InMemoryStateStore
from .nl2sql_core.payloads.interaction_payloads import PayloadType
import logging

class AutoGenText2SqlRunner:
    def __init__(self, use_case: str = "query Sumsung's product data", state_store=None):
        self.state_store = state_store or InMemoryStateStore()
        self.engine = AutoGenText2Sql(state_store=self.state_store, use_case=use_case)

    async def run(self, thread_id: str, message: str):
        payloads = []
        msg_payload = UserMessagePayload(user_message=message)
        
        # Store the final payload object for SQL extraction
        final_payload_object = None
        
        async for payload in self.engine.process_user_message(thread_id, msg_payload):
            if payload.payload_type == PayloadType.PROCESSING_UPDATE:
                payloads.append({
                    "type": "processing_update",
                    "title": getattr(payload.body, "title", "Processing..."),
                    "message": getattr(payload.body, "message", ""),
                })
            else:
                # final message - store the payload object
                final_payload_object = payload
                
                if hasattr(payload, "model_dump"):
                    final_dump = payload.model_dump()
                    
                    # Extract SQL query results using both the payload object and dump
                    sql_results = self._extract_sql_results(final_dump, final_payload_object)
                    
                    # Comment out logging to reduce noise
                    # logging.info(f"Final dump structure: {final_dump}")
                    # logging.info(f"Extracted SQL results: {sql_results}")

                    return {
                        "thread_id": thread_id,
                        "updates": payloads,
                        "final": final_dump,
                        "sql_results": sql_results
                    }
                else:
                    final_dump = {"payload_type": payload.payload_type.value}
                    return {
                        "thread_id": thread_id,
                        "updates": payloads,
                        "final": final_dump,
                        "sql_results": None
                    }
        # Should always return in loop; fallback:
        return {"thread_id": thread_id, "updates": payloads, "final": None, "sql_results": None}

    def _extract_sql_results(self, final_dump: dict, payload_object=None) -> dict:
        """Extract SQL query results from the final payload."""
        try:
            logging.info(f"Extracting SQL results from payload type: {final_dump.get('payloadType')}")
            
            # Try to extract from the payload object directly first
            if payload_object and hasattr(payload_object, 'body') and hasattr(payload_object.body, 'sources'):
                sources = payload_object.body.sources
                logging.info(f"Found {len(sources)} sources in payload object")
                
                if sources:
                    sql_queries = []
                    all_rows = []
                    
                    for source in sources:
                        sql_query = getattr(source, 'sql_query', None)
                        sql_rows = getattr(source, 'sql_rows', [])

                        # Comment out logging to reduce noise
                        # logging.info(f"Source SQL Query: {sql_query}")
                        # logging.info(f"Source SQL Rows: {sql_rows}")

                        if sql_query:
                            sql_queries.append(sql_query)
                            if sql_rows:
                                all_rows.extend(sql_rows)
                    
                    result = {
                        "queries": sql_queries,
                        "rows": all_rows,
                        "total_rows": len(all_rows),
                        "queries_executed": len(sql_queries)
                    }
                    # Comment out logging to reduce noise
                    # logging.info(f"Extracted SQL results from object: {result}")
                    return result
            
            # Fallback: try to extract from the dumped dictionary
            if final_dump.get("payloadType") == "answer_with_sources":
                body = final_dump.get("body", {})
                sources = body.get("sources", [])
                
                logging.info(f"Found {len(sources)} sources in final_dump")
                
                if sources:
                    sql_queries = []
                    all_rows = []
                    
                    for source in sources:
                        sql_query = source.get("sqlQuery") or source.get("sql_query")
                        sql_rows = source.get("sqlRows") or source.get("sql_rows", [])
                        
                        # Comment out logging to reduce noise
                        # logging.info(f"Dump Source SQL Query: {sql_query}")
                        # logging.info(f"Dump Source SQL Rows: {sql_rows}")

                        if sql_query:
                            sql_queries.append(sql_query)
                            if sql_rows:
                                all_rows.extend(sql_rows)
                    
                    result = {
                        "queries": sql_queries,
                        "rows": all_rows,
                        "total_rows": len(all_rows),
                        "queries_executed": len(sql_queries)
                    }
                    # Comment out logging to reduce noise
                    # logging.info(f"Extracted SQL results from dump: {result}")
                    return result
            
            logging.warning("No SQL results found in payload")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting SQL results: {e}", exc_info=True)
            return None