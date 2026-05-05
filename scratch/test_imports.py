import sys
import os
sys.path.append(os.getcwd())
print("Importing utils...")
import server.utils
print("Utils imported.")
print("Importing database...")
import server.database
print("Database imported.")
print("Importing main...")
import server.main
print("Main imported.")
print("Success.")
