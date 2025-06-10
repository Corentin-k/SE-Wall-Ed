import logging
from api import create_app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
