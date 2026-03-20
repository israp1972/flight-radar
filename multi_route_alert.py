from routes_config import ROUTES


def main():
    print("=== ROUTES LOADED ===")

    for route in ROUTES:
        print(
            f"{route['name']} | "
            f"{route['code']} | "
            f"max_price={route['max_price']} | "
            f"max_duration_one_stop_hours={route['max_duration_one_stop_hours']} | "
            f"url={'SET' if route['url'] else 'EMPTY'}"
        )


if __name__ == "__main__":
    main()