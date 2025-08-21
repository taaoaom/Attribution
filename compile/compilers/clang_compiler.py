import os
import asyncio
from ..base_compiler import BaseCompiler

class ClangCompiler(BaseCompiler):
    def __init__(self, config):
        super().__init__(config)
        self.gcc_lib_path = config["gcc_lib_path"]
        self.lib_path = config["lib_path"]
        self.c_include_path = config["c_include_path"]
        self.cpp_include_path = config["cpp_include_path"]
        self.sys_include_path = config["sys_include_path"]

    async def compile_file(self, file_path, user, year):
        output_dir = os.path.join(self.output_base_path, 'Clang', user, year)
        os.makedirs(output_dir, exist_ok=True)

        output_file_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + '_clang.exe')
        clang_cmd = f'clang -o "{output_file_path}" "{file_path}" -target x86_64-pc-windows-gnu -stdlib=libstdc++ -fuse-ld=lld -Xlinker --enable-stdcall-fixup -L "{self.lib_path}" -L "{self.gcc_lib_path}" -I "{self.cpp_include_path}" -I "{self.sys_include_path}" -I "{self.c_include_path}" -lstdc++'

        try:
            proc = await asyncio.create_subprocess_shell(clang_cmd)
            await proc.communicate()
            if proc.returncode == 0:
                print(f'Successfully compiled {file_path} with Clang')
            else:
                print(f'Failed to compile {file_path} with Clang')
        except Exception as e:
            print(f'Failed to compile {file_path} with Clang: {e}')
