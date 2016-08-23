import os
import inspect

def createfile(path):
    """
    creates a file
    ###
    path - (string) the path of the file to be created
    """
    if not(os.path.exists(path)):
        try:
            os.system("@echo off")
            os.system('''copy nul '''+'''"'''+path+'''"''')
        except:
            print("[!] failed to create path: "+path)


if __name__ == '__main__':

    project_directory = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    login_folder_path = ''.join([project_directory, "\\login"])

    filepath = login_folder_path + "\\test"
    createfile(filepath)
    with open(filepath, "w") as file:
        file.write(project_directory+"\\console.py")