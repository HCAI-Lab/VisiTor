import json
import os
import urllib.error
import urllib.request


class VLLMClient:
    def __init__(self, url=None, model=None, timeout_seconds=None):
        self.url = url or os.getenv("VLLM_URL", "http://127.0.0.1:8000/v1/chat/completions")
        self.model = model or os.getenv("VLLM_MODEL", "Xingyu-Zheng/gemma-4-E2B-it-int4-foem")
        self.timeout_seconds = float(timeout_seconds or os.getenv("VLLM_TIMEOUT_SECONDS", "120"))

    def _post_json(self, payload, timeout_seconds):
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    @staticmethod
    def _build_messages(prompt, system=None, history=None):
        messages = []
        if system:
            messages.append({"role": "system", "content": str(system)})

        if isinstance(history, list):
            for item in history:
                if not isinstance(item, dict):
                    continue
                role = item.get("role")
                content = item.get("content")
                if role in {"system", "user", "assistant"} and content is not None:
                    messages.append({"role": role, "content": str(content)})

        messages.append({"role": "user", "content": str(prompt)})
        return messages

    def ask(self, prompt, **kwargs):
        if prompt is None or str(prompt).strip() == "":
            return {"error": "prompt is required"}

        payload = {
            "model": kwargs.get("model", self.model),
            "messages": self._build_messages(
                prompt=prompt,
                system=kwargs.get("system"),
                history=kwargs.get("history"),
            ),
            "temperature": float(kwargs.get("temperature", 0.2)),
            "top_p": float(kwargs.get("top_p", 0.95)),
            "max_tokens": int(kwargs.get("max_tokens", 512)),
            "stream": False,
        }

        # Strip fields that can cause API schema errors for invalid values.
        if payload["temperature"] < 0:
            payload.pop("temperature", None)
        if payload["top_p"] <= 0:
            payload.pop("top_p", None)
        if payload["max_tokens"] <= 0:
            payload.pop("max_tokens", None)

        try:
            response = self._post_json(
                payload,
                timeout_seconds=float(kwargs.get("timeout", self.timeout_seconds)),
            )
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            return {"error": f"HTTP {e.code}", "details": body}
        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

        choices = response.get("choices") or []
        content = ""
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content", "")

        return {
            "result": content,
            "model": response.get("model", payload["model"]),
            "usage": response.get("usage", {}),
            "raw": response,
        }


# Backward-compatible helper for simple direct use.
def query_vllm(prompt, kwargs=None):
    kwargs = kwargs or {}
    client = VLLMClient(
        url=kwargs.get("url"),
        model=kwargs.get("model"),
        timeout_seconds=kwargs.get("timeout"),
    )
    return client.ask(prompt, **kwargs)
