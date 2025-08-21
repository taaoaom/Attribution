import asyncio
import os
from .compiler_interface import CompilerInterface

class BaseCompiler(CompilerInterface):
    def __init__(self, config):
        self.base_path = config["base_path"]
        self.output_base_path = config["output_base_path"]

    async def compile_files(self):
        tasks = []
        for user in os.listdir(self.base_path):
            user_path = os.path.join(self.base_path, user)
            if os.path.isdir(user_path):
                for year in os.listdir(user_path):
                    year_path = os.path.join(user_path, year)
                    if os.path.isdir(year_path):
                        for file in os.listdir(year_path):
                            file_path = os.path.join(year_path, file)
                            file_base, file_ext = os.path.splitext(file_path)
                            if file_ext == '.cpp':
                                tasks.append(self.compile_file(file_path, user, year))
        
        await asyncio.gather(*tasks)

    def compile_file(self, file_path, user, year):
        raise NotImplementedError("Subclasses must implement this method.")
