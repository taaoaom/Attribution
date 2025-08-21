from abc import ABC, abstractmethod

class CompilerInterface(ABC):
    @abstractmethod
    def compile_files(self):
        pass

    @abstractmethod
    def compile_file(self, file_path, user, year):
        pass
