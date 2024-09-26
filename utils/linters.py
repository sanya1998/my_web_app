import os

if __name__ == "__main__":
    # Подняться в рабочую директорию
    os.chdir("..")

    cmd = "make linters"
    os.system(f"{cmd}\\")
