import anthropic
import httpx
import time
import os

class AgentService:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

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

    def chat(self, user_message):

        messages = [{"role": "user", "content": user_message}]

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=self.tools,
                messages=messages
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
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            else:
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                break
        return "No response generated"

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



