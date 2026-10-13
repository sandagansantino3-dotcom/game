LORNA_CHALLENGES = [
    {
        "broken": 'print("Hello"',
        "answer": 'print("Hello")',
        "time": 25,
        "damage": 25,
    },
    {
        "broken": "if score > 10",
        "answer": "if score > 10:",
        "time": 25,
        "damage": 25,
    },
    {
        "broken": "ready = true",
        "answer": "ready = True",
        "time": 25,
        "damage": 25,
    },
    {
        "broken": 'name = "Rene',
        "answer": 'name = "Rene"',
        "time": 25,
        "damage": 25,
    },
    {
        "broken": "numbers = [1, 2, 3",
        "answer": "numbers = [1, 2, 3]",
        "time": 25,
        "damage": 25,
    },
    {
        "broken": 'name = input("Name?"',
        "answer": 'name = input("Name?")',
        "time": 25,
        "damage": 25,
    },
]


MIGUEL_CHALLENGES = [
    {
        "broken": (
            'def greet(name)\n'
            '    return "Hello " + name'
        ),
        "answer": (
            'def greet(name):\n'
            '    return "Hello " + name'
        ),
        "time": 35,
        "damage": 25,
    },
    {
        "broken": (
            "for number in range(5):\n"
            "print(number)"
        ),
        "answer": (
            "for number in range(5):\n"
            "    print(number)"
        ),
        "time": 35,
        "damage": 25,
    },
    {
        "broken": (
            "numbers = "
            "[x * 2 for x range(5)]"
        ),
        "answer": (
            "numbers = "
            "[x * 2 for x in range(5)]"
        ),
        "time": 35,
        "damage": 25,
    },
    {
        "broken": (
            'player = {"name": "Rene", '
            '"score" 10}'
        ),
        "answer": (
            'player = {"name": "Rene", '
            '"score": 10}'
        ),
        "time": 35,
        "damage": 25,
    },
    {
        "broken": (
            "def add(a, b):\n"
            "return a + b"
        ),
        "answer": (
            "def add(a, b):\n"
            "    return a + b"
        ),
        "time": 35,
        "damage": 25,
    },
    {
        "broken": (
            "while health > 0\n"
            "    health -= 1"
        ),
        "answer": (
            "while health > 0:\n"
            "    health -= 1"
        ),
        "time": 35,
        "damage": 25,
    },
]


BOSS_CHALLENGES = {
    "Lorna": LORNA_CHALLENGES,
    "Miguel": MIGUEL_CHALLENGES,
}

DEFAULT_CHALLENGES = (
    LORNA_CHALLENGES
)