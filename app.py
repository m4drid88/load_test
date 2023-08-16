import random

# Número de líneas que deseas en data.txt
NUM_LINES = 10

with open("data.txt", "w") as f:
    for _ in range(NUM_LINES):
        f.write(str(random.randint(1, 10)) + "\n")

