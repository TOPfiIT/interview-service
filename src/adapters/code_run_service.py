from src.usecases.interfaces.code_run_service import CodeRunServiceBase
from src.domain.test.run_result import RunResult

import aiohttp
from loguru import logger


class CodeRunService(CodeRunServiceBase):
    """
    Run code in a language
    """

    def __init__(self, base_url: str, api_key: str):
        """
        Initializes the code run service
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def run_code(self, language: str, stdin: str, code: str) -> RunResult:
        """
        Run code in a language
        """

        logger.info(f"Running code in {language}")
        url = f"{self.base_url}/api/v1/run"

        async with aiohttp.ClientSession(
            headers={
                "x-rapidapi-host": self.base_url,
                "x-rapidapi-key": self.api_key,
            }
        ) as session:
            try:
                async with session.post(
                    url,
                    json={
                        "language": language,
                        "stdin": stdin,
                        "files": {
                            "name": "index" + self._parse_language(language),
                            "content": code,
                        },
                    },
                ) as response:
                    if response.status == 200:
                        json_response = await response.json()

                        return RunResult(
                            status=json_response["status"],
                            exception=json_response["exception"],
                            stdout=json_response["stdout"],
                            stderr=json_response["stderr"],
                            execution_time=json_response["executionTime"],
                            stdin=json_response["stdin"],
                        )
                    else:
                        logger.error(
                            f"Failed to run code in {language}, status {response.status}, reason {response.reason}"
                        )
                        raise Exception("Failed to run code")

            except Exception as e:
                logger.error(f"Failed to run code in {language}, error {e}")
                raise e

    def _parse_language(self, language: str) -> str:
        """
        Parse language to file extension
        """

        if language == "python":
            return ".py"
        elif language == "javascript":
            return ".js"
        elif language == "java":
            return ".java"
        elif language == "c":
            return ".c"
        elif language == "cpp":
            return ".cpp"
        elif language == "csharp":
            return ".cs"
        elif language == "php":
            return ".php"
        elif language == "ruby":
            return ".rb"
        elif language == "go":
            return ".go"
        else:
            return ""
