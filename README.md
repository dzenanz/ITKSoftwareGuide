ITK Software Guide
==================

This is the source code for the ITK Software Guide. A combination of CMake
Superbuild infrastructure, python extraction scripts, and LaTeX formatting
needed to render the entire ITK Software Guide.

Build Overview
--------------

The generation of the ITK Software Guide is orchestrated as a CMake superubild
process. CMakeLists.txt files are placed in the directories involved on the
build process. As any other CMake-managed process, the results of the build
process are put in a binary tree corresponding to the source tree.

The following dependencies are required to build ITK Software Guide on Linux or
Windows platforms:

 - Git
 - Python
 - ImageMagick
   Windows installer can be found here: http://www.imagemagick.org/.
 - LaTeX and BibTeX
   See the preamble of the LaTeX/00-SoftwareGuide.tex file for the full list of
   required LaTeX packages. Among these packages Minted package for syntax
   highlighting in its turn depends on a Python package Pygments. Instructions
   for installing Minted and Pygments packages on Windows are available here:
   https://minted.googlecode.com/files/minted.pdf.
 - dvips, ps2pdf
   While on Linux platforms these tools are usually included with most
   distributions, on Windows platforms they are usually included in MikTex Latex
   distribution.

ITK Software Guide is generated with Latex by using input from a variety of
source code files and images:

 1. LaTeX files found in SoftwareGuide/LaTeX
 2. JPEG, PNG and EPS files in SoftwareGuide/Art
 3. PNG files generated as the result of compiling and running the examples
    included in the ITK source code
 3. ITK examples source code cxx files where the comments delimited with
    BeginLaTeX, EndLaTeX and BeginCodeSnippet, EndCodeSnippet have been written
    specifically to be included in the ITK Software Guide; the regular LaTeX
    files in SoftwareGuide/LaTeX include the LaTeX files generated from the ITK
    examples source code.

Following is a brief description of the build process:

 1. The source code of ITK 4 is downloaded and built (including ITK examples)
    in the binary output directory.
 2. JPEG and PNG files in the Art directory are converted to EPS using
    ImageMagic tools; the resulting EPS files are saved in the Art directory in
    the binary output directory.
 3. PNG files are generated by running ITK examples and converted to EPS using
    MagicTools; the resulting EPS files are saved in Art/Generated directory of
    the binary output directory.
 4. A Python script SoftwareGuide/ParseCxxExamples.py is invoked to extract the
    comments in the ITK examples source file delimited with BeginLaTeX, EndLaTeX
    and BeginCodeSnippet, EndCodeSnippet and generate LaTeX files which are
    copied into the Examples subdirectory of the binary output directory.
 5. The top-level LaTeX file SoftwareGuide/LaTeX/000-ITKSoftwareGuide-Book1.tex is
    compiled with a series of calls to latex, bibtex, latex, makeindex, dvips,
    and ps2pdf to generate the PDF file.

Configuring and Building with CMake
-----------------------------------

Following is the description how to configure and build ITK Software Guide using
CMake:

 1. Run cmake-gui and specify input and binary output directories.
    Alternatively, create the binary output directory and run
    "ccmake source_dir" where source_dir is the full path of the
    ITKSoftwareGuide directory.
 2. Configure and generate the project for the target platform.
 3. Build SuperBuild\_ITKSoftwareGuide project as appropriate for the target
    platform.

Troubleshooting
---------------

 1. Build process will fail if CMake is unable to locate any of the
    dependencies. In this case a close examination of the error messages might
    provide a clue as to which dependency is failing.

 2. Frustrated by the build taking a long time to complete
   ... no solution here. :)

How to Contribute to the ITK Software Guide
===========================================

The contribution process mirrors the [ITK contribution
process](http://itk.org/Wiki/ITK/Git/Develop) with the exception of the clone
url:

    http://itk.org/ITKSoftwareGuide.git

The basic knowledge of git underpins the contribution process. A very concise
but very handy guide to git can be found
[here](http://rogerdudler.github.io/git-guide/).

Contribution Process Overview
-----------------------------

The following commands illustrate patch submission to Gerrit:

    git clone http://itk.org/ITKSoftwareGuide.git
    cd ITKSoftwareGuide
    ./Utilities/SetupForDevelopment.sh
    git checkout -b MyTopic
    # make changes to local file(s)
    git add -- changedFileName
    git commit
    git gerrit-push

Further Details on Contributing Patches Through Git and Gerrit
--------------------------------------------------------------

After cloning the repository on your local machine for the first time, it is
necessary to provide git with your basic identity details in order to enable
the correct process of contributing to source code. The SetupForDevelopment.sh
script does just that along with giving you an opportunity to change some
other basic settings.

Before you start making changes, a new branch needs to be created with the given
name: "git checkout -b branchName". Use the editor of your choice to make the
changes to the file(s).

When you are satisfied with your changes use "git add -- fileName" to stage the
file to commit. The outcome of this process will result in a patch submitted
to Gerrit code review.

When you run "git commit" you'll be presented with a VIM editor window to type
your commit message. The commit message must be started with a one of the
following standard prefixes:

 - BUG: - fix for runtime crash or incorrect result
 - COMP: - compiler error or warning fix
 - DOC: - documentation change
 - ENH: - new functionality
 - PERF: - performance improvement
 - STYLE: - no logic impact (indentation, comments)
 - WIP: - work In Progress not ready for merge

TODO: These options are missing from msg\_gerrit() in ./git/hooks/commit-msg
file.

Following the prefix, separated by the colon and a space, type the brief
one-line description of the patch. Type a more detailed description of the
patch after a blank line. When you save and close the commit message file
you will see the change ID at the bottom of the commit message.

The process of submitting a patch is ended by running "git gerrit-push" command
which will provide a summary message from Gerrit including the URL for the
patch page on Gerrit web interface. It is important to add reviewers to your
patch.

The code is merged through the *Submit Patch Set* button in Gerrit after it
has been approved.

Some Helpful Git Commands
-------------------------

 - "git status" will report at any time which files have been modified.
 - "git branch" will list the branches available in the local repository.
 - "git checkout -- fileName" will revert the local changes made to the
   specified file.
 - "git blame -- fileName" will report the source of contributors line-by-line.
 - "git commit --amend" will revise a commit or commit message to respond to
   reviewer comments.
 - "git rebase -i HEAD~3" will give an opportunity to squash or revise the
   previous three commits.
 - "git grep searchTerm" will list all occurrences of the searchTerm in the
   source tree.
 - "get help gitCommandName" will show the documentation on the gitCommandName
   in HTML format.

A one-page Git-ITK cheat-sheet is available
[here](http://www.itk.org/Wiki/images/1/10/GitITKCheatSheet.pdf).

Further Help
------------

A lot of helpful video-guides can be found on the [ITK Bar Camp](
http://insightsoftwareconsortium.github.io/ITKBarCamp-doc/index.html) site.