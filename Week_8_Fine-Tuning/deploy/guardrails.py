import re

PROGRAMMING_KEYWORDS = [
    "code", "coding", "program", "programming",
    "python", "java", "c++", "c#", "ruby", "go", "rust",
    "sql", "javascript", "typescript", "html", "css",
    "react", "angular", "vue", "node", "express",
    "api", "backend", "frontend", "database", "query",
    "algorithm", "algorithms", "data structure",
    "array", "string", "loop", "recursion",
    "function", "method", "class", "object",
    "inheritance", "polymorphism", "encapsulation",
    "compiler", "interpreter", "debug", "debugging",
    "software", "developer", "framework", "library",
    "machine", "machines", "model", "models",
    "prime", "sorting", "searching", "binary",
    "tree", "graph", "heap", "stack", "queue",
    "hashmap", "dictionary", "set", "tuple",
    "linked list", "pointer", "reference",
    "tensorflow", "pytorch", "neural", "network",
    "training", "inference", "optimization",
    "complexity", "time complexity", "space complexity",
    "microservice", "docker", "kubernetes",
    "git", "github", "version control",
    "json", "xml", "rest", "http",
    "socket", "thread", "multithreading",
    "concurrency", "asynchronous", "synchronous",
    "oop", "object oriented", "functional programming",
    "lambda", "iteration",
    "deployment", "server", "cloud",
    "aws", "azure", "gcp"
]


def is_programming_related(text: str) -> bool:
    text = text.lower()

    for keyword in PROGRAMMING_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            return True

    return False