from enum import Enum


class GroqModel(Enum):
    LLAMA3_8B_8192 = "llama3-8b-8192"
    GEMMA2_9B = "gemma2-9b-it"
    DEEPSEEK = "deepseek-r1-distill-llama-70b"

    def __str__(self):
        return self.value
