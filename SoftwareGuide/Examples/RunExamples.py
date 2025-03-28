#!/usr/bin/env python
import sys
import os
import re
import subprocess
import errno
import os.path
import time
from datetime import date, timedelta


#
# Tag defs
#
beginCmdLineArgstag = "BeginCommandLineArgs"
endCmdLineArgstag = "EndCommandLineArgs"

outputToCodeBlockMap = dict()


def mkdir_p(path):
    """ Safely make a new directory, checking if it already exists"""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


"""
def GetFilesInThisLine(line, IOtag):
    line.replace(IOtag, "")  # Strip the tag away
    # squish more than one space into one
    line.replace("  ", " ").rstrip().lstrip()  # strip leading and trailing spaces
    outputfilesInThisLine = line.split(' ')
    return outputfilesInThisLine

fileoutputstag = "OUTPUTS:"
def GetOutputFilesInThisLine(line):
    return GetFilesInThisLine(line, fileoutputstag)

fileinputstag = "INPUTS:"
def GetInputFilesInThisLine(line):
    return GetFilesInThisLine(line, fileinputstag)
"""

## This class is initialized with a the starting line of
## the command processing, and the block of text for
## this command invocation
class OneCodeBlock:
    def __init__(self, sourceFile, id, codeblock, pathFinder):
        self.sourceFile = sourceFile
        self.id = id
        self.codeblock = codeblock
        self.inputs = []
        self.outputs = []
        self.MakeAllFileLists()
        self.pathFinder = pathFinder
        self.progBaseName = os.path.basename(self.sourceFile)[:-4]
        self.progFullPath = pathFinder.GetProgramPath(self.progBaseName)
        self.verbose = False
        self.parents = set()
        self.children = set()
        if not os.path.exists(self.progFullPath):
            print(
                f"ERROR:  Required program {self.progBaseName} does not exists.  Please rebuild ITK"
            )
            sys.exit(-1)

    def GetProgBaseName(self):
        return self.progBaseName

    def DoInputsExists(self):
        for ii in self.inputs:
            if os.path.isabs(ii):
                ii = pathFinder.GetInputPath(ii)
            if ii == None:
                continue
            if not os.path.exists(ii):
                print(f"ERROR:  XXXXXXXXXXXX MISSING {ii}")
                return False
        return True

    def AreOutputsNewer(self):
        oldest_output = 100000000000000000000000
        if self.verbose:
            print(f"Self Outputs {self.outputs}")
            print(f"Self Inputs {self.inputs}")
        for o in self.outputs:
            if self.verbose:
                print(f"CHECKING TIME FOR: {o}")
            if os.path.exists(o):
                this_output_time = os.path.getmtime(o)
                if self.verbose:
                    print(f"This Output Time: {this_output_time}")
                if this_output_time < oldest_output:
                    oldest_output = this_output_time
            else:
                if self.verbose:
                    print(f"Missing Output: {o}")
                return False
        newest_input = os.path.getmtime(self.progFullPath)
        for i in self.inputs:
            if i == None:
                continue
            if self.verbose:
                print(f"CHECKING TIME FOR: {i}")
            if os.path.exists(i):
                this_input_time = os.path.getmtime(i)
                if self.verbose:
                    print(f"This Input Time: {this_input_time}")
                if this_input_time > newest_input:
                    newest_input = this_input_time
            else:
                print(f"Missing input {i}")
                print(f"Searched {self.inputs}")
                print("ERROR:" * 20)
                print(
                    "Failing to process all data, This should never happen because you should only run this function once all inputs exists."
                )
                sys.exit(
                    -1
                )  # This should never happen because you should only run this function once all inputs exists.
        if self.verbose:
            print(f"Newest Input: {newest_input}, Oldest Output: {oldest_output}")
        if newest_input < oldest_output:
            return True
        else:
            return False

    def GetCommandLine(self):
        commandLine = self.progFullPath + " "
        lineparse = re.compile(" *(.*): *(.*)")
        currLineNumber = self.id
        for currLine in self.codeblock:
            currLineNumber = currLineNumber + 1
            parseGroups = lineparse.search(currLine)
            if parseGroups == None:
                print(
                    f"ERROR: Invalid parsing of {self.sourceFile} at line {currLineNumber}"
                )
                sys.exit(-1)
            if parseGroups.group(1) == "INPUTS":
                inputBaseFileName = parseGroups.group(2)
                inputFileName = pathFinder.GetInputPath(inputBaseFileName)
                if inputFileName == None:
                    print(
                        f"ERROR: Invalid input {parseGroups.group(2)} at {self.sourceFile} at line {currLineNumber}"
                    )
                    exit(-1)
                else:
                    commandLine = commandLine + " " + inputFileName
                    if not os.path.exists(inputFileName):
                        inputFileName = pathFinder.GetOutputPath(inputBaseFileName)
                    if not os.path.exists(inputFileName):
                        print(
                            f"WARNING: Can not find {inputFileName} path, assuming it is autogenerated"
                        )
                    self.inputs.append(inputFileName)
            elif parseGroups.group(1) == "OUTPUTS":
                outputFileName = pathFinder.GetOutputPath(parseGroups.group(2))
                commandLine = commandLine + " " + outputFileName
                self.outputs.append(outputFileName)
            elif parseGroups.group(1) == "ARGUMENTS":
                commandLine = commandLine + " " + parseGroups.group(2)
            elif parseGroups.group(1) == "NOT_IMPLEMENTED":
                pass
        return commandLine

    def GetOutputPaths(self):
        return self.outputs

    def GetInputPaths(self):
        return self.inputs

    def MakeAllFileLists(self):
        self.inputs = []
        self.outputs = []
        lineparse = re.compile(" *(.*): *(.*)")
        lineNumber = self.id
        for currLine in self.codeblock:
            lineNumber = lineNumber + 1
            parseGroups = lineparse.search(currLine)
            parseKey = parseGroups.group(1).rstrip().lstrip()
            if parseKey == "":
                continue  # Empty lines are OK
            elif parseKey == "INPUTS":
                inputFile = currLine.replace("INPUTS:", "").rstrip().lstrip()
                inputFile = pathFinder.GetInputPath(inputFile)
                self.inputs.append(inputFile)
            elif parseKey == "OUTPUTS":
                outputFile = currLine.replace("OUTPUTS:", "").rstrip().lstrip()
                outputFile = pathFinder.GetOutputPath(outputFile)
                self.outputs.append(outputFile)
            elif parseKey == "ARGUMENTS":
                pass
            elif parseKey == "NOT_IMPLEMENTED":
                pass
            else:
                print(
                    f"ERROR:  INVALID LINE IDENTIFIER {parseGroups.group(1)} at line {lineNumber} in {self.sourceFile}"
                )
                sys.exit(-1)

    def Print(self):
        blockline = self.id
        print("=" * 80)
        print(self.sourceFile)
        for blocktext in self.codeblock:
            blockline += 1
            print(f"{blockline}  : {blocktext}")
        print(self.GetCommandLine())
        print("^" * 80)

    def PopulateChildren(self):
        for inputFile in self.inputs:
            # If one of this file's inputs is generated by another program
            # it is dependent on that program.
            if inputFile in outputToCodeBlockMap:
                self.children.add(outputToCodeBlockMap[inputFile])
                outputToCodeBlockMap[inputFile].parents.add(self)
        return


def ParseOneFile(sourceFile, pathFinder):
    #
    # Read each line and Parse the input file
    #
    # Get the command line args from the source file
    sf = open(sourceFile, "r")
    INFILE = sf.readlines()
    sf.close()
    parseLine = 0
    starttagline = 0
    thisFileCommandBlocks = []
    for thisline in INFILE:
        parseLine += 1

        thisline = thisline.replace("//", "")
        thisline = thisline.replace("{", "").replace("}", "")
        thisline = thisline.rstrip().rstrip("/").rstrip().lstrip().lstrip("/").lstrip()
        # If the "BeginCommandLineArgs" tag is found, set the "starttagline" var and
        # initialize a few variables and arrays.
        if thisline.count(beginCmdLineArgstag) == 1:  # start of codeBlock
            starttagline = parseLine
            codeBlock = []
        elif thisline.count(endCmdLineArgstag) == 1:  # end of codeBlock
            ocb = OneCodeBlock(sourceFile, starttagline, codeBlock, pathFinder)
            thisFileCommandBlocks.append(ocb)
            starttagline = 0
        elif starttagline > 0:  # Inside a codeBlock
            codeBlock.append(thisline)
        else:  # non-codeBlock line
            pass
    return thisFileCommandBlocks


dirsNotUsed = []


def datecheck(root, age):
    basedate = date.today() - timedelta(days=age)
    used = os.stat(root).st_mtime  # st_mtime=modified, st_atime=accessed
    year, day, month = time.localtime(used)[:3]
    lastused = date(year, day, month)
    return basedate, lastused


