"""
Canonical Starter Boilerplates for Famous Languages in CodingDuo.
Provides pure, minimal starter templates (like Hello World / standard entry points)
shown in Preview Mode and inserted only on Tab key / Tab button trigger.
"""

from typing import Dict

LANGUAGE_BOILERPLATES: Dict[str, Dict[str, str]] = {
    "python": {
        "name": "Python",
        "icon": "🐍",
        "filename": "main.py",
        "code": (
            "def main():\n"
            "    print(\"Hello, World!\")\n"
            "\n"
            "if __name__ == \"__main__\":\n"
            "    main()\n"
        ),
    },
    "cpp": {
        "name": "C / C++",
        "icon": "⚡",
        "filename": "main.cpp",
        "code": (
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            "    std::cout << \"Hello, World!\" << std::endl;\n"
            "    return 0;\n"
            "}\n"
        ),
    },
    "java": {
        "name": "Java",
        "icon": "☕",
        "filename": "Main.java",
        "code": (
            "public class Main {\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Hello, World!\");\n"
            "    }\n"
            "}\n"
        ),
    },
    "javascript": {
        "name": "JavaScript",
        "icon": "🟨",
        "filename": "index.js",
        "code": (
            "function main() {\n"
            "    console.log(\"Hello, World!\");\n"
            "}\n"
            "\n"
            "main();\n"
        ),
    },
    "go": {
        "name": "Go",
        "icon": "🐹",
        "filename": "main.go",
        "code": (
            "package main\n"
            "\n"
            "import \"fmt\"\n"
            "\n"
            "func main() {\n"
            "    fmt.Println(\"Hello, World!\")\n"
            "}\n"
        ),
    },
    "rust": {
        "name": "Rust",
        "icon": "🦀",
        "filename": "main.rs",
        "code": (
            "fn main() {\n"
            "    println!(\"Hello, World!\");\n"
            "}\n"
        ),
    },
    "html": {
        "name": "HTML",
        "icon": "🌐",
        "filename": "index.html",
        "code": (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "    <title>CodingDuo</title>\n"
            "</head>\n"
            "<body>\n"
            "    <h1>Hello, World!</h1>\n"
            "</body>\n"
            "</html>\n"
        ),
    },
}
