import os

cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__)))
print(cmd_folder)

rv = []
for filename in os.listdir(cmd_folder):
    if filename == "__pycache__":
        continue
    filepath = f"{cmd_folder}/{filename}"
    if os.path.isdir(filepath):
        mod = __import__( "workers." + filename)
        print(getattr(mod, filename).cmd_grp)