def getdirs(basedir, age):
    for root, dirs, files in os.walk(basedir):
        basedate, lastused = datecheck(root, age)
        if lastused < basedate:  # Gets files older than (age) days
            dirsNotUsed.append(root)


class ITKPathFinder:
    def __init__(self, itkSourceDir, itkExecutablesDir, itkBuildDir, SWGuidBaseOutput):
        self.execDir = itkExecutablesDir
        self.execDir = self.execDir.rstrip("/")
        self.outPicDir = os.path.join(SWGuidBaseOutput, "Art", "Generated")
        # Check if there are any input files that need to be flipped.
        self.outPicDir = os.path.realpath(self.outPicDir)
        self.outPicDir = self.outPicDir.rstrip("/")
        mkdir_p(self.outPicDir)

        # HACK:  Need better search criteria
        searchPaths = f"{itkBuildDir}/ExternalData/Testing/Data/Input#{itkBuildDir}/ExternalData/Examples/Data/BrainWeb#{itkBuildDir}/Testing/Temporary#{itkBuildDir}/Modules/Nonunit/Review/test#{itkBuildDir}/ExternalData/Modules/Segmentation/LevelSetsv4/test/Baseline#{itkBuildDir}/ExternalData/Modules/IO/GE/test/Baseline#{itkBuildDir}/ExternalData/Examples/Filtering/test/Baseline#{itkBuildDir}/Examples/Segmentation/test#{SWGuidBaseOutput}/Art/Generated#{itkSourceDir}/Examples/Data"
        dirtyDirPaths = searchPaths.split("#")

        self.searchDirList = []
        for eachpath in dirtyDirPaths:
            if os.path.isdir(eachpath):
                self.searchDirList.append(os.path.realpath(eachpath))
            else:
                print(f"WARNING: MISSING search path {eachpath} ")
                sys.exit(-1)

    def GetProgramPath(self, execfilenamebase):
        testPath = os.path.join(self.execDir, execfilenamebase)
        if os.name == "nt":
            testPath += ".exe"
        if os.path.exists(testPath):
            return testPath
        else:
            print(f"ERROR:  {testPath} does not exists")
            sys.exit(-1)

    def GetInputPath(self, inputBaseName):
        for checkPath in self.searchDirList:
            testPath = os.path.join(checkPath, inputBaseName)
            if os.path.exists(testPath):
                return testPath
            else:
                # print(f"##STATUS: Not yet found input {testPath}")
                pass
        return self.GetOutputPath(inputBaseName)

    def GetOutputPath(self, outputBaseName):
        outPath = os.path.join(self.outPicDir, outputBaseName)
        # outPath = outPath.replace(self.outPicDir+'/'+self.outPicDir, self.outPicDir ) #Avoid multiple path concatenations
        # if not os.path.exists(outPath):
        # print(f"@@Warning: Output missing {outPath}")
        return outPath


