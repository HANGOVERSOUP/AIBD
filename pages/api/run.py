from main import app
import sys
import os
import uvicorn

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=9999,  reload=True)
