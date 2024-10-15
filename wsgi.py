from chamber_app import create_app
import os
from config import DevelopmentConfig, Config


# Create the app using the config class
app = create_app(Config)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5572)