class CodeBlockTopSort:
    def __init__(self, CodeBlockList):
        self.CodeBlockList = list(codeblock for codeblock in CodeBlockList)
        self.PopulateCodeBlockToOutputMap()
        self.LinkCodeBlocks()
        self.unsortedCodeBlockSet = set(self.CodeBlockList)
        self.sortedCodeBlocks = list()
        self.SortCodeBlocks()

    def PopulateCodeBlockToOutputMap(self):
        for codeblock in self.CodeBlockList:
            for outputFile in codeblock.outputs:
                outputToCodeBlockMap[outputFile] = codeblock
        return

    def LinkCodeBlocks(self):
        for codeblock in self.CodeBlockList:
            codeblock.PopulateChildren()
        return

    def SortCodeBlocks(self):
        # In this implementation, a parent CodeBlock depends on its children
        while len(self.unsortedCodeBlockSet) > 0:
            candidate = self.unsortedCodeBlockSet.pop()
            if len(candidate.children) > 0:
                # If it still has children, put it back in the pile of unsorted CodeBlocks
                self.unsortedCodeBlockSet.add(candidate)
            else:
                for parent in candidate.parents:
                    parent.children.remove(candidate)
                self.sortedCodeBlocks.append(candidate)
        return

    def GetSortedCodeBlockList(self):
        return self.sortedCodeBlocks


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse an ITK source tree and run programs in order to make output files for Software Guide."
    )
    parser.add_argument(
        "--itkSourceDir",
        dest="itkSourceDir",
        action="store",
        default=None,
        help="The path to the ITK source tree.",
    )
    parser.add_argument(
        "--itkBuildDir",
        dest="itkBuildDir",
        action="store",
        default=None,
        help="The path to the ITK build tree where test data is found.",
    )
    parser.add_argument(
        "--itkExecDir",
        dest="itkExecDir",
        action="store",
        default=None,
        help="The path to the ITK binary tree bin directory were executables are found.",
    )
    parser.add_argument(
        "--SWGuidBaseOutput",
        dest="SWGuidBaseOutput",
        action="store",
        default=None,
        help="The base directory of the output directory.",
    )

    args = parser.parse_args()

    itkExecutablesDir = os.path.realpath(args.itkExecDir)
    itkBuildDir = os.path.realpath(args.itkBuildDir)
    pathFinder = ITKPathFinder(
        args.itkSourceDir, itkExecutablesDir, itkBuildDir, args.SWGuidBaseOutput
    )

    allCommandBlocks = []
    for rootDir, dirList, fileList in os.walk(args.itkSourceDir):
        if rootDir.count("ThirdParty") >= 1:
            # print(f"Passing on: {rootDir}")
            continue

        for currFile in fileList:
            if currFile[-4:] != ".cxx":  # Only parse cxx files
                # print(f"NOT PARSING: {currFile} because it has wrong extension {currFile[-r:]}")
                continue
            sourceFile = os.path.realpath(rootDir + "/" + currFile)

            # A dictionary indexed by starting line to the command blocks
            allCommandBlocks += ParseOneFile(sourceFile, pathFinder)

    sorter = CodeBlockTopSort(allCommandBlocks)
    sortedAllCommandBlocks = sorter.GetSortedCodeBlockList()
    for blockStart in sortedAllCommandBlocks:
        runCommand = blockStart.GetCommandLine()
        for inputFile in blockStart.inputs:
            if not os.path.exists(inputFile):
                print(f"WARNING: {blockStart.sourceFile} input does not exist")
        print(f"Running: {runCommand}")
        try:
            retcode = subprocess.call(runCommand, shell=True)
            if retcode < 0:
                print("Child was terminated by signal " + str(-retcode))
            else:
                print("Child returned " + str(retcode))
        except OSError as e:
            print("Execution failed for some reason: " + str(e))

    dependencyDictionary = dict()
    for block in sortedAllCommandBlocks:
        baseProgramName = block.GetProgBaseName()
        if not baseProgramName in dependencyDictionary:
            dependencyDictionary[baseProgramName] = list()
        # Now we warn if the input or output doesn't exist
        for outputFile in block.outputs:
            if not os.path.exists(outputFile):
                print(
                    f"WARNING: output {outputFile} of {baseProgramName} does not exist!"
                )
        for inputFile in block.inputs:
            if not os.path.exists(inputFile):
                print(
                    f"WARNING: input {inputFile} of {baseProgramName} does not exist!"
                )
        dependencyDictionary[baseProgramName].extend(block.outputs)
        for inputFile in block.inputs:
            # Only add pngs because imagemagick does not yet support metaimage
            if inputFile[-4:] == ".png":
                dependencyDictionary[baseProgramName].append(inputFile)

    mkdir_p(os.path.join(args.SWGuidBaseOutput, "Examples"))
    outputCMakeDependancies = os.path.join(
        args.SWGuidBaseOutput, "Examples", "GeneratedDependencies.cmake"
    )
    outputEPSDirectory = os.path.join(args.SWGuidBaseOutput, "Art", "Generated")
    mkdir_p(os.path.join(args.SWGuidBaseOutput, "Art", "Generated"))

    outputCDFile = open(outputCMakeDependancies, "w")
    allDependencies = "set(allEPS-DEPS "
    for baseName in dependencyDictionary.keys():
        outstring = f'set("{baseName}-DEPS" '
        allDependencies += ' "${' + f"{baseName}-DEPS" + '}" '
        for output in dependencyDictionary[baseName]:
            epsOutput = os.path.join(
                outputEPSDirectory, os.path.basename(output.replace(".png", ".eps"))
            )
            # chr(92) is backslash
            outstring += f' "{epsOutput.replace(chr(92), "/")}"'
            outputCDFile.write(
                f'CONVERT_INPUT_IMG("{output.replace(chr(92), "/")}" "{epsOutput.replace(chr(92), "/")}" "")\n'
            )
        outstring += ")\n"
        outputCDFile.write(outstring)
    allDependencies += ")\n"
    outputCDFile.write(allDependencies)
    outputCDFile.close()
