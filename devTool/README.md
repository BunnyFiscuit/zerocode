## Installing dev-tool in new project

The first step is to add this folder `devTool` into the system to use it in. After this is done, perform the below steps:

1. Add a `sonar-project.properties` file in the root of the project. Update the file according to the project.
2. Rename the component name which you used in step 1 for the project name. Update here: https://git.chalmers.se/courses/dat265/sep2020/group8/-/blob/master/devTool/sonarScript.py#L97 
3. Install the python package requirements. `pip install -r devTool/requirements.txt`
4. Activate the **git-hooks**. Run the command `cp -a devTool/gitHooks/. .git/hooks & find .git/hooks -type f -exec chmod 777 {} \;`
5. Start the SonarQube server. 

You should now be ready to go.


### For Windows
Windows users need to update the scripts in `devTool/gitHooks` and do the following for each git-hook file:
1. add a SHEBANG `#!/bin/sh` in the top of each file to make it executable. 
2. change from `python3` to `python`

After these changes have been made, perform **steps 3-5**. 


## Troubleshooting

### Files not execetubale 
Message when running the git actions:

*hint: The '.git/hooks/pre-commit' hook was ignored because it's not set as executable.  
hint: You can disable this warning with \`git config advice.ignoredHook false`.*

This means that the files are missing permissions to be executed and will not be activated. Either perform above **step 3** again.  
Or set the file permissions for each file using `chmod .git/hooks/pre-commit`. Change the filename and repeat for each git hook.

After this you can verify that the appropriate file permissions have been set `ls -l .git/hooks`, where there needs to be an **x** included in he file permissions. 

Example of file with correct permissions: `-rwxrwxrwx 1 username staff 90 10 Dec 08:27 pre-commit`