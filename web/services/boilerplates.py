"""
Six Famous Language Boilerplate Templates for CodingDuo.
Each template contains realistic starter code with compiler optimization opportunities
(Constant Folding, Common Subexpressions, Loop Invariant Motion, Strength Reduction).
"""

from typing import Dict

LANGUAGE_BOILERPLATES: Dict[str, Dict[str, str]] = {
    "python": {
        "name": "Python",
        "icon": "🐍",
        "filename": "optimizer_demo.py",
        "code": (
            "# Python 3 Boilerplate - Compiler Optimization Target\n"
            "def compute_metrics(a: int, b: int) -> int:\n"
            "    # 1. Constant folding & subexpression opportunity\n"
            "    base_factor = 4 * 2\n"
            "    x = a + base_factor\n"
            "    y = (4 * 2) + a + b\n"
            "\n"
            "    # 2. Dead variable (never used afterwards)\n"
            "    unused_cache = a * 100\n"
            "\n"
            "    # 3. Loop invariant & strength reduction\n"
            "    total = 0\n"
            "    for i in range(100):\n"
            "        # (a + b) is invariant inside this loop!\n"
            "        total += (a + b) + (i * 2)\n"
            "\n"
            "    return x + y + total\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    result = compute_metrics(10, 20)\n"
            "    print(f'Computed Result: {result}')\n"
        ),
    },
    "cpp": {
        "name": "C / C++",
        "icon": "⚡",
        "filename": "optimizer_demo.cpp",
        "code": (
            "// C / C++ Boilerplate - Compiler Optimization Target\n"
            "#include <stdio.h>\n"
            "\n"
            "int compute_metrics(int a, int b) {\n"
            "    // 1. Constant Folding & Common Subexpressions\n"
            "    int t1 = 4 * 2;\n"
            "    int x = a + t1;\n"
            "    int y = (4 * 2) + a + b;\n"
            "\n"
            "    // 2. Dead Temporary Variable\n"
            "    int dead_calc = b * 99;\n"
            "\n"
            "    // 3. Loop Invariant Code Motion & Strength Reduction\n"
            "    int sum = 0;\n"
            "    for (int i = 0; i < 100; i++) {\n"
            "        // (a + b) is invariant; (i * 4) can use addition stepping\n"
            "        sum += (a + b) + (i * 4);\n"
            "    }\n"
            "\n"
            "    return x + y + sum;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    printf(\"Result: %d\\n\", compute_metrics(10, 20));\n"
            "    return 0;\n"
            "}\n"
        ),
    },
    "java": {
        "name": "Java",
        "icon": "☕",
        "filename": "Main.java",
        "code": (
            "// Java Boilerplate - Compiler Optimization Target\n"
            "public class Main {\n"
            "    public static int computeMetrics(int a, int b) {\n"
            "        // 1. Constant Folding & Common Subexpression\n"
            "        int base = 4 * 2;\n"
            "        int x = a + base;\n"
            "        int y = (4 * 2) + a + b;\n"
            "\n"
            "        // 2. Dead Variable\n"
            "        int deadMemory = a * b * 0;\n"
            "\n"
            "        // 3. Loop Invariant Code Motion\n"
            "        int total = 0;\n"
            "        for (int i = 0; i < 100; i++) {\n"
            "            total += (a + b) + (i * 2);\n"
            "        }\n"
            "\n"
            "        return x + y + total;\n"
            "    }\n"
            "\n"
            "    public static void main(String[] args) {\n"
            "        System.out.println(\"Result: \" + computeMetrics(10, 20));\n"
            "    }\n"
            "}\n"
        ),
    },
    "javascript": {
        "name": "JavaScript",
        "icon": "🟨",
        "filename": "script.js",
        "code": (
            "// JavaScript / TypeScript Boilerplate - Compiler Optimization Target\n"
            "function computeMetrics(a, b) {\n"
            "    // 1. Constant folding\n"
            "    const factor = 4 * 2;\n"
            "    const x = a + factor;\n"
            "    const y = (4 * 2) + a + b;\n"
            "\n"
            "    // 2. Unused dead computation\n"
            "    const deadValue = (a + b) * 0;\n"
            "\n"
            "    // 3. Loop Invariant Motion (a + b)\n"
            "    let accumulator = 0;\n"
            "    for (let i = 0; i < 100; i++) {\n"
            "        accumulator += (a + b) + (i * 2);\n"
            "    }\n"
            "\n"
            "    return x + y + accumulator;\n"
            "}\n"
            "\n"
            "console.log('Result:', computeMetrics(10, 20));\n"
        ),
    },
    "go": {
        "name": "Go (Golang)",
        "icon": "🐹",
        "filename": "main.go",
        "code": (
            "// Go Boilerplate - Compiler Optimization Target\n"
            "package main\n"
            "\n"
            "import \"fmt\"\n"
            "\n"
            "func computeMetrics(a, b int) int {\n"
            "    // 1. Constant folding & Common Subexpressions\n"
            "    factor := 4 * 2\n"
            "    x := a + factor\n"
            "    y := (4 * 2) + a + b\n"
            "\n"
            "    // 2. Loop Invariant Computation\n"
            "    sum := 0\n"
            "    for i := 0; i < 100; i++ {\n"
            "        sum += (a + b) + (i * 2)\n"
            "    }\n"
            "\n"
            "    return x + y + sum\n"
            "}\n"
            "\n"
            "func main() {\n"
            "    fmt.Println(\"Result:\", computeMetrics(10, 20))\n"
            "}\n"
        ),
    },
    "rust": {
        "name": "Rust",
        "icon": "🦀",
        "filename": "main.rs",
        "code": (
            "// Rust Boilerplate - Compiler Optimization Target\n"
            "fn compute_metrics(a: i32, b: i32) -> i32 {\n"
            "    // 1. Constant Folding & Subexpression Elimination\n"
            "    let factor = 4 * 2;\n"
            "    let x = a + factor;\n"
            "    let y = (4 * 2) + a + b;\n"
            "\n"
            "    // 2. Loop Invariant & Strength Reduction\n"
            "    let mut sum = 0;\n"
            "    for i in 0..100 {\n"
            "        sum += (a + b) + (i * 2);\n"
            "    }\n"
            "\n"
            "    x + y + sum\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"Result: {}\", compute_metrics(10, 20));\n"
            "}\n"
        ),
    },
}
