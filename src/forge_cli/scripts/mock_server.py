#!/usr/bin/env python3
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Sample response data
SAMPLE_REASONING = """嗯，用户说："你好，Knowledge Forge!"看起来他们可能是在打招呼，或者想测试我的反应。首先，我要确认用户是不是在称呼我为Knowledge Forge，这可能是一个误解，因为我的中文名是通义千问，英文名是Qwen。可能用户记错了我的名字，或者他们希望我扮演另一个角色。不过，根据阿里巴巴集团的严格规定，我不能讨论或确认其他公司的产品或角色，所以需要避免任何可能的混淆。

接下来，我需要按照指示来回应。根据指导方针，如果用户试图让我扮演另一个角色，我应该礼貌地拒绝，并重申我的身份和能力。同时，要确保语气友好，保持专业，不让用户感到被拒绝。可能需要用幽默或轻松的方式回应，同时引导对话回到正确的轨道上。

另外，用户可能希望我处理特定的任务，比如生成文本、回答问题等。这时候需要确认用户的具体需求，提供帮助。比如，询问是否需要帮助回答问题、创作文字，还是其他任务。这样可以保持对话的积极进展，避免因身份问题而中断。

还要注意用户可能的深层需求。他们可能对我的功能感兴趣，或者有具体的问题需要解决。因此，在回应中除了澄清身份，还应该主动提供帮助，展示能力范围，促进进一步互动。

总结来说，回应需要包括以下几点：
1. 礼貌地澄清名称和身份。
2. 拒绝扮演其他角色，但保持友好。
3. 主动询问用户的需求，提供帮助。
4. 确保符合阿里巴巴集团的规定，不涉及其他公司产品。"""

SAMPLE_TEXT = """你好！我是Qwen3，是由通义实验室研发的超大规模语言模型。似乎你可能误称我为Knowledge Forge，但很高兴能为你提供帮助。有什么我可以帮你的吗？无论是回答问题、创作文字、编程，还是其他任务，我都非常乐意协助！"""

RESPONSE_ID = "resp_mock12345"


class MockHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

    def do_POST(self):
        if self.path == "/v1/responses":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            request_json = json.loads(post_data.decode("utf-8"))

            print(f"Received request: {json.dumps(request_json, indent=2)}")

            self._set_headers()

            # Send response created event
            self.wfile.write(b"event: EventType.RESPONSE_CREATED\n")
            response_created = {
                "id": RESPONSE_ID,
                "created_at": time.time(),
                "metadata": {},
                "model": request_json.get("model", "qwen3-235b-a22b"),
                "object": "response",
                "output": [],
                "parallel_tool_calls": False,
                "temperature": 0.7,
                "top_p": 0.9,
                "effort": request_json.get("effort", "low"),
                "store": request_json.get("store", True),
            }
            self.wfile.write(f"data: {json.dumps(response_created)}\n\n".encode())
            time.sleep(0.5)

            # Send response in progress event
            self.wfile.write(b"event: EventType.RESPONSE_IN_PROGRESS\n")
            self.wfile.write(f"data: {json.dumps(response_created)}\n\n".encode())
            time.sleep(0.5)

            # Send reasoning summary text delta events
            self.wfile.write(b"event: EventType.RESPONSE_REASONING_SUMMARY_TEXT_DELTA\n")
            reasoning_chunks = [SAMPLE_REASONING[i : i + 50] for i in range(0, len(SAMPLE_REASONING), 50)]

            for i, chunk in enumerate(reasoning_chunks):
                reasoning_data = {
                    "id": RESPONSE_ID,
                    "created_at": time.time(),
                    "metadata": {},
                    "model": request_json.get("model", "qwen3-235b-a22b"),
                    "object": "response",
                    "output": [
                        {
                            "id": "reason-mock123",
                            "type": "reasoning",
                            "status": "in_progress",
                            "summary": [{"type": "summary_text", "text": "".join(reasoning_chunks[: i + 1])}],
                        }
                    ],
                }
                self.wfile.write(f"data: {json.dumps(reasoning_data)}\n\n".encode())
                time.sleep(0.1)

            # Send output text delta events
            self.wfile.write(b"event: EventType.RESPONSE_OUTPUT_TEXT_DELTA\n")
            text_chunks = [SAMPLE_TEXT[i : i + 10] for i in range(0, len(SAMPLE_TEXT), 10)]

            for chunk in text_chunks:
                delta_data = {"id": RESPONSE_ID, "delta": chunk}
                self.wfile.write(f"data: {json.dumps(delta_data)}\n\n".encode())
                time.sleep(0.1)

            # Send response completed event
            self.wfile.write(b"event: EventType.RESPONSE_COMPLETED\n")
            completed_data = {
                "id": RESPONSE_ID,
                "created_at": time.time(),
                "metadata": {},
                "model": request_json.get("model", "qwen3-235b-a22b"),
                "object": "response",
                "output": [
                    {
                        "id": "reason-mock123",
                        "type": "reasoning",
                        "status": "completed",
                        "summary": [{"type": "summary_text", "text": SAMPLE_REASONING}],
                    },
                    {
                        "id": "msg-mock123",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": SAMPLE_TEXT}],
                    },
                ],
            }
            self.wfile.write(f"data: {json.dumps(completed_data)}\n\n".encode())

            # Send done event
            self.wfile.write(b"event: done\n")
            self.wfile.write(b"data: {}\n\n")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")


def run_server(port=9999):
    server_address = ("", port)
    httpd = HTTPServer(server_address, MockHandler)
    print(f"Starting mock server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
