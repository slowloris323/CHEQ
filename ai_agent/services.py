import sqlite3
import uuid
from datetime import datetime, timezone
import anthropic
import httpx
import time
import os
import requests
from anyio.lowlevel import checkpoint
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage


class AgentService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

        # self.memory = SqliteSaver.from_conn_string("cheq_memory.db")
        # self.memory.setup()

        self.db_conn = sqlite3.connect("cheq_memory.db", check_same_thread=False)
        # 2. Pass it directly to SqliteSaver
        self.memory = SqliteSaver(self.db_conn)
        # 3. Now you can call setup() directly
        self.memory.setup()

        self.tools = [
            {
                "name": "execute_process",
                "description": "Execute a business process with human-in-the-loop confirmation via the CHEQ protocol",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "process_id": {
                            "type": "integer",
                            "description": "The ID of the business process to execute (1 or 2 or 3)"
                        }
                    },
                    "required": ["process_id"]
                }
            }
        ]
    # we take in 2 params user_message now we are taking in with the session id which will get form the django session key

    def chat(self, user_message, session_id="default"):

        # loading the previous conversation
        thread_id = f"session_{session_id}"
        # "config = {"configurable": {"thread_id": thread_id}}"
        config = {"configurable": {"thread_id": thread_id,
                                   "checkpoint_ns": ""}}
        checkpoint = self.memory.get_tuple(config)
        if checkpoint and checkpoint.checkpoint:
            messages = checkpoint.checkpoint.get("channel_values", {}).get("messages", [])
        else:
            messages = []


        messages.append(HumanMessage(content=user_message))


        anthropic_message = self._convert_to_anthropic_format(messages)

        # messages = [{"role": "user", "content": user_message}]

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=self.tools,
                messages= anthropic_message
            )

            if response.stop_reason == "tool_use":
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        if block.name == "execute_process":
                            result = self.execute_cheq_flow(block.input["process_id"])

                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result)
                            })
                anthropic_message.append({"role": "assistant", "content": response.content})
                anthropic_message.append({"role": "user", "content": tool_results})
            else:
                final_response =""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response = block.text
                        break

                messages.append(AIMessage(content=final_response))

                checkpoint_data = {
                    "v": 1,
                    "id": str(uuid.uuid4()),
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "channel_values": {"messages": messages},
                    "channel_versions": {},
                    "versions_seen": {},
                    "pending_sends": [],
                }

                self.memory.put(
                    config,
                    checkpoint_data,  # Use the structured object
                    {},
                    {}
                )
                # self.memory.put(
                #     config,
                #     {"messages": messages},
                #     {},
                #     {}
                # ) this was resulting in an error because we didn't have a full check object so there were missing params
                return final_response
        return "No response generated"

    def _convert_to_anthropic_format(self, messages):
        """Convert LangChain messages to Anthropic API format"""
        anthropic_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                anthropic_messages.append({
                    "role": "user",
                    "content": msg.content
                })
            elif isinstance(msg, AIMessage):
                anthropic_messages.append({
                    "role": "assistant",
                    "content": msg.content
                })

        return anthropic_messages
    def execute_cheq_flow(self, process_id):
        try:

            response = httpx.post(
                'http://127.0.0.1:8000/resource_server/execute_process_with_confirmation/',
                json={"process_id": process_id},
                timeout=10.0
            )

            if response.status_code != 202:
                return f"Error: Failed to trigger process {process_id}"

            uri_pack = response.json()

            confirm_response = httpx.post(
                uri_pack['confirmation_uri'],
                json={"resource_uri": uri_pack['resource_uri']},
                timeout=10.0
            )

            if confirm_response.status_code != 200:
                return f"Error: Failed to trigger confirmation for process {process_id}"

            result_uri = uri_pack['result_uri']
            result = self.poll_for_result(result_uri, process_id)

            return result

        except Exception as e:
            return f"Error executing CHEQ flow: {str(e)}"

    def poll_for_result(self, result_uri, process_id,max_attempts=60, interval=5):
        for attempt in range(max_attempts):
            try:
                response = httpx.get(result_uri, timeout=5.0)
                result = response.json()

                if result and len(result) > 0:
                    status = result[0]['confirmation_status']

                    if status != 'PENDING':
                        if status == 'ACCEPT':
                            return f" Process {process_id} was approved and executed successfully!"
                        else:
                            return f" Process {process_id} was rejected."

                time.sleep(interval)

            except Exception as e:
                time.sleep(interval)
                continue

        return f"Timeout: No confirmation received for process {process_id} within {max_attempts * interval} seconds."

    def clear_memory(self, session_id="default"):
        """Clear conversation memory for a session"""
        thread_id = f"session_{session_id}"
        config = {"configurable": {"thread_id": thread_id}}

        self.memory.put(
            config,
            {"messages": []},
            {},
            {}
        )

