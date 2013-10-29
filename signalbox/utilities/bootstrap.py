import os
import shutil

def bootstrap_signalbox():
    example_proj = os.path.join(os.path.realpath(os.path.dirname(__file__)), "../../", "example_project")
    newname = raw_input("Enter a new name for your project:")
    newdir = os.path.join(os.getcwd(), newname) 
    shutil.copytree(example_proj, newdir)
    
