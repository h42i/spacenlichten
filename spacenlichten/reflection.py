import os

def _import_module(path):
    """
    Dynamically import modules at runtime and return the module object,
    otherwise the return value will be None.
    """
    
    try:
        # determine the absolute module path
        abs_path = os.path.abspath(path)
        
        # split things up into directory, module name and file
        # extension
        mod_dir, mod_file = os.path.split(abs_path)
        mod_name, mod_ext = os.path.splitext(mod_file)
        
        # save the working directory to go back to it later
        cwd = os.getcwd()
        
        # go to the modules directory and ...
        os.chdir(mod_dir)
        
        # actually do the import
        mod_obj = __import__(mod_name)
        mod_obj.__file__ = abs_path
        
        # go back to the saved working directory
        os.chdir(cwd)
        
        # finally return the imported module
        return mod_obj
    except:
        # something went wrong, so raise a reasonable error
        raise ImportError
