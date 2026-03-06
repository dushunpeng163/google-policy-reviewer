#!/usr/bin/env python3
"""
LLM 统一客户端

支持 Anthropic Claude 和 OpenAI，通过环境变量配置：
  LLM_PROVIDER=anthropic   (默认) | openai
  ANTHROPIC_API_KEY=sk-ant-...
  OPENAI_API_KEY=sk-...
  LLM_MODEL=claude-sonnet-4-5   (可选覆盖)

使用方式：
  client = LLMClient()
  for chunk in client.stream(system_prompt, user_message):
      print(chunk, end='', flush=True)
"""

import os
from typing import Generator

# 各 provider 的默认模型
DEFAULT_MODELS = {
    'anthropic': 'claude-sonnet-4-5',
    'openai':    'gpt-4o',
}

# 无 API Key 时显示的引导文本
_NO_KEY_MESSAGE = """\
## 需要配置 API Key

还没有设置 LLM API Key，请按以下步骤操作：

**第一步：在项目根目录创建 `.env` 文件**

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-你的Key
```

**或者使用 OpenAI：**

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-你的Key
```

**第二步：重启服务器**

```bash
python launcher.py
```

---

**获取 API Key：**
- Claude（推荐）：https://console.anthropic.com
- OpenAI：https://platform.openai.com

> 提示：`.env` 文件不会被提交到 Git（已在 .gitignore 中）。
"""

_IMPORT_ERROR_ANTHROPIC = """\
## 缺少依赖包

请先安装 Anthropic SDK：

```bash
pip install anthropic
```

或安装全部依赖：

```bash
pip install -r requirements.txt
```
"""

_IMPORT_ERROR_OPENAI = """\
## 缺少依赖包

请先安装 OpenAI SDK：

```bash
pip install openai
```

或安装全部依赖：

```bash
pip install -r requirements.txt
```
"""


class LLMClient:
    """LLM 统一客户端，支持 Claude 和 OpenAI 流式输出"""

    def __init__(self):
        # 加载 .env 文件（如果存在）
        self._load_dotenv()

        self.provider = os.getenv('LLM_PROVIDER', 'anthropic').lower().strip()
        self.model    = os.getenv('LLM_MODEL', DEFAULT_MODELS.get(self.provider, 'claude-sonnet-4-5'))
        self.max_tokens = int(os.getenv('LLM_MAX_TOKENS', '4096'))

        if self.provider == 'anthropic':
            self.api_key = os.getenv('ANTHROPIC_API_KEY', '').strip()
        elif self.provider == 'openai':
            self.api_key = os.getenv('OPENAI_API_KEY', '').strip()
        else:
            self.api_key = ''

    def _load_dotenv(self):
        """简单的 .env 文件加载（不依赖 python-dotenv）"""
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if not os.path.exists(env_path):
            return
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or '=' not in line:
                        continue
                    key, _, value = line.partition('=')
                    key   = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 只在没有设置时才写入（环境变量优先）
                    if key and key not in os.environ:
                        os.environ[key] = value
        except Exception:
            pass

    def stream(self, system_prompt: str, user_message: str) -> Generator[str, None, None]:
        """
        流式生成 LLM 响应。

        yield str 文本块，直到完成。
        无 API Key 或依赖缺失时 yield 友好提示文本。
        """
        if not self.api_key:
            yield _NO_KEY_MESSAGE
            return

        if self.provider == 'anthropic':
            yield from self._stream_anthropic(system_prompt, user_message)
        elif self.provider == 'openai':
            yield from self._stream_openai(system_prompt, user_message)
        else:
            yield f"## 不支持的 LLM Provider\n\n`LLM_PROVIDER={self.provider}` 不被识别，请设置为 `anthropic` 或 `openai`。"

    def _stream_anthropic(self, system_prompt: str, user_message: str) -> Generator[str, None, None]:
        try:
            import anthropic
        except ImportError:
            yield _IMPORT_ERROR_ANTHROPIC
            return

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            with client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{'role': 'user', 'content': user_message}],
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except anthropic.AuthenticationError:
            yield "## API Key 无效\n\n请检查 `ANTHROPIC_API_KEY` 是否正确。"
        except anthropic.RateLimitError:
            yield "## 请求频率超限\n\n请稍等片刻后重试，或检查账户额度。"
        except Exception as e:
            yield f"## 调用失败\n\n```\n{type(e).__name__}: {e}\n```"

    def _stream_openai(self, system_prompt: str, user_message: str) -> Generator[str, None, None]:
        try:
            from openai import OpenAI
        except ImportError:
            yield _IMPORT_ERROR_OPENAI
            return

        try:
            client = OpenAI(api_key=self.api_key)
            with client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                stream=True,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user',   'content': user_message},
                ],
            ) as stream:
                for chunk in stream:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            err = str(e)
            if 'authentication' in err.lower() or 'api key' in err.lower():
                yield "## API Key 无效\n\n请检查 `OPENAI_API_KEY` 是否正确。"
            elif 'rate limit' in err.lower():
                yield "## 请求频率超限\n\n请稍等片刻后重试，或检查账户额度。"
            else:
                yield f"## 调用失败\n\n```\n{type(e).__name__}: {e}\n```"

    @property
    def model_display(self) -> str:
        """用于 UI 显示的模型名称"""
        return f"{self.provider}/{self.model}"
