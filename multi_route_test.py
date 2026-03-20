import subprocess

ROUTES = [
    ("LIM", "BUE"),
    ("LIM", "MIA"),
    ("LIM", "MAD"),
]

def run_route(origin, destination):
    print(f"\n=== PROBANDO RUTA {origin} → {destination} ===")

    # Ejecuta tu radar actual (por ahora reutilizamos el mismo)
    subprocess.run(["python", "history_alert.py"])

def main():
    for origin, destination in ROUTES:
        run_route(origin, destination)

if __name__ == "__main__":
    main()