import os

from core.exceptions import ToolExecutionError


class FileTool:
    """
    Tool to read text files.
    """

    def read_file(self, file_path):
        try:
            if not os.path.exists(file_path):
                raise ToolExecutionError("File Tool", "File not found.")

            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            if not content.strip():
                raise ToolExecutionError("File Tool", "File is empty.")

            return content

        except ToolExecutionError:
            raise

        except Exception as e:
            raise ToolExecutionError("File Tool", str(e))
