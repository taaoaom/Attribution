import os
import asyncio
from ..base_compiler import BaseCompiler

class GCCCompiler(BaseCompiler):
    def __init__(self, config):
        super().__init__(config)

    async def compile_file(self, file_path, user, year):
        output_dir = os.path.join(self.output_base_path, 'GCC', user, year)
        os.makedirs(output_dir, exist_ok=True)

        output_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '_gcc.exe')
        gcc_cmd = f'g++ -o "{output_file_path}" "{file_path}"'

        try:
            proc = await asyncio.create_subprocess_shell(gcc_cmd)
            await proc.communicate()
            if proc.returncode == 0:
                print(f'Successfully compiled {file_path} with GCC')
            else:
                print(f'Failed to compile {file_path} with GCC')
        except Exception as e:
            print(f'Failed to compile {file_path} with GCC: {e}')
