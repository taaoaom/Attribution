import inspect
import json
import asyncio
import importlib
import pkgutil
from compile.base_compiler import BaseCompiler
from compile.compiler_interface import CompilerInterface
from obfuscate.obfuscator import Obfuscator
from md5_checker import MD5Checker
from database import GCJDatabase

class CodeProcessor:
    def __init__(self, config):
        self.compilers = get_compiler_instances(config["compiler"])
        self.obfuscator = Obfuscator(config["obfuscator"])

    async def process_files(self):
        compile_tasks = []
        for compiler in self.compilers:
            compile_tasks.append(compiler.compile_files())
        await asyncio.gather(*compile_tasks)

        await self.obfuscator.obfuscate_files()

def get_compiler_instances(config):
    compiler_instances = []
    package_name = "compile.compilers"
    
    package = importlib.import_module(package_name)
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{module_name}")
        for cls in module.__dict__.values():
            if inspect.isclass(cls) and issubclass(cls, CompilerInterface) and cls is not BaseCompiler:
                instance = cls(config)
                compiler_instances.append(instance)

    return compiler_instances

async def main():
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    db = GCJDatabase(config["database_path"])

    md5_checker = MD5Checker(config["submissions_path"], db)
    await md5_checker.process_files()

    db.close()

    # code_processor = CodeProcessor(config)
    # await code_processor.process_files()

if __name__ == "__main__":
    asyncio.run(main())
