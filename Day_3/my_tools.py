"""Day 3: tools for the agent you build yourself."""
import ast
import operator
import os
import re

# ---------- Tool 1: a safe calculator ----------
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}

def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")

def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression such as (12000 + 18000) * 0.9."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use only numbers and + - * / ( )."

# ---------- Tool 2: a generic web page reader ----------

SPACES = re.compile(r"\s+")

def read_webpage(url: str, max_chars: int = 10000) -> str:
    """Open a web page in Chromium and return its rendered visible text."""

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)

            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Wait until the body exists and is visible
            page.locator("body").wait_for(
                state="visible",
                timeout=300000
            )

            # Give JavaScript a chance to render dynamic content
            page.wait_for_timeout(3000)

            text = page.locator("body").inner_text()

            browser.close()

        text = SPACES.sub(" ", text).strip()

        # Detect common security-verification pages
        security_messages = [
            "Performing security verification",
            "verify you are human",
            "checking your browser",
            "security check",
            "captcha"
        ]

        lower_text = text.lower()

        for message in security_messages:
            if message.lower() in lower_text:
                return (
                    "Read error: the website returned a security "
                    "verification page instead of the requested content."
                )

        if not text:
            return "Read error: page contained no readable text."

        if len(text) > max_chars:
            text = text[:max_chars] + (
                f" ... [truncated, {len(text)} characters total]"
            )

        return text

    except Exception as error:
        return f"Read error: {type(error).__name__}: {error}"

def read_webpage_browser(url: str, max_chars: int = 5000) -> str:
    """Open a web page using Chromium and return its rendered text."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Give JavaScript time to execute
            page.wait_for_timeout(5000)

            print("TITLE:", page.title())
            print("\nPAGE TEXT:\n")
            print(page.locator("body").inner_text())

            input("\nPress Enter to close...")

            browser.close()

            return text or "Read error: page contained no readable text."

    except Exception as error:
        return f"Browser read error: {type(error).__name__}: {error}"

TOOL_FUNCTIONS = {"calculator": calculator, "read_webpage": read_webpage}

TOOLS = [
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression using + - * / ** and brackets, "
                       "for example (12000 + 18000) * 0.9.",
        "parameters": {"type": "object",
                       "properties": {"expression": {"type": "string",
                                      "description": "The arithmetic expression to evaluate"}},
                       "required": ["expression"]}}},
    {"type": "function", "function": {
        "name": "read_webpage",
        "description": "Read a web page or a local HTML/text file and return its visible text. "
                       "Give a full URL such as https://example.com or a file name such as notice.html.",
        "parameters": {"type": "object",
                       "properties": {"url": {"type": "string",
                                      "description": "URL or local file name to read"}},
                       "required": ["url"]}}},
    # {"type": "function", "function": {
    #     "name": "read_webpage_browser",
    #     "description": "Open a web page using Chromium and return its rendered text. "
    #                    "Give a full URL such as https://example.com.",
    #     "parameters": {"type": "object",
    #                    "properties": {"url": {"type": "string",
    #                                   "description": "URL to read"}},
    #                    "required": ["url"]}}},
]

if __name__ == "__main__":
    print(calculator("(12000 + 18000) * 0.9"))
    print(calculator("2 ** 10"))
    print(calculator("import os"))
    print(read_webpage("Day_3/notice.html")[:200])
    print(read_webpage("no_such_file.html"))