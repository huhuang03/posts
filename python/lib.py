cvbot-0.0.1.dist-info
cb/
_cb.cp312-win_amd64.pyd

flash_attn_2_cuda.cp312-win_amd64.pyd

        opencv_imgproc4.dll => not found
        opencv_core4.dll => not found




> What's the correct way to set the DLL search path when running a python script?

If possible, the simplest approach is to put dependent DLLs in the same directory as the extension module. 

In 3.8+, the search path for the dependent DLLs of a normally imported extension module includes the following directories:

    * the loaded extension module's directory
    * the application directory (e.g. that of python.exe)
    * the user DLL search directories that get added by 
      SetDllDirectory() and AddDllDirectory(), such as with 
      os.add_dll_directory()
    * %SystemRoot%\System32

Note that the above list does not include the current working directory or %PATH% directories.

> It would be helpful if it listed the actual name of 
> the DLL that it cannot find.

WinAPI LoadLibraryExW() doesn't have an out parameter to get the missing DLL or procedure name that caused the call to fail. All we have is the error code to report, such as ERROR_MOD_NOT_FOUND (126) and ERROR_PROC_NOT_FOUND (127). Using a debugger, you can see the name of the missing DLL or procedure if loader snaps are enabled for the application.
