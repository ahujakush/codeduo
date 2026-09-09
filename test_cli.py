"""
Interactive CLI Simulator for the AI Problem Solver.
Test the problem-solving engine directly in your terminal without needing Telegram!
"""

import sys
import asyncio
import argparse
from bot.config import config
from bot.ai.factory import create_ai_solver
from bot.memory.chat_memory import ChatMemoryManager


async def run_single_query(query: str, persona: str):
    """Run a single test problem query."""
    solver = create_ai_solver(config)
    print(f"\n[AI Provider]: {solver.get_provider_name()} (Model: {solver.get_model_name()})")
    print(f"[Persona]: {persona}")
    print(f"[Question]: {query}\n" + "-" * 50)

    solution = await solver.solve_text(query, persona=persona)
    print(solution)
    print("-" * 50 + "\n")


async def run_interactive_repl():
    """Run interactive terminal session simulating Telegram chat."""
    solver = create_ai_solver(config)
    memory = ChatMemoryManager(max_turns=5)
    chat_id = 9999
    persona = config.default_persona

    print("=" * 65)
    print("🤖 AI Problem Solver - Terminal Interactive Mode")
    print(f"• Active Provider: {solver.get_provider_name()}")
    print(f"• Model: {solver.get_model_name()}")
    print(f"• Persona: {persona}")
    print("Type your problem or question below.")
    print("Special commands: /persona <name>, /clear, /exit")
    print("=" * 65 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/exit", "exit", "quit"):
            print("Goodbye!")
            break

        if user_input.startswith("/persona"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                persona = parts[1].strip().lower()
                print(f"🎭 Switched persona to: {persona}\n")
            else:
                print(f"Current persona: {persona}. Available: solver, coder, math, tutor, concise\n")
            continue

        if user_input.lower() == "/clear":
            memory.clear_history(chat_id)
            print("🧹 Conversation memory cleared.\n")
            continue

        history = memory.get_history(chat_id)
        print("\nThinking...\n")
        solution = await solver.solve_text(user_input, history=history, persona=persona)

        memory.add_message(chat_id, "user", user_input)
        memory.add_message(chat_id, "assistant", solution)

        print(f"AI ({persona}):\n{solution}\n")
        print("-" * 65)


def main():
    parser = argparse.ArgumentParser(description="Test AI Problem Solver in Terminal")
    parser.add_argument("--test-query", "-q", type=str, help="Run a single test problem")
    parser.add_argument("--persona", "-p", type=str, default="solver", help="Persona to use")

    args = parser.parse_args()

    if args.test_query:
        asyncio.run(run_single_query(args.test_query, args.persona))
    else:
        asyncio.run(run_interactive_repl())


if __name__ == "__main__":
    main()
