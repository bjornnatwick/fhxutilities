'''
    DeltaV fhx Utilities Library
    Rev: 0.0
    
    This library contains functions and classes for DeltaV fhx file parsing and updating.
    
    Design assumptions:
     - The term "Object" used throughout is referencing either a step or transition.
     - If a function name ends with "Data", it returns a dictionary.
     - If a function name ends with "Dataframe", it returns a pandas dataframe.
     - When a function argument is named "fhxLines", that means it requires a list of strings, where
       each string is a row in fhx file.
     - When a function argument is named "lines", that means it requires a string where each row in
       fhx file is separated by a return (\n).

'''

#Importing python libraries
import pandas as pd
from re import sub
from re import finditer

#Importing config files
import fhxconstants as const

#Declare constants from config files
if True:
    NA, ALPHA_NUM, POS_LINE_NUM = const.NA, const.ALPHA_NUM, const.POS_LINE_NUM
    
    CLASSES, NAMED_SETS, FB_DEF, FBS, MODULES = const.CLASSES, const.NAMED_SETS, const.FB_DEF, const.FBS, const.MODULES
    MODULE_CLASS, EM_CLASS, PHASE_CLASS, UNIT_CLASS, PROCCELL_CLASS, EQUTRN_CLASS = const.MODULE_CLASS, const.EM_CLASS, const.PHASE_CLASS, const.UNIT_CLASS, const.PROCCELL_CLASS, const.EQUTRN_CLASS
    CLASS_TYPES = const.CLASS_TYPES

    NAMED_SET = const.NAMED_SET
    RUN, HOLD, RESTART, ABORT, STOP = const.RUN, const.HOLD, const.RESTART, const.ABORT, const.STOP
    PHASE_CMDS = const.PHASE_CMDS
    STEP, ACTION, TRANSITION, VARIABLE, TYPE, NEXT_OBJS, OBJS = const.STEP, const.ACTION, const.TRANSITION, const.VARIABLE, const.TYPE, const.NEXT_OBJS, const.OBJS
    
    INDEX, XPOS, YPOS, HEIGHT, WIDTH = const.INDEX, const.XPOS, const.YPOS, const.HEIGHT, const.WIDTH
    CLASS_NAME, CLASS_DESC, CMD_NAME, COMP_NAME = const.CLASS_NAME, const.CLASS_DESC, const.CMD_NAME, const.COMP_NAME
    STEP_TRAN, STEP_TRAN_NAME, STEP_TRAN_DESC, TRAN_EXP = const.STEP_TRAN, const.STEP_TRAN_NAME, const.STEP_TRAN_DESC, const.TRAN_EXP
    ACT_NAME, ACT_DESC, ACT_TYPE, ACT_QUAL = const.ACT_NAME, const.ACT_DESC, const.ACT_TYPE, const.ACT_QUAL
    ACT_DELAY, ACT_EXP, CFM_EXP, CFM_TMO = const.ACT_DELAY, const.ACT_EXP, const.CFM_EXP, const.CFM_TMO
    QUAL_NO_DELAY, QUAL_NO_CFM = const.QUAL_NO_DELAY, const.QUAL_NO_CFM

    SFC_COL_NAMES = const.SFC_COL_NAMES
                    
    VAR_NAME, VAR_DESC, VAR_TYPE, VAR_VALUE, VAR_GROUP, VAR_CATEGORY = const.VAR_NAME, const.VAR_DESC, const.VAR_TYPE, const.VAR_VALUE, const.VAR_GROUP, const.VAR_CATEGORY
    VAR_COL_NAMES = const.VAR_COL_NAMES
                     
    NS_NAME, NS_DESC = const.NS_NAME, const.NS_DESC
    NS_COL_NAMES = const.NS_COL_NAMES

    VAR_TYPE_TXT = const.VAR_TYPE_TXT
                    
    VAR_TYPE_TXT_BAT = const.VAR_TYPE_TXT_BAT

    VAR_VALUE_TXT = const.VAR_VALUE_TXT
    
    BRANCHES, PREV_BRANCH = const.BRANCHES, const.PREV_BRANCH
    
    STEP_SIZE = const.STEP_SIZE
    INIT_STEP_POS = const.INIT_STEP_POS
    STEP_TRAN_VERT_DIST, TRAN_STEP_VERT_DIST = const.STEP_TRAN_VERT_DIST, const.TRAN_STEP_VERT_DIST
    STEP_TRAN_X_DIFF, BRANCH_DIST, TP_BRANCH_DIST = const.STEP_TRAN_X_DIFF, const.BRANCH_DIST, const.TP_BRANCH_DIST
    TASK_PTR_PARAM_NAME = const.TASK_PTR_PARAM_NAME
    SEGMENT_DIST_BELOW_TRAN = const.SEGMENT_DIST_BELOW_TRAN
    SEGMENT_DIST_ABOVE_STEP = const.SEGMENT_DIST_ABOVE_STEP
    SEGMENT_DIST_LEFT_OF_TRAN = const.SEGMENT_DIST_LEFT_OF_TRAN
    SEGMENT_DIST_RIGHT_OF_TRAN = const.SEGMENT_DIST_RIGHT_OF_TRAN
    SEGMENT_TP_X_DIST = const.SEGMENT_TP_X_DIST
    SEGMENT_SPACING = const.SEGMENT_SPACING
    
    INIT_STEP_NUM = const.INIT_STEP_NUM
    OBJ_NAME_INCREM = const.OBJ_NAME_INCREM
    TERM_NAME = const.TERM_NAME
    OBJ_NAME_NUM_OF_NUMER_CHAR = const.OBJ_NAME_NUM_OF_NUMER_CHAR
    TRAN_INIT_CHAR = const.TRAN_INIT_CHAR
    LAST_STEP_NUM = const.LAST_STEP_NUM
    ACTION_INIT_NUM = const.ACTION_INIT_NUM
    ACTION_NUM_INCREM = const.ACTION_NUM_INCREM
    ACTION_INIT_CHAR = const.ACTION_INIT_CHAR
    ACTION_NS_INIT_CHAR = const.ACTION_NS_INIT_CHAR
    ACTION_NUM_OF_NUMER_CHAR = const.ACTION_NUM_OF_NUMER_CHAR
    

#Declare variables
msgCount = 0
#branchNum = 1

#Declare class(s):
class Paragraph:
    def __init__(self, name, idx, size, type=''):
        self.name = name
        self.idx = idx
        self.size = size
        self.type = type

#Declare function(s):
'''
File data retrieve functions
'''
def BuildLinesFromFhx(fileName):
    '''
    Creates a list of strings from fhx file.
    Every string in list is a row in fhx file.
    '''
    with open(fileName, encoding='utf-16-le') as file:
        fhxLines = [line[:-1] for line in file.readlines()]
        fhxLines[-1] = '}'
    
    return fhxLines

'''
Paragraph saving and parsing functions.
'''
def SaveParagraphs(fhxLines, paragraphTypes=None):
    '''
    Runs through all fhx lines and saves index and size of components. User can specify which
    component types they want to return.
    '''
    paragraphTypes = paragraphTypes or [CLASSES, NAMED_SETS, FB_DEF, FBS, MODULES]
    
    classes, namedSets, fbDefinitions, fbInstances, modules = [], [], [], [], []
    idx, prevIdx = 0, 0
    size = len(fhxLines)
    newSection, endSection = '{', '}'
    
    print('\nBuilding paragraph objects...')
    
    while True:
        #If type request and found, then add new object to list
        if CLASSES in paragraphTypes:
            idx, classes = ParseModuleClass(fhxLines, idx, classes)
            idx, classes = ParseBatchClass(fhxLines, idx, classes)
        if NAMED_SETS in paragraphTypes:
            idx, namedSets = ParseNamedSet(fhxLines, idx, namedSets)
        if (FB_DEF in paragraphTypes or
            FBS in paragraphTypes):
            idx, fbDefinitions, fbInstances = ParseFunctionBlock(fhxLines, idx, fbDefinitions, fbInstances)
        if MODULES in paragraphTypes:
            idx, modules = ParseModuleInstance(fhxLines, idx, modules)
        
        #Increase index
        if idx == prevIdx:
            idx += 1
        
        #Exit if last line
        if idx == size:
            break
        
        #Skip sections that do not need parsing
        if fhxLines[idx] == newSection:
            while fhxLines[idx] != endSection:
                idx += 1
            
        prevIdx = idx
    
    
    #Returns list of paragraphs matching the order entered into function
    paragraphList = []
    
    for type in paragraphTypes:
        if type == CLASSES:
            paragraphList.append(classes)
        if type == NAMED_SETS:
            paragraphList.append(namedSets)
        if type == FB_DEF:
            paragraphList.append(fbDefinitions)
        if type == FBS:
            paragraphList.append(fbInstances)
        if type == MODULES:
            paragraphList.append(modules)
            
    return paragraphList

def ParseModuleClass(fhxLines, idx, classes):
    '''
    Checks if module class has been found. 
    If found, this function determines the name, index, size, class type,
    and adds class to paragraph list.
    '''
    fhxLine = fhxLines[idx]
    startID, endID = 'MODULE_CLASS NAME="', '}'
    moduleID, emID = 'CATEGORY="Library/Control Module Classes/', 'CATEGORY="Library/Equipment Module Classes/'
    
    #Exit if not a class
    if not fhxLine.startswith(startID):
        return idx, classes
    
    #Updates type
    if moduleID in fhxLine:
        type = MODULE_CLASS
    elif emID in fhxLine:
        type = EM_CLASS
    else: #Exit if not EM or module class
        return idx, classes
    
    name = FindString(fhxLine, startID)
    
    #Add new paragraph to classes
    return SaveParagraph(fhxLines, idx, name, endID, classes, type)

def ParseBatchClass(fhxLines, idx, classes):
    '''
    Checks if phase, unit, process cell, or equipment train class has been found. 
    If found, this function determines the name, index, size, class type,
    and adds class to paragraph list.
    '''
    fhxLine = fhxLines[idx]
    startID, endID = 'BATCH_EQUIPMENT_', '}'
    phaseID, unitID = 'PHASE_CLASS NAME="', 'UNIT_MODULE_CLASS NAME="'
    pcID, etID = 'PROCESS_CELL_CLASS NAME="', 'TRAIN_CLASS NAME="'
    
    #Exit if not a class
    if not fhxLine.startswith(startID):
        return idx, classes
    
    #Updates type
    if phaseID in fhxLine:
        name = FindString(fhxLine, startID + phaseID)
        type = PHASE_CLASS
    elif unitID in fhxLine:
        name = FindString(fhxLine, startID + unitID)
        type = UNIT_CLASS
    elif pcID in fhxLine:
        name = FindString(fhxLine, startID + pcID)
        type = PROCCELL_CLASS
    elif etID in fhxLine:
        name = FindString(fhxLine, startID + etID)
        type = EQUTRN_CLASS
    else: #Exit if not phase or unit or process cell or equipment train class
        return idx, classes
    
    #Add new paragraph to classes
    return SaveParagraph(fhxLines, idx, name, endID, classes, type)

def ParseFunctionBlock(fhxLines, idx, fbDefinitions, fbInstances):
    '''
    Checks if function block definition or instance has been found.
    If found, this function determines the name, index, size, function block type,
    and adds function block to paragraph list.
    '''
    fbDefStartID, fbDefEndID = 'FUNCTION_BLOCK_DEFINITION NAME="', '}'
    fbsStartID, fbsEndID = '/* FUNCTION BLOCK(S) USING:"', '*/'
    
    fhxLine = fhxLines[idx]
    
    #Update name and fb lists if line is fb
    if fhxLine.startswith(fbDefStartID):
        name = FindString(fhxLine, fbDefStartID)
        
        idx, fbDefinitions = SaveParagraph(fhxLines, idx, name, fbDefEndID, fbDefinitions)
    
    if fhxLine.startswith(fbsStartID):
        name = FindString(fhxLine, fbsStartID)
        
        idx, fbInstances = SaveParagraph(fhxLines, idx, name, fbsEndID, fbInstances)
    
    return idx, fbDefinitions, fbInstances

def ParseNamedSet(fhxLines, idx, namedSets):
    '''
    Checks if named set has been found.
    If found, this function determines the name, index, size,
    and adds named set to paragraph list.
    '''
    fhxLine = fhxLines[idx]
    startID, endID = 'ENUMERATION_SET NAME="', '}'
    
    #If named set, then update index and named sets
    if fhxLine.startswith(startID):
        name = FindString(fhxLine, startID)
        
        return SaveParagraph(fhxLines, idx, name, endID, namedSets)
        
    return idx, namedSets

def ParseModuleInstance(fhxLines, idx, modules):
    '''
    Checks if module instance has been found. 
    If found, this function determines the name, index, size,
    and adds instanced to paragraph list.
    '''
    fhxLine = fhxLines[idx]
    startID, endID = 'MODULE_INSTANCE TAG="', '}'
    
    #Exit if not a module instance
    if not fhxLine.startswith(startID):
        return idx, modules
    
    #Find module instance name
    name = FindString(fhxLine, startID)
    
    #Add new paragraph to classes
    return SaveParagraph(fhxLines, idx, name, endID, modules)

def SaveParagraph(fhxLines, idx, name, endID, paragraphList, type=''):
    '''
    Appends a single component to paragraphs list.
    '''
    savedIdx = idx
    sfcID = '  SFC_ALGORITHM'
    
    #Determine end of paragraph
    while fhxLines[idx] != endID:
        idx += 1
    
    size = idx - savedIdx
    
    #Append data to list
    if type:
        paragraphList.append(Paragraph(name, savedIdx, size, type))
    else:
        paragraphList.append(Paragraph(name, savedIdx, size))
      
    return idx, paragraphList

'''
Fhx data pulling functions.
'''
def BuildNamedSetData(fhxLines, namedSets):
    '''
    This function iterates through named set paragraphs and pulls
    named set data into a dictionary.
    '''
    namedSetMap = {}
    nameID = 'NAME="'
    size = len(namedSets)
    
    #Iterates through named set paragraphs to build named set data
    for namedSet in namedSets:
        desc = fhxLines[namedSet.idx + 3][15:-1]
        
        namedSetMap.update({namedSet.name: {NS_DESC: desc}})
        
        for i in range(namedSet.idx + 5, namedSet.idx + namedSet.size - 1):
            fhxLine = fhxLines[i]
            
            value = int(fhxLine[14: fhxLine.index(' ', 14)])
            name = FindString(fhxLine, nameID)
            
            namedSetMap[namedSet.name][value] = name
        
        #Progress for terminal
        UpdateTerminal('named set map', size)
    
    return namedSetMap

def BuildStepTranData(lines, fbLineNum=0):
    '''
    Finds step and transition data and returns a dictionary.
    '''
    stepNameID, tranNameID = '    STEP NAME="', '    TRANSITION NAME="'
    endID = '\n    }'
    stepLocID, tranLocID = ' STEP="', ' TRANSITION="'
    stepTranConID, tranStepConID  = '    STEP_TRANSITION_CONNECTION STEP=', '    TRANSITION_STEP_CONNECTION TRANSITION='
    tranExpID = '      EXPRESSION="'
    xPosID, yPosID = ' X=', ' Y='
    tranDescID, tranEndID = '      DESCRIPTION="', '\n    }'
    objMap = {}
    
    #Save step data
    stepIdxs = [x.start() for x in finditer(stepNameID, lines)]
    
    for stepIdx in stepIdxs:
        stepName = FindString(lines, stepNameID, startIdx=stepIdx)
        lineNum = fbLineNum + lines[:stepIdx].count('\n')
        xPos = int(FindString(lines, xPosID, ' ', startIdx=stepIdx))
        yPos = int(FindString(lines, yPosID, ' ', startIdx=stepIdx))
        
        stepLines = lines[stepIdx:lines.index(endID, stepIdx) + 1]
        size = stepLines.count('\n')
        rectIdx = stepLines.index(xPosID)
        rectLineNum = lineNum + stepLines[:rectIdx].count('\n')
        
        
        objMap[stepName] = {'Line Number': lineNum, 
                            'Size': size, 
                            TYPE:STEP, 
                            XPOS: xPos, 
                            YPOS: yPos, 
                            NEXT_OBJS:[], 
                            'Previous Objects': [], 
                            TRAN_EXP:NA, 
                            POS_LINE_NUM:rectLineNum}
    
    #Save transition data
    tranIdxs = [x.start() for x in finditer(tranNameID, lines)]
    
    for tranIdx in tranIdxs:
        tranName = FindString(lines, tranNameID, startIdx=tranIdx)
        lineNum = fbLineNum + lines[:tranIdx].count('\n')
        xPos = int(FindString(lines, xPosID, ' ', startIdx=tranIdx))
        yPos = int(FindString(lines, yPosID, ' ', startIdx=tranIdx))
        exp = FindString(lines, tranExpID, startIdx=tranIdx, isExp=True)
        
        tranLines = lines[tranIdx:lines.index(endID, tranIdx) + 1]
        
        if tranDescID in tranLines:
            desc = FindString(tranLines, tranDescID)
        else:
            desc = ''
        
        size = tranLines.count('\n')
        posIdx = tranLines.index(xPosID)
        expIdx = tranLines.index(tranExpID)
        posLineNum = lineNum + tranLines[:posIdx].count('\n')
        expLineNum = lineNum + tranLines[:expIdx].count('\n')
        
        objMap[tranName] = {'Line Number': lineNum,
                            'Size': size,
                            TYPE: TRANSITION, 
                            'Description': desc,
                            XPOS: xPos, 
                            YPOS: yPos, 
                            NEXT_OBJS: [], 
                            TRAN_EXP: exp, 
                            POS_LINE_NUM: posLineNum, 
                            'Previous Objects': [], 
                            'Expression Line Number': expLineNum, 
                            'Expression Number of Lines': 1 + exp.count('\n')}
    
    #Save step/transition order data
    stepTranIdxs = [x.start() for x in finditer(stepTranConID, lines)]
    
    for stepTranIdx in stepTranIdxs:
        step = FindString(lines, stepLocID, startIdx=stepTranIdx)
        tran = FindString(lines, tranLocID, startIdx=stepTranIdx)
        
        objMap[step][NEXT_OBJS].append(tran)
        objMap[tran]['Previous Objects'].append(step)
        
    tranStepIdxs = [x.start() for x in finditer(tranStepConID, lines)]
    
    for tranStepIdx in tranStepIdxs:
        step = FindString(lines, stepLocID, startIdx=tranStepIdx)
        tran = FindString(lines, tranLocID, startIdx=tranStepIdx)
        
        objMap[tran][NEXT_OBJS].append(step)
        objMap[step]['Previous Objects'].append(tran)
        objMap[tran]['Segment Line Number'] = fbLineNum + lines[:tranStepIdx].count('\n')
    
    return objMap

ObjectNames = lambda objMap: list(objMap.keys())

def BuildActionData(lines, objMap, fbLineNum=0):
    '''
    Finds action data and returns a dictionary.
    '''
    stepNameID = '    STEP NAME="'
    stepEndID, actionEndID = '\n    }', '\n      }'
    actionNameID, actionDescID = '      ACTION NAME="', '        DESCRIPTION="'
    actionDelayExpID, actionDelayTimeID, actionQualID = '        DELAY_EXPRESSION="', '        DELAY_TIME=', '        QUALIFIER='
    
    actionMap, actionsInStep = {}, {}
    steps = [object for object in list(objMap.keys()) if objMap[object][TYPE] == STEP]
    
    for step in steps:
        stepIdx = lines.index(stepNameID + step)
        
        stepSection = lines[stepIdx:lines.index(stepEndID, stepIdx) + 1]
        
        actionIdxs = [x.start() for x in finditer(actionNameID, stepSection)]
        
        #If no actions, skip to next step
        if not actionIdxs:
            continue
        
        #Save action data to action map
        for idx, actionIdx in enumerate(actionIdxs):
            name = FindString(stepSection, actionNameID, startIdx=actionIdx)
            qualifier = FindString(stepSection, actionQualID, '\n', startIdx=actionIdx)
            lineNum = fbLineNum + lines[:stepIdx].count('\n') + stepSection[:actionIdx].count('\n')
            
            desc, delayExp = '', ''
            
            actionSection = stepSection[actionIdx:stepSection.index(actionEndID, actionIdx) + 1]
            
            size = actionSection.count('\n')
            if actionDescID in actionSection:
                desc = FindString(stepSection, actionDescID, startIdx=actionIdx)
            
            if actionDelayExpID in actionSection:
                delayExp = FindString(stepSection, actionDelayExpID, startIdx=actionIdx, isExp=True)
                delayIdx = actionSection.index(actionDelayExpID)
            elif actionDelayTimeID in actionSection:
                delayIdx = actionSection.index(actionDelayTimeID)
            else:
                delayIdx = actionIdx + 1
            
            delayLineNum = lineNum + actionSection[:delayIdx].count('\n')
            
            stepAction = ''.join([step, '/', name])
            
            #Update action map
            actionMap[stepAction] = {'Line Number': lineNum,
                                     'Size': size,
                                     'Description': desc,
                                     'Qualifier': qualifier,
                                     'Delay Expression': delayExp,
                                     'Delay Line Number': delayLineNum,
                                     'Delay Number of Lines': 1 + delayExp.count('\n'),
                                     'Neighboring Actions': []}
            
            #Update actions in step for next section
            if not idx:
                actionsInStep[step] = [name]
            else:
                actionsInStep[step].append(name)
        
        #Update neighboring actions in action map
        for stepAction in list(actionMap.keys()):
            [step, currentAction] = stepAction.split('/')
            
            actionMap[stepAction]['Neighboring Actions'] = [action for action in actionsInStep[step] if action != currentAction]
    
    return actionMap

def BuildClassCompData(fhxLines, classes, namedSetMap, fbInstances):
    '''
    Builds a dictionary to tie function block names to commands in EMs or phases.
    '''
    descID = '  DESCRIPTION="'
    cmdSetID = '    COMMAND_SET="'
    fbNameID, fbCmdID, defID = '  FUNCTION_BLOCK NAME="', '  FUNCTION_BLOCK NAME="COMMAND_', '" DEFINITION="'
    fbInstanceID = '\n"'
    
    classCompMap, classDescTypeMap = {}, {}
    size = len(classes) + len(fbInstances)
    
    for Class in classes:
        name = Class.name
        
        lines = '\n'.join(fhxLines[Class.idx: Class.idx + Class.size])
        
        #EM class
        if Class.type == EM_CLASS and cmdSetID in lines:
            desc = FindString(lines, descID)
            namedSet = FindString(lines, cmdSetID)
            
            classDescTypeMap[name] = {'Description':desc, 'Type':EM_CLASS}
            
            cmdIdxs = [x.start() for x in finditer(fbCmdID, lines)]
            
            for cmdIdx in cmdIdxs:
                cmdNum = int(FindString(lines, fbCmdID, startIdx=cmdIdx))
                compName = FindString(lines, defID, startIdx=cmdIdx)
                cmdName = namedSetMap[namedSet][cmdNum]
                
                if compName in list(classCompMap.keys()):
                    classCompMap[compName]['Name'] += ', ' + name
                    classCompMap[compName]['Description'] = 'Multiple Classes'
                else:
                    classCompMap[compName] = {'Name':name, 'Description':desc, 'Command':cmdName, 'Type':EM_CLASS}
                
        #Phase class
        if Class.type == PHASE_CLASS:
            desc = FindString(lines, descID)
            
            classDescTypeMap[name] = {'Description':desc, 'Type':PHASE_CLASS}
            
            for cmd in PHASE_CMDS:
                compName = FindString(lines, fbNameID + cmd + defID)
                
                if compName in list(classCompMap.keys()):
                    classCompMap[compName]['Name'] += ', ' + name
                    classCompMap[compName]['Description'] = 'Multiple Classes'
                else:
                    classCompMap[compName] = {'Name':name, 'Description':desc, 'Command':cmd[:-6], 'Type':PHASE_CLASS}
        
        #Progress for terminal
        UpdateTerminal('class/composite map', size)
    
    #For function block definitions without class info in fhx, add by referencing "function blocks using" section
    for fb in fbInstances:
        fbName = fb.name
        
        if fbName not in list(classCompMap.keys()):
            lines = '\n'.join(fhxLines[fb.idx: fb.idx + fb.size])
            
            instanceIdxs = [x.start() for x in finditer(fbInstanceID, lines)]
            
            for instanceIdx in instanceIdxs:
                moduleName = FindString(lines, fbInstanceID, endChar='/', startIdx=instanceIdx)
                compName = FindString(lines, '/', startIdx=instanceIdx)
                
                if fbName in list(classCompMap.keys()):
                    classCompMap[fbName]['Name'] += ', ' + moduleName
                    classCompMap[fbName]['Description'] = 'Multiple Classes'
                    
                    if moduleName in list(classDescTypeMap.keys()):
                        classCompMap[fbName]['Type'] = classDescTypeMap[moduleName]['Type']
                else:
                    if moduleName in list(classDescTypeMap.keys()):
                        classCompMap[fbName] = {'Name':moduleName, 'Description':classDescTypeMap[moduleName]['Description'], 'Command':compName, 'Type':classDescTypeMap[moduleName]['Type']}
                    else:
                        classCompMap[fbName] = {'Name':moduleName, 'Description':'', 'Command':compName, 'Type':''}
                        
        #Progress for terminal
        UpdateTerminal('class/composite map', size)
    
    return classCompMap

FunctionBlocks = lambda classCompMap: list(classCompMap.keys())

'''
Dataframe building and modifying functions.
'''
def BuildNamedSetDataframe(namedSetMap):
    '''
    Builds a named set dataframe from a named set dictionary
    '''
    namedSetData = pd.DataFrame(columns = NS_COL_NAMES)
    size = len(namedSetMap.keys())
    
    for namedSet in list(namedSetMap.keys()):
        desc = namedSetMap[namedSet][NS_DESC]
        namedSetRow = [namedSet, desc] + [None for _ in range(256)]
        namedSetData = namedSetData.append(pd.DataFrame([namedSetRow], columns = NS_COL_NAMES), ignore_index = True)
        
        #Progress for terminal
        UpdateTerminal('named set data', size)
    
    #Set named set name to Idx
    namedSetData.set_index(NS_NAME, inplace=True)
    
    #Update dataframe columns 0-255 values
    for namedSet in list(namedSetMap.keys()):
        for number in list(namedSetMap[namedSet].keys()):
            namedSetData.at[namedSet, number] = namedSetMap[namedSet][number]
    
    #Delete columns with no data
    namedSetData.dropna(axis=1, how='all', inplace=True)
    
    return namedSetData

def BuildVariableDataframe(fhxLines, classes):
    '''
    Builds equipment module and/or phase variable dataframes.
    '''
    classDescID, batchParID = '\n  DESCRIPTION="', '\n    BATCH_PHASE_PARAMETER NAME="'
    varNameID, varMatrixID, varInstanceID, varTypeID, varEndID = '  ATTRIBUTE NAME="', '    ATTRIBUTE_MATRIX NAME="', '  ATTRIBUTE_INSTANCE NAME="', ' TYPE=', '  }'
    varGroupID, varCategoryID = '    GROUP="', '    CATEGORY { CATEGORY='
    valueID, valueStrID, setID= '    VALUE { CV=', '    VALUE { CV="', '      SET="'
    stringValueID, enumSetID = '      STRING_VALUE="', '      ENUM_SET="'
    mdTarID, mdNorID = '      TARGET=', '      NORMAL='
    valueRefID, actExpID = '    VALUE { REF="', '      VALUE { TYPE=ACTION EXPRESSION="'
    almPrioID, almTypeID, almAttrID = '      PRIORITY_NAME="', '      ATYP="', '      ALMATTR="'
    batDescID, batGroupID, varDirectID = '\n      DESCRIPTION="', '\n      GROUP="', ' DIRECTION='
    
    emVarData, phaseVarData = pd.DataFrame(columns = VAR_COL_NAMES), pd.DataFrame(columns = VAR_COL_NAMES)
    
    size = len(classes)
    print(f'Building variable data: 0.0 % ', end='\r')
    
    for Class in classes:
        lines = '\n'.join(fhxLines[Class.idx: Class.idx + Class.size])
        
        df, batDf = pd.DataFrame(columns = VAR_COL_NAMES), pd.DataFrame(columns = VAR_COL_NAMES)
        
        #Append batch parameters to dataframe        
        if Class.type == PHASE_CLASS:
            batIdxs = [x.start() for x in finditer(batchParID, lines)]
            
            for batIdx in batIdxs:
                name = FindString(lines, batchParID, startIdx=batIdx)
                desc = FindString(lines, batDescID, startIdx=batIdx)
                type = FindString(lines, varTypeID, ' ', startIdx=batIdx)
                direction = FindString(lines, varDirectID, '\n', startIdx=batIdx)
                group = FindString(lines, batGroupID, startIdx=batIdx)
                
                batDf = batDf.append(pd.DataFrame([[Class.name,
                                         name,
                                         desc,
                                         VAR_TYPE_TXT_BAT[type][direction],
                                         '', #value, updated in final section
                                         group,
                                         '']], columns = VAR_COL_NAMES), ignore_index = True) #no category field
        
        #Append non-batch parameters to dataframe
        if Class.type == EM_CLASS or Class.type == PHASE_CLASS:
            varIdxs = [x.start() for x in finditer(varNameID, lines)]
            
            for varIdx in varIdxs:
                name = FindString(lines, varNameID, startIdx=varIdx)
                
                if name not in batDf[VAR_NAME].tolist():
                    type = FindString(lines, varTypeID, '\n', startIdx=varIdx)
                    
                    varSection = lines[varIdx:lines.index(varEndID, varIdx) + 1]
                    
                    group = ''
                    if varGroupID in varSection:
                        group = FindString(lines, varGroupID, startIdx=varIdx)
                    
                    catIdxs = [x.start() for x in finditer(varCategoryID, varSection)]
                    
                    categories = ''
                    for catIdx in catIdxs:
                        if categories:
                            categories += ', ' + FindString(varSection, varCategoryID, ' ', catIdx)
                        else:
                            categories += FindString(varSection, varCategoryID, ' ', catIdx)
                    
                    df = df.append(pd.DataFrame([[Class.name,
                                             name,
                                             NA,
                                             VAR_TYPE_TXT[type],
                                             '', #value, updated in final section
                                             group,
                                             categories]], columns = VAR_COL_NAMES), ignore_index = True)
        
        #Update instance value of parameters
        if Class.type == EM_CLASS or Class.type == PHASE_CLASS:
            instIdxs = [x.start() for x in finditer(varInstanceID, lines)]
                        
            for instIdx in instIdxs:
                name = FindString(lines, varInstanceID, startIdx=instIdx)
                
                instSection = lines[instIdx:lines.index(varEndID, instIdx) + 1]
                
                value = ''
                if valueStrID in instSection:
                    value = FindString(instSection, valueStrID)
                
                elif valueID in instSection:
                    value = FindString(instSection, valueID, ' ')
                
                if setID in instSection:
                    namedSet = FindString(instSection, setID)
                    nsValue = FindString(instSection, stringValueID)
                    
                    value = namedSet + ':' + nsValue
            
                if enumSetID in instSection:
                    value = FindString(instSection, enumSetID)
                
                if mdTarID in instSection:
                    target = FindString(instSection, mdTarID, '\n')
                    normal = FindString(instSection, mdNorID, '\n')
                    
                    value = target + ', ' + normal
                    
                if valueRefID in instSection:
                    value = FindString(instSection, valueRefID)
                    
                if almPrioID in instSection:
                    almPrio = FindString(instSection, almPrioID)
                    almType = FindString(instSection, almTypeID)
                    almAttr = FindString(instSection, almAttrID)
                    
                    value = ', '.join([almPrio, almType, almAttr])
                
                #Updates text value if in dictionary
                if value in list(VAR_VALUE_TXT.keys()):
                    value = VAR_VALUE_TXT[value]
                
                #Updates value of variable in dataframe
                if name in df[VAR_NAME].tolist():
                    df.at[df[VAR_NAME] == name, VAR_VALUE] = value
                
                if name in batDf[VAR_NAME].tolist():
                    batDf.at[batDf[VAR_NAME] == name, VAR_VALUE] = value
        
        #Merge and sort dataframes, then update variable dataframe
        df = df.append(batDf, ignore_index = True)
        df.sort_values(VAR_NAME, inplace=True)
        
        if Class.type == EM_CLASS:
            emVarData = emVarData.append(df, ignore_index = True)
        
        if Class.type == PHASE_CLASS:
            phaseVarData = phaseVarData.append(df, ignore_index = True)
        
        #Progress for terminal
        UpdateTerminal('variable data', size)
    
    emVarData.drop(VAR_DESC, axis=1, inplace=True)
    
    return emVarData, phaseVarData

def BuildSFCDataframe(fhxLines, fbDefinitions, classCompMap, classType):
    '''
    Builds equipment module or phase step and transition dataframe.
    '''
    stepTranConID, tranStepConID, stepLocID, tranLocID, initStepID = '    STEP_TRANSITION_CONNECTION STEP=', '    TRANSITION_STEP_CONNECTION TRANSITION=', ' STEP="', ' TRANSITION="', '    INITIAL_STEP='
    stepNameID, stepDescID = '    STEP NAME="', '      DESCRIPTION="'
    xPosID, yPosID, hPosID, wPosID = ' X=', ' Y=', ' H=', ' W='
    actionNameID, actionDescID, actionExpID = '      ACTION NAME="', '        DESCRIPTION="', '        EXPRESSION="'
    actionDelayTimeID, actionDelayExpID = '        DELAY_TIME=', '        DELAY_EXPRESSION="'
    actionTypeID, actionQualID = '        ACTION_TYPE=', '        QUALIFIER='
    confirmExpID, confirmTmoID, confirmTmoExpID = '        CONFIRM_EXPRESSION="', '        CONFIRM_TIME_OUT=', '        CONFIRM_TIME_OUT_EXPRESSION="'
    tranNameID, tranDescID, tranExpID = '    TRANSITION NAME="', '      DESCRIPTION="', '      EXPRESSION="'
    stepEndID, actionEndID, tranEndID = '\n    }', '\n      }', '\n    }'
    stepTranConID, tranStepConID = '\n    STEP_TRANSITION_CONNECTION STEP="', '\n    TRANSITION_STEP_CONNECTION TRANSITION="'
    stepLocID, tranLocID, initStepID = ' STEP="', ' TRANSITION="', '\n    INITIAL_STEP="'
    sfcID = '  SFC_ALGORITHM'
    
    classData = {'Name':'', 'Desc':'', 'Type':'', 'Cmd Name':'', 'Comp Name':''}
    stepDataCleared = {'Name':'', 'Desc':'', 'X':0, 'Y':0, 'H':0, 'W':0}
    actionDataCleared = {'Name':'', 'Desc':'', 'Delay':NA, 'Type':'', 'Qual':'', 'Exp':'', 'CfmExp':NA, 'CfmTmo':NA}
    tranDataCleared = {'Name':'', 'Desc':'', 'Exp':'', 'X':0, 'Y':0}
    stepData, actionData, tranData = stepDataCleared, actionDataCleared, tranDataCleared
    sfcDF = pd.DataFrame(columns = SFC_COL_NAMES)
    objOrders = {}
    size = len(fbDefinitions)
    
    for fb in fbDefinitions:
        fbName = fb.name
        
        #Progress for terminal
        UpdateTerminal('step and transition data for ' + classType, size)
        
        #Build string for fb
        lines = '\n'.join(fhxLines[fb.idx: fb.idx + fb.size])
        
        #Skip composite if not sfc or not in comp-class map
        if (sfcID not in lines or
            fbName not in list(classCompMap.keys())):
            continue
        
        type = classCompMap[fbName]['Type']
        
        #Skip composite if class type is not requested
        if type != classType:
            continue
        
        #Save class data
        classData['Name'] = classCompMap[fbName]['Name']
        classData['Desc'] = classCompMap[fbName]['Description']
        classData['Type'] = type
        classData['Cmd Name'] = classCompMap[fbName]['Command']
        classData['Comp Name'] = fbName
        
        
        stepIdxs = [x.start() for x in finditer(stepNameID, lines)]
        
        #Save step data
        for stepIdx in stepIdxs:
            stepData['Name'] = FindString(lines, stepNameID, startIdx=stepIdx)
            stepData['X'] = int(FindString(lines, xPosID, ' ', startIdx=stepIdx))
            stepData['Y'] = int(FindString(lines, yPosID, ' ', startIdx=stepIdx))
            stepData['H'] = int(FindString(lines, hPosID, ' ', startIdx=stepIdx))
            stepData['W'] = int(FindString(lines, wPosID, ' ', startIdx=stepIdx))
            
            stepSection = lines[stepIdx:lines.index(stepEndID, stepIdx) + 1]
            
            if stepDescID in stepSection:
                stepData['Desc'] = FindString(lines, stepDescID, startIdx=stepIdx)
            
            actionIdxs = [x.start() for x in finditer(actionNameID, stepSection)]
            
            #If no actions, append step row to dataframe and skip to next step
            if not actionIdxs:
                sfcDF = AppendSFCRow(sfcDF, STEP, classData, stepData)
                continue
            
            #Save action data
            for actionIdx in actionIdxs:
                actionData['Name'] = FindString(stepSection, actionNameID, startIdx=actionIdx)
                actionData['Type'] = FindString(stepSection, actionTypeID, '\n', startIdx=actionIdx)
                actionData['Qual'] = FindString(stepSection, actionQualID, '\n', startIdx=actionIdx)
                actionData['Exp'] = FindString(stepSection, actionExpID, startIdx=actionIdx, isExp=True)
                
                actionData['Desc'], actionData['Delay'], actionData['CfmExp'], actionData['CfmTmo'] = '', NA, NA, NA
                
                actionSection = stepSection[actionIdx:stepSection.index(actionEndID, actionIdx) + 1]
                
                if actionDescID in actionSection:
                    actionData['Desc'] = FindString(stepSection, actionDescID, startIdx=actionIdx)
                if actionDelayTimeID in actionSection:
                    actionData['Delay'] = FindString(stepSection, actionDelayTimeID, '\n', startIdx=actionIdx)
                if actionDelayExpID in actionSection:
                    actionData['Delay'] = FindString(stepSection, actionDelayExpID, startIdx=actionIdx, isExp=True)
                if confirmExpID in actionSection:
                    actionData['CfmExp'] = FindString(stepSection, confirmExpID, startIdx=actionIdx, isExp=True)
                if confirmTmoID in actionSection:
                    actionData['CfmTmo'] = FindString(stepSection, confirmTmoID, '\n', startIdx=actionIdx)
                if confirmTmoExpID in actionSection:
                    actionData['CfmTmo'] = FindString(stepSection, confirmTmoExpID, startIdx=actionIdx, isExp=True)
                
                #All action and step info has been pulled. Now append to dataframe
                sfcDF = AppendSFCRow(sfcDF, ACTION, classData, stepData, actionData)
                
                #Clear action data
                actionData = actionDataCleared
            
            #Clear step data
            stepData = stepDataCleared
            
        tranIdxs = [x.start() for x in finditer(tranNameID, lines)]
        
        #Save transition data
        for tranIdx in tranIdxs:
            tranData['Name'] = FindString(lines, tranNameID, startIdx=tranIdx)
            tranData['Exp'] = FindString(lines, tranExpID, startIdx=tranIdx, isExp=True)
            tranData['X'] = int(FindString(lines, xPosID, ' ', startIdx=tranIdx))
            tranData['Y'] = int(FindString(lines, yPosID, ' ', startIdx=tranIdx))
            
            tranData['Desc'] = ''
            
            tranSection = lines[tranIdx:lines.index(tranEndID, tranIdx) + 1]
            
            if tranDescID in tranSection:
                tranData['Desc'] = FindString(lines, tranDescID, startIdx=tranIdx)
            
            #Append transition row to sfc dataframe
            sfcDF = AppendSFCRow(sfcDF, TRANSITION, classData, tranData)
            
            #Clear transition data
            tranData = tranDataCleared
        
        #Build list of ordered steps/transitions
        objMap = BuildStepTranData(lines)
        objOrders[fbName] = BuildSFCOrder([FindInitStep(lines)], objMap)
        
    #Order sfc dataframe
    sfcDF = OrderDataframe(sfcDF, objOrders, classCompMap)
    
    return sfcDF

def AppendSFCRow(sfcDF, type, classData, typeData, actionData={}):
    '''
    Appends step, action, or transition data to dataframe
    '''
    #Append data based on type
    #Type is Step with no actions
    if type == STEP:
        sfcDF = sfcDF.append(pd.DataFrame([[0,
                                            classData['Name'],
                                            classData['Desc'],
                                            classData['Cmd Name'],
                                            classData['Comp Name'],
                                            type,
                                            typeData['Name'],
                                            typeData['Desc'],
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA]], columns = SFC_COL_NAMES), ignore_index = True)
    #Type is Action
    if type == ACTION:
        sfcDF = sfcDF.append(pd.DataFrame([[0,
                                            classData['Name'],
                                            classData['Desc'],
                                            classData['Cmd Name'],
                                            classData['Comp Name'],
                                            STEP,
                                            typeData['Name'],
                                            typeData['Desc'],
                                            NA,
                                            actionData['Name'],
                                            actionData['Desc'],
                                            actionData['Type'],
                                            actionData['Qual'],
                                            actionData['Delay'],
                                            actionData['Exp'],
                                            actionData['CfmExp'],
                                            actionData['CfmTmo']]], columns = SFC_COL_NAMES), ignore_index = True)
    #Type is Transition
    if type == TRANSITION:
        sfcDF = sfcDF.append(pd.DataFrame([[0,
                                            classData['Name'],
                                            classData['Desc'],
                                            classData['Cmd Name'],
                                            classData['Comp Name'],
                                            type,
                                            typeData['Name'],
                                            typeData['Desc'],
                                            typeData['Exp'],
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA,
                                            NA]], columns = SFC_COL_NAMES), ignore_index = True)
    
    return sfcDF

def OrderDataframe(sfcDF, objOrders, classCompMap):
    '''
    Builds step and transition order.
    '''
    idx = 1
    size = len(list(objOrders.keys()))
    classType = ''
    
    #Sort dataframes by action numbers
    sfcDF['Action Numbers'] = sfcDF[ACT_NAME].apply(lambda x: sub("[^0-9]", "", x))
    sfcDF.sort_values('Action Numbers', inplace=True)
    sfcDF.drop(columns='Action Numbers', inplace=True)
    sfcDF.reset_index(drop=True, inplace=True)
    
    #Loop through composites to update INDEX column with order
    for composite in list(objOrders.keys()):
        objOrder = objOrders[composite]
        
        if composite in list(classCompMap.keys()):
            className = classCompMap[composite]['Name']
            classDesc = classCompMap[composite]['Description']
            cmdName = classCompMap[composite]['Command']
            classType = classCompMap[composite]['Type']
            
            for obj in objOrder:
                objectDF = sfcDF[(sfcDF[COMP_NAME] == composite) & (sfcDF[STEP_TRAN_NAME] == obj)]
                
                for i, row in objectDF.iterrows():
                    sfcDF.at[i, INDEX] = idx
                    
                    idx += 1
            
        #Progress for terminal
        if classType:
            UpdateTerminal('step and transition order for ' + classType, size)
        else:
            UpdateTerminal('step and transition order', size)
        
    #Sort by Index
    sfcDF.sort_values(INDEX, inplace=True)
    
    #Set Index
    sfcDF.set_index(INDEX, inplace=True)
    
    #If embedded composite, clear composite name
    sfcDF[COMP_NAME] = sfcDF[COMP_NAME].apply(lambda comp: NA if comp[:2] == '__' and comp[-2:] == '__' else comp)
    
    return sfcDF

def BuildSFCOrder(objOrder, objMap, idx=0):
    '''
    This recursive function builds step and transition order.
    '''
    SkipObject = lambda obj: obj in objOrder
    
    #Next objects is a ist of steps or transitions
    nextObjs = objMap[objOrder[idx]][NEXT_OBJS]
    
    #If there are no objects, then exit
    if not nextObjs:
        return objOrder
    
    #Sort list of objects
    nextObjs.sort()
    
    #Create list that determines if objects should be skipped. Object is skipped if already in order list
    skipObj = [(obj in objOrder) for obj in nextObjs]
    skipObj = list(map(SkipObject, nextObjs))
    #If all objects should be skipped, then exit
    if all(skipObj):
        return objOrder
    
    #Iterate through objects and append to order list if not skipped
    for i in range(0, len(nextObjs)):
        if not skipObj[i]:
            objOrder.append(nextObjs[i])
    
    strtIdx = objOrder.index(nextObjs[0])
    
    #Recall function for objects that were appended
    for i in range(strtIdx, len(objOrder)):
        objOrder = BuildSFCOrder(objOrder, objMap, i)
    
    return objOrder

'''
Branch building and modifying functions.
'''
def BuildBranch(object, objPos, objMap, branchMap=None, type='', prevBranchNum=0, leftBranches=None, rightBranches=None, sortType=XPOS):
    '''
    This recursive function builds all branches and saves to a dictionary.
    '''
    if not prevBranchNum:
        global branchNum
        branchNum = 1
    
    ObjectType = lambda obj: objMap[obj][TYPE]
    ObjectXPos = lambda obj: objMap[obj][XPOS]
    ObjectXPosDiff = lambda nextObj: abs(objMap[object][XPOS] + xAdjust - objMap[nextObj][XPOS])
    IsStep = lambda obj: ObjectType(obj) == STEP
    IsObjectInBranch = lambda brnchNum: object in branchMap[brnchNum][OBJS]
    BranchYPos = lambda brnchNum: branchMap[brnchNum][YPOS]
    IsLeftBranch = lambda nextObj: objMap[nextObj][XPOS] < objMap[object][XPOS]
    
    branchMap = branchMap or {}
    leftBranches = leftBranches or []
    rightBranches = rightBranches or []
    
    newBranches, newBranchesPos, newBranchTypes = [], [], []
    branchPosAdjust = 0
    
    #If there are no previous branches, then this is the trunk
    if not prevBranchNum:
        type = 'Trunk'
    
    #If task pointer parameter in expression and previous branch is trunk, then update type to task pointer
    if (TASK_PTR_PARAM_NAME in objMap[object][TRAN_EXP] and
        prevBranchNum == 1):
        type += ' Task Pointer'
    
    #Build branch instance
    branch = {OBJS:[object], 
              'Object Distances':[], 
              'Length':0, 
              XPOS:objPos[XPOS], 
              YPOS:objPos[YPOS], 
              PREV_BRANCH:prevBranchNum, 
              BRANCHES:[], 
              'Branch Locations':[], 
              TYPE:type, 
              'Left Branches':[], 
              'Right Branches':[], 
              'Left Shift Distance':0, 
              'Right Shift Distance':0,
              'End Step': ''}
    
    while True:
        #Next objects is a list of steps or transitions
        nextObjs = objMap[object][NEXT_OBJS]
        
        #If there are no objects, then exit loop
        if not nextObjs:
            break
        
        #Determine position of next object by checking type current object
        if objMap[object][TYPE] == STEP:
            objPos[XPOS] += STEP_TRAN_X_DIFF
            objPos[YPOS] += STEP_TRAN_VERT_DIST
            xAdjust = STEP_TRAN_X_DIFF
            branch['Object Distances'].append(STEP_TRAN_VERT_DIST)
        else:
            objPos[XPOS] -= STEP_TRAN_X_DIFF
            objPos[YPOS] += TRAN_STEP_VERT_DIST
            xAdjust = 0 - STEP_TRAN_X_DIFF
            branch['Object Distances'].append(TRAN_STEP_VERT_DIST)
        
        #Sort list of objects
        if sortType == ALPHA_NUM: #Sort alphabetical numeric
            nextObjs.sort()
            
            idx = 0
        
        #Sort list by position
        if sortType == XPOS:
            nextObjs = sorted(nextObjs, key = ObjectXPos)
            
            #Determine which obj is closest in horizontial position to previous object
            xPosDiffs = list(map(ObjectXPosDiff, nextObjs))
            xPosMin = min(xPosDiffs)
            idx = xPosDiffs.index(xPosMin)
        
        #Determine next object, and remove from list
        object = nextObjs.pop(idx)
        
        #Exit if next object is in current branch, and set type to loop back
        if (object in branch[OBJS]):
            branch['Object Distances'].pop(-1)
            branch[TYPE] += ' Loop Back to Current Branch'
            branch['End Step'] = object
            
            break
        
        #Exit if next object is in previous branches, and determine type
        branchNumbers = BranchNumbers(branchMap)
        nextBranch = list(filter(IsObjectInBranch, branchNumbers))
        
        if nextBranch:
            branch['Object Distances'].pop(-1)
            
            nextBranchNum = nextBranch[0]
            
            nextObjYPos = sum(branchMap[nextBranchNum]['Object Distances'][:branchMap[nextBranchNum][OBJS].index(object)]) + BranchYPos(nextBranchNum)
            
            if nextObjYPos > branch[YPOS]:
                branch[TYPE] += ' Parallel'
                if IsStep(branch[OBJS][0]):
                    branch[TYPE] += ' Step'
                else:
                    branch[TYPE] += ' Transition'
                
                if IsObjectInBranch(branch[PREV_BRANCH]):
                    branch[TYPE] += ' to Previous Branch'
                else:
                    branch[TYPE] += ' to Other Branch'
                
            else:
                if IsObjectInBranch(branch[PREV_BRANCH]):
                    branch[TYPE] += ' Loop Back to Previous Branch'
                else:
                    branch[TYPE] += ' Loop Back to Other Branch'
            
            branch['End Step'] = object
            
            break
        
        #Update branch locations
        branch['Branch Locations'].append(nextObjs)
        
        #Add object closest in horizontial position to previous object to branch
        branch[OBJS].append(object)
        
        #If there are no branches, then continue
        if not nextObjs:
            continue
        
        leftBranches = sum(1 for obj in nextObjs if IsLeftBranch(obj))
        
        rightBranches = 0
        
        #Update branch x position adjustment for left branches
        branchPosAdjust = max(branchPosAdjust, leftBranches)
        
        #Add new branch starting object and position to lists
        for nextObj in nextObjs:
            if not IsLeftBranch(nextObj):
                rightBranches += 1
                xPos = objPos[XPOS] + rightBranches * BRANCH_DIST
                newBranchTypes.append('Right')
            else:
                xPos = objPos[XPOS] - leftBranches * BRANCH_DIST
                leftBranches -= 1
                newBranchTypes.append('Left')
            
            newBranchesPos.append({XPOS: xPos, YPOS: objPos[YPOS]})
        
        newBranches = newBranches + nextObjs
    
    #Update branch length
    branch['Length'] = sum(branch['Object Distances'])
    
    #Add branch to list of branches
    branchMap[branchNum] = branch
    
    #Call function for new branches
    origBrnchNum = branchNum
    newBranchNums = []
    
    for i in range(len(newBranches)):
        branchNum += 1
        newBranchNums.append(branchNum)
        branchMap[origBrnchNum][BRANCHES].append(branchNum)
        
        branchMap = BuildBranch(newBranches[i], newBranchesPos[i], objMap, branchMap, newBranchTypes[i], origBrnchNum)
    
    #Update left and right branches for new branches
    for idx, newBranchNum in enumerate(newBranchNums):
        IsYPosEqual = lambda num: BranchYPos(num) == BranchYPos(newBranchNum)
        
        leftBranches = list(filter(IsYPosEqual, newBranchNums[:idx]))
        rightBranches = list(filter(IsYPosEqual, newBranchNums[idx + 1:]))
        
        branchMap[newBranchNum]['Left Branches'] = leftBranches
        branchMap[newBranchNum]['Right Branches'] = rightBranches
    
    #Update branch locations to branch num instead of first object
    numIdx = 0
    for locIdx, branchLocations in enumerate(branchMap[origBrnchNum]['Branch Locations']):
        for brnchIdx, branch in enumerate(branchLocations):
            branchMap[origBrnchNum]['Branch Locations'][locIdx][brnchIdx] = newBranchNums[numIdx]
            
            numIdx += 1
    
    #Return dictionary of branches
    return branchMap

def UpdateTaskPointerBranches(branchMap, classCompMap, fbName):
    '''
    Determines which branches are the main task pointer branches. Some transitions outside 
    of the main task pointer transitions may also be referencing task pointer parameter. These
    need to have "Task Pointer" remove from type. Also task pointer type is only applicable in phase
    Run command or EM commands that are not hold. Updates map in-place.
    '''
    IsTaskPointerBranch = lambda branchNum: 'Task Pointer' in branchMap[branchNum][TYPE]
    BranchType = lambda branchNum: branchMap[branchNum][TYPE]
    BranchYPos = lambda branchNum: branchMap[branchNum][YPOS]
    
    branchNumbers = BranchNumbers(branchMap)
    
    tpBranches = list(filter(IsTaskPointerBranch, branchNumbers))
    
    #Exit if no task pointer branches
    if not tpBranches:
        return branchMap
    
    #Pull command name and class type
    if fbName in list(classCompMap.keys()):
        cmdName = classCompMap[fbName]['Command']
        classType = classCompMap[fbName][TYPE]
    else:
        cmdName = fbName
        classType = 'None'
    
    #Removes task pointer types if not applicable
    if (classType == EM_CLASS and (cmdName == HOLD) or
        classType == PHASE_CLASS and (cmdName == HOLD or cmdName == RESTART or cmdName == ABORT or cmdName == STOP)):
        for tpBranch in tpBranches:
            branchMap[tpBranch][TYPE] = BranchType(tpBranch).replace(' Task Pointer', '')
    
    #Create a dictionary for counting task pointer branches with the same y position
    tpYPositions = set(map(BranchYPos, tpBranches))
    tpYPosCounts = dict.fromkeys(tpYPositions, 0)
    
    for tpBranch in tpBranches:
        tpYPosCounts[BranchYPos(tpBranch)] += 1
    
    #Determine the y position with highest count, then remove from dictionary
    tpYPosHighestCount = max(tpYPosCounts, key = lambda yPos: tpYPosCounts[yPos])
    del tpYPosCounts[tpYPosHighestCount]
    
    #Remove task pointer type from all other branches that do not have highest y position count
    for tpBranch in tpBranches:
        if BranchYPos(tpBranch) in list(tpYPosCounts.keys()):
            branchMap[tpBranch][TYPE] = BranchType(tpBranch).replace(' Task Pointer', '')

def MoveBranchesWithinParallel(branchMap):
    '''
    Finds branches incompassed by parallel branches and shifts them to other side of 
    previous branch. Updates dictionary in-place.
    '''
    BranchType = lambda branchNum: branchMap[branchNum][TYPE]
    IsParallelBranch = lambda brnchNum: 'Parallel' in BranchType(brnchNum)
    PreviousBranch = lambda brnchNum: branchMap[brnchNum][PREV_BRANCH]
    BranchLocations = lambda brnchNum: branchMap[brnchNum]['Branch Locations']
    BranchXPos = lambda brnchNum: branchMap[brnchNum][XPOS]
    
    branchNumbers = BranchNumbers(branchMap)
    parallelBranches = list(filter(IsParallelBranch, branchNumbers))
    
    for parallelBranch in parallelBranches:
        parallelBrnchType = BranchType(parallelBranch)
        prevBranch = PreviousBranch(parallelBranch)
        
        startIdx = [idx for idx, branches in enumerate(branchMap[prevBranch]['Branch Locations']) if parallelBranch in branches][0] + 1
        endIdx = [idx for idx, object in enumerate(branchMap[prevBranch][OBJS]) if object == branchMap[parallelBranch]['End Step']]
        
        if not endIdx:
            continue
        
        endIdx = endIdx[0]
        
        branchesBetween = BranchLocations(prevBranch)[startIdx:endIdx]
        
        branchesBetween = [num for branches in branchesBetween for num in branches if num]
        
        if not branchesBetween:
            continue
        
        for idx, branchBetween in enumerate(branchesBetween):
            betweenBrnchType = BranchType(branchBetween)
            
            if ('Left' in betweenBrnchType and 'Left' not in parallelBrnchType or
                'Right' in betweenBrnchType and 'Right' not in parallelBrnchType):
                continue
            
            if 'Left' in betweenBrnchType:
                IsAccrossBranch = lambda num: ('Right' in BranchType(num) and 
                                               BranchYPos(num) == BranchYPos(branchBetween))
                branchesAcross = list(filter(IsAccrossBranch, branchesBetween))
                
                if branchesAcross:
                    xPos = max(map(BranchXPos, branchesAcross)) + BRANCH_DIST    
                    
                    for branchAcross in branchesAcross:
                        branchMap[branchAcross]['Right Branches'].append(branchBetween)
                
                else:
                    xPos = BranchXPos(prevBranch) + BRANCH_DIST + ('Trunk' in BranchType(prevBranch)) * STEP_TRAN_X_DIFF
                
                branchMap[branchBetween][XPOS] = xPos
                branchMap[branchBetween][TYPE] = 'Right' + betweenBrnchType[4:]
                branchMap[branchBetween]['Left Branches'] = branchesAcross
                branchMap[branchBetween]['Right Branches'] = []
                
                continue
                
            if 'Right' in betweenBrnchType:
                IsAccrossBranch = lambda num: ('Left' in BranchType(num) and 
                                               BranchYPos(num) == BranchYPos(branchBetween))
                branchesAcross = list(filter(IsAccrossBranch, branchesBetween))
                
                if branchesAcross:
                    xPos = min(map(BranchXPos, branchesAcross)) - BRANCH_DIST
                    
                    for branchAcross in branchesAcross:
                        branchMap[branchAcross]['Left Branches'].append(branchBetween)
                else:
                    xPos = BranchXPos(prevBranch) - BRANCH_DIST + ('Trunk' in BranchType(prevBranch)) * STEP_TRAN_X_DIFF
                
                branchMap[branchBetween][XPOS] = xPos
                branchMap[branchBetween][TYPE] = 'Left' + betweenBrnchType[5:]
                branchMap[branchBetween]['Left Branches'] = []
                branchMap[branchBetween]['Right Branches'] = branchesAcross
                
                continue

def ShiftBranchesLongParallel(branchMap):
    '''
    Shifts branches if parallel branch is longer than previous branch's section.
    '''
    BranchType = lambda brnchNum: branchMap[brnchNum][TYPE]
    IsParaPrevBranch = lambda brnchNum: 'Parallel' in BranchType(brnchNum) and 'Previous' in BranchType(brnchNum)
    PreviousBranch = lambda brnchNum: branchMap[brnchNum][PREV_BRANCH]
    BranchEndStep = lambda brnchNum: branchMap[brnchNum]['End Step']
    BranchObjects = lambda brnchNum: branchMap[brnchNum][OBJS]
    BranchYPos = lambda brnchNum: branchMap[brnchNum][YPOS]
    ObjectDistances = lambda brnchNum: branchMap[brnchNum]['Object Distances']
    BranchLocations = lambda brnchNum: branchMap[brnchNum]['Branch Locations']
    
    branchNumbers = BranchNumbers(branchMap)
    paraBranches = list(filter(IsParaPrevBranch, branchNumbers))
    
    for branch in paraBranches:
        prevBranch = PreviousBranch(branch)
        endStep = BranchEndStep(branch)
        endStepIdx = BranchObjects(prevBranch).index(endStep)
        
        lastTranYPos = BranchYPos(branch) + sum(ObjectDistances(branch))
        endStepYPos = BranchYPos(prevBranch) + sum(ObjectDistances(prevBranch)[:endStepIdx])
        
        estimEndStepYPos = lastTranYPos + TRAN_STEP_VERT_DIST
        
        #Check end stop vertical position, skip if shifting is not needed
        if endStepYPos >= estimEndStepYPos:
            continue
        
        shiftDistance = estimEndStepYPos - endStepYPos
        
        branchMap[prevBranch]['Object Distances'][endStepIdx - 1] += shiftDistance
        
        branchesBelow = BranchLocations(prevBranch)[endStepIdx - 1:]
        branchesBelow = [branch for listOfBranchBelow in branchesBelow for branch in listOfBranchBelow]
        
        for branchBelow in branchesBelow:
            ShiftBranch(branchMap, branchBelow, 'Down', shiftDistance)

def ShiftBranchesPreventCollisions(branchMap):
    '''
    Shifts branches both horizontially and vertically to prevent collisions. Updates map in-place.
    '''
    BranchType = lambda branchNum: branchMap[branchNum][TYPE]
    BranchXPos = lambda brnchNum: branchMap[brnchNum][XPOS]
    BranchYPos = lambda brnchNum: branchMap[brnchNum][YPOS]
    StemmingBranches = lambda brnchNum: branchMap[brnchNum][BRANCHES]
    PreviousBranch = lambda brnchNum: branchMap[brnchNum][PREV_BRANCH]
    IsTaskPointerBranch = lambda branchNum: 'Task Pointer' in branchMap[branchNum][TYPE]
    IsLeftBranch = lambda branchNum: 'Left' in BranchType(branchNum)
    IsRightBranch = lambda branchNum: 'Right' in BranchType(branchNum)
    IsLeftTPBranch = lambda branchNum: IsLeftBranch(branchNum) and IsTaskPointerBranch(branchNum)
    IsRightTPBranch = lambda branchNum: IsRightBranch(branchNum) and IsTaskPointerBranch(branchNum)
    
    branchNumbers = BranchNumbers(branchMap)
    
    #Building list of branches excluding trunk, sorted by x position
    branches = BranchNumbers(branchMap)[1:]
    
    #Save task point y position
    tpBranches = list(filter(IsTaskPointerBranch, branches))
    
    if tpBranches:
        yPosTP = min(map(BranchYPos, tpBranches))
    else:
        yPosTP = 0
    
    #Check for horizontial collisions
    while branches:
        branch = branches.pop(0)
        
        origBrnchType = BranchType(branch)
        xPos = BranchXPos(branch)
        
        #Iterate through previous branches until collision is found
        while True:
            prevBranch = branchMap[branch][PREV_BRANCH]
            prevBrnchType = BranchType(prevBranch)
            
            #If collision found, shift if requested distance if not already shifted
            if ('Left' in origBrnchType and 
                'Right' in prevBrnchType):
                distance = BranchXPos(prevBranch) - xPos - branchMap[prevBranch]['Right Shift Distance']
                
                if distance <= 0:
                    break
                    
                branchMap[prevBranch]['Right Shift Distance'] += distance
                
                branchesToShift = [prevBranch] + branchMap[prevBranch]['Right Branches']
                
                for branchToShift in branchesToShift:
                    ShiftBranch(branchMap, branchToShift, 'Right', distance)
                
                break
            
            #If collision found, shift if requested distance if not already shifted
            if ('Left' in origBrnchType and 
                branchMap[prevBranch]['Left Branches']):
                distance = BranchXPos(prevBranch) - xPos - branchMap[prevBranch]['Right Shift Distance']
                
                if distance <= 0:
                    break
                
                branchMap[prevBranch]['Right Shift Distance'] += distance
                
                excludedBranches = branchMap[prevBranch]['Left Branches']
                
                while 'Trunk' not in BranchType(prevBranch):
                    branch = prevBranch
                    
                    prevBranch = PreviousBranch(branch)
                    
                ShiftBranch(branchMap, prevBranch, 'Right', distance, excludedBranches)
                
                break
            
            #If collision found, shift requested distance if not already shifted
            if ('Right' in origBrnchType and 
                'Left' in prevBrnchType):
                distance = xPos - BranchXPos(prevBranch) - branchMap[prevBranch]['Left Shift Distance']
                
                if distance <= 0:
                    break
                    
                branchMap[prevBranch]['Left Shift Distance'] += distance
                
                branchesToShift = [prevBranch] + branchMap[prevBranch]['Left Branches']
                
                for branchToShift in branchesToShift:
                    ShiftBranch(branchMap, branchToShift, 'Left', distance)
                
                break
            
            #If collision found, shift if requested distance if not already shifted
            if ('Right' in origBrnchType and 
                branchMap[prevBranch]['Right Branches']):
                distance = xPos - BranchXPos(prevBranch) - branchMap[prevBranch]['Left Shift Distance']
                
                if distance <= 0:
                    break
                
                branchMap[prevBranch]['Left Shift Distance'] += distance
                
                excludedBranches = branchMap[prevBranch]['Right Branches']
                
                while 'Trunk' not in BranchType(prevBranch):
                    branch = prevBranch
                    
                    prevBranch = PreviousBranch(branch)
                    
                ShiftBranch(branchMap, prevBranch, 'Left', distance, excludedBranches)
                
                break
            
            #If collision found, shift requested distance if not already shifted
            if ('Trunk' in prevBrnchType and 
                BranchYPos(branch) > yPosTP):
                
                if 'Left' in origBrnchType:
                    branchesToShift = list(filter(IsLeftTPBranch, branchNumbers))
                    
                    distance = BranchXPos(prevBranch) - xPos - branchMap[prevBranch]['Right Shift Distance']
                    
                    if distance <= 0:
                        break
                    
                    branchMap[prevBranch]['Right Shift Distance'] += distance
                    
                    excludedBranches = list(filter(IsLeftTPBranch, StemmingBranches(prevBranch)))
                    
                    ShiftBranch(branchMap, prevBranch, 'Right', distance, excludedBranches)
                    
                    break
                
                if 'Right' in origBrnchType:
                    branchesToShift = list(filter(IsRightTPBranch, branchNumbers))
                    
                    distance = xPos - BranchXPos(prevBranch) - branchMap[prevBranch]['Left Shift Distance']
                    
                    if distance <= 0:
                        break
                    
                    branchMap[prevBranch]['Left Shift Distance'] += distance
                    
                    excludedBranches = list(filter(IsRightTPBranch, StemmingBranches(prevBranch)))
                    
                    ShiftBranch(branchMap, prevBranch, 'Left', distance, excludedBranches)
                    
                    break
            
            branch = prevBranch
            
            #Exit if trunk
            if branch == 1:
                break
    
    #Check for vertical collisions
    for currentBranch in branchNumbers:
        branches = StemmingBranches(currentBranch)
        
        for branch in branches:
            if 'Right' in BranchType(branch):
                IsBranchAbove = lambda num: (IsRightBranch(num) and
                                             BranchXPos(num) <= BranchXPos(branch) and
                                             BranchYPos(num) < BranchYPos(branch))
                
            else:
                IsBranchAbove = lambda num: (IsLeftBranch(num) and
                                             BranchXPos(num) >= BranchXPos(branch) and
                                             BranchYPos(num) < BranchYPos(branch))
            
            branchesAbove = list(filter(IsBranchAbove, branches))
            
            if not branchesAbove:
                continue
            
            branchAbove = sorted(branchesAbove, key = BranchYPos)[-1]
            
            branchY = BranchYPos(branch)
            aboveY, aboveLen = BranchYPos(branchAbove), branchMap[branchAbove]['Length']
            
            if aboveY + aboveLen >= branchY:
                shiftDistance = (aboveY + aboveLen - branchY) + (STEP_TRAN_VERT_DIST + TRAN_STEP_VERT_DIST + 10)
                
                objectIdx = [idx for idx, branchLocation in enumerate(branchMap[currentBranch]['Branch Locations']) if branchAbove in branchLocation][0]
                
                branchMap[currentBranch]['Object Distances'][objectIdx + 1] += shiftDistance
                
                branchesBelow = branchMap[currentBranch]['Branch Locations'][objectIdx + 1:]
                
                branchesBelow = [branch for listOfBranchBelow in branchesBelow for branch in listOfBranchBelow]
                
                for branchBelow in branchesBelow:
                    ShiftBranch(branchMap, branchBelow, 'Down', shiftDistance)

def ShiftBranch(branchMap, number, direction, distance, excludedBranches=None):
    '''
    Shifts branch and all child branches (unless some are excluded) in specified direction. Updates map in-place.
    '''
    excludedBranches = excludedBranches or []
    
    branches = FindBranches(branchMap, number, [number], excludedBranches)
    
    for branch in branches:
        if direction == 'Left':
            branchMap[branch][XPOS] -= distance
        if direction == 'Right':
            branchMap[branch][XPOS] += distance
        if direction == 'Down':
            branchMap[branch][YPOS] += distance

def FindBranches(branchMap, branchNum, branches=None, excludedBranches=None):
    '''
    Returns all child branches (unless some are excluded).
    '''
    StemmingBranches = lambda brnchNum: branchMap[brnchNum][BRANCHES]
    IsNewBranch = lambda brnchNum: brnchNum not in excludedBranches and brnchNum not in branches
    
    branches = branches or []
    excludedBranches = excludedBranches or []
    
    newBranches = list(filter(IsNewBranch, StemmingBranches(branchNum)))
    branches += newBranches
    
    for branch in newBranches:
        branches = FindBranches(branchMap, branch, branches, excludedBranches)
    
    return branches

def ResetBranchNum():
    '''
    Resets global variable.
    '''
    branchNum = 1

def FindFarthestObject(branchMap, branches, direction, objMap=None):
    '''
    Returns farthest step/transition x or y position based on direction.
    '''
    #Find all branches branching from branches
    BranchLastObj = lambda branchNum: branchMap[branchNum][OBJS][-1]
    ObjectYPos = lambda obj: objMap[obj][YPOS]
    
    for branch in branches:
        branches = branches + FindBranches(branchMap, branch)
    
    #Return x position
    if (direction == 'Left' or 
        direction == 'Right'):
        xPositions = []
        
        for branch in branches:
            xPositions.append(branchMap[branch][XPOS])
        
        return min(xPositions) if direction == 'Left' else max(xPositions)
    
    #Return y position
    if (direction == 'Up' or 
        direction == 'Down'):
        yPositions = []
        
        for branch in branches:
            yPositions.append(ObjectYPos(BranchLastObj(branch)))
        
        return min(yPositions) if direction == 'Up' else max(yPositions)

BranchNumbers = lambda branchMap: sorted(branchMap.keys())

'''
These functions update step and transition data.
'''
def UpdateStepTranPositions(objMap, branch):
    '''
    Updates position and size (if step) to steps and transitions in object map. Updates map in-place.
    '''
    ObjectIsStep = lambda obj: objMap[obj][TYPE] == STEP
    
    xPos = branch[XPOS]
    yPos = branch[YPOS]
    
    #Update position for each object in branch
    for idx, obj in enumerate(branch[OBJS]):
        objMap[obj][XPOS] = xPos
        objMap[obj][YPOS] = yPos
        
        #Update size if step
        if ObjectIsStep(obj):
            objMap[obj][HEIGHT] = STEP_SIZE[HEIGHT]
            objMap[obj][WIDTH] = STEP_SIZE[WIDTH]
            
        #Determine x position of next object by checking type of current object
        if ObjectIsStep(obj):
            xPos += STEP_TRAN_X_DIFF
        else:
            xPos -= STEP_TRAN_X_DIFF
        
        #Determine y position of next object
        if idx != len(branch[OBJS]) - 1:
            yPos += branch['Object Distances'][idx]

def UpdateStepTranSegments(objMap, branchMap):
    '''
    Addes segment orientation data to transitions in object map. Updates map in-place.
    '''
    ObjectType = lambda obj: objMap[obj][TYPE]
    ObjectXPos = lambda obj: objMap[obj][XPOS]
    ObjectYPos = lambda obj: objMap[obj][YPOS]
    IsStep = lambda obj: ObjectType(obj) == STEP
    BranchType = lambda branchNum: branchMap[branchNum][TYPE]
    IsLoopBackBrnch = lambda branchNum: 'Loop Back' in BranchType(branchNum)
    BranchLastObj = lambda branchNum: branchMap[branchNum][OBJS][-1]
    LeftBranches = lambda branchNum: branchMap[branchNum]['Left Branches']
    RightBranches = lambda branchNum: branchMap[branchNum]['Right Branches']
    StemmingBranches = lambda brnchNum: branchMap[brnchNum][BRANCHES]
    IsLeftBranch = lambda brnchNum:'Left' in BranchType(brnchNum)
    IsRightBranch = lambda brnchNum:'Right' in BranchType(brnchNum)
    IsTaskPointerBranch = lambda brnchNum: 'Task Pointer' in BranchType(brnchNum)
    IsTrunk = lambda brnchNum: 'Trunk' in BranchType(brnchNum)
    
    objNames = ObjectNames(objMap)
    branchNumbers = BranchNumbers(branchMap)
    
    maxYPos = max(map(ObjectYPos, objNames))
    
    loopbackBranches = list(filter(IsLoopBackBrnch, branchNumbers))
    
    #Determine which branches are loop back, and add segment orientation data to object map
    for branch in loopbackBranches:
        transition = BranchLastObj(branch)
        
        if IsStep(transition):
            continue
        
        branchType = BranchType(branch)
        leftBranches = LeftBranches(branch)
        rightBranches = RightBranches(branch)
        branchesStemLeft = list(filter(IsLeftBranch, StemmingBranches(branch)))
        branchesStemRight = list(filter(IsRightBranch, StemmingBranches(branch)))
        nextStep = branchMap[branch]['End Step']
        
        tranXPos, tranYPos = ObjectXPos(transition), ObjectYPos(transition)
        stepXPos, stepYPos = ObjectXPos(nextStep), ObjectYPos(nextStep)
        
        #Determine segment horizontial and vertical orientations
        if (IsTaskPointerBranch(branch) or IsTrunk(branch)):
            vert1Orien = maxYPos + SEGMENT_DIST_BELOW_TRAN * 2
            horizOrien = SEGMENT_TP_X_DIST
            vert2Orien = stepYPos - SEGMENT_DIST_ABOVE_STEP
            
        elif 'Current Branch' in branchType:
            vert1Orien = tranYPos + SEGMENT_DIST_BELOW_TRAN
            vert2Orien = stepYPos - SEGMENT_DIST_ABOVE_STEP
            
            if (not branchesStemLeft and
                not branchesStemRight):
                if IsRightBranch(branch):
                    horizOrien = tranXPos + SEGMENT_DIST_RIGHT_OF_TRAN
                else:
                    horizOrien = tranXPos - SEGMENT_DIST_LEFT_OF_TRAN
            
            elif (branchesStemLeft and
                not branchesStemRight):
                horizOrien = tranXPos + SEGMENT_DIST_RIGHT_OF_TRAN
            
            elif (not branchesStemLeft and
                  branchesStemRight):
                horizOrien = tranXPos - SEGMENT_DIST_LEFT_OF_TRAN
            
            elif IsRightBranch(branch):
                farthestRightObj = FindFarthestObject(branchMap, branchesStemRight, 'Right')
                
                horizOrien = farthestRightObj + SEGMENT_SPACING
            
            else:
                farthestLeftObj = FindFarthestObject(branchMap, branchesStemLeft, 'Left')
                
                horizOrien = farthestLeftObj - SEGMENT_SPACING
            
        elif 'Previous Branch' in branchType:
            vert1Orien = tranYPos + SEGMENT_DIST_BELOW_TRAN
            vert2Orien = stepYPos - SEGMENT_DIST_ABOVE_STEP
            
            if IsLeftBranch(branch):
                if (not leftBranches and
                    not branchesStemLeft):
                    horizOrien = tranXPos - SEGMENT_DIST_LEFT_OF_TRAN
                elif not leftBranches:
                    leftmostObjXPos = FindFarthestObject(branchMap, branchesStemLeft, 'Left')
                    
                    horizOrien = leftmostObjXPos - SEGMENT_DIST_LEFT_OF_TRAN - SEGMENT_SPACING
                else:
                    leftmostObjXPos = FindFarthestObject(branchMap, leftBranches, 'Left')
                    horizOrien = leftmostObjXPos - SEGMENT_DIST_LEFT_OF_TRAN - SEGMENT_SPACING * len(leftBranches)
                    
                    lowestObjYPos = FindFarthestObject(branchMap, leftBranches, 'Down', objMap)
                    
                    if tranYPos <= lowestObjYPos:
                        vert1Orien = lowestObjYPos + SEGMENT_DIST_BELOW_TRAN + SEGMENT_SPACING * len(leftBranches)
            
            else:
                if (not rightBranches and
                    not branchesStemRight):
                    horizOrien = tranXPos + SEGMENT_DIST_RIGHT_OF_TRAN
                elif not rightBranches:
                    rightmostObjXPos = FindFarthestObject(branchMap, branchesStemRight, 'Right')
                    
                    horizOrien = rightmostObjXPos + SEGMENT_DIST_RIGHT_OF_TRAN + SEGMENT_SPACING
                else:
                    rightmostObjXPos = FindFarthestObject(branchMap, rightBranches, 'Right')
                    horizOrien = rightmostObjXPos + SEGMENT_DIST_RIGHT_OF_TRAN + SEGMENT_SPACING * len(rightBranches)
                    
                    lowestObjYPos = FindFarthestObject(branchMap, rightBranches, 'Down', objMap)
                    
                    if tranYPos <= lowestObjYPos:
                        vert1Orien = lowestObjYPos + SEGMENT_DIST_BELOW_TRAN + SEGMENT_SPACING * len(rightBranches)
            
        else:
            vert1Orien = tranYPos + SEGMENT_DIST_BELOW_TRAN
            vert2Orien = stepYPos - SEGMENT_DIST_ABOVE_STEP
            
            if IsRightBranch(branch):
                horizOrien = tranXPos + SEGMENT_DIST_RIGHT_OF_TRAN
            else:
                horizOrien = tranXPos - SEGMENT_DIST_LEFT_OF_TRAN
        
        #Update object with orientations
        objMap[transition]['Segment Orientations'] = [vert1Orien, 
                                                      horizOrien, 
                                                      vert2Orien]

'''
These functions rename items.
'''
def BuildNewStepTranNames(branchMap, classCompMap, fbName, objMap):
    '''
    Builds new step and transition names and stores in a dictionary.
    '''
    ObjectXPos = lambda obj: objMap[obj][XPOS]
    ObjectYPos = lambda obj: objMap[obj][YPOS]
    PrevObjects = lambda obj: objMap[obj]['Previous Objects']
    PrevObject = lambda obj: PrevObjects(obj)[0]
    NextObject = lambda obj: objMap[obj][NEXT_OBJS][0]
    
    #Pull command name and class type
    if fbName in FunctionBlocks(classCompMap):
        cmdName = classCompMap[fbName]['Command']
        classType = classCompMap[fbName][TYPE]
    else:
        cmdName = fbName
        classType = 'None'
    
    #Determine starting letter
    if classType == EM_CLASS:
        if cmdName == HOLD:
            stepInitLetter = 'H'
        else:
            stepInitLetter = 'S'
    
    elif classType == PHASE_CLASS:
        if cmdName == 'RUN':
            stepInitLetter = 'S'
        elif cmdName == 'RESTART':
            stepInitLetter = 'R'
        elif cmdName == 'ABORT':
            stepInitLetter = 'A'
        elif cmdName == 'STOP':
            stepInitLetter = 'S'
        elif cmdName == 'HOLD':
            stepInitLetter = 'H'
        else:
            stepInitLetter = 'S'
    
    else:
        stepInitLetter = 'S'
    
    #Calls function to build names for all steps and transitions, starting with trunk
    newObjNames, objNum, termCount = BuildObjNamesOfBranch(branchMap, objMap, 1, stepInitLetter)
    
    
    IsTerm = lambda obj: TERM_NAME in newObjNames[obj]
    NewObjName = lambda obj: newObjNames[obj]
    NewObjLastNum = lambda obj: int(NewObjName(obj)[-1])
    IsParalTran = lambda obj: newObjNames[obj] == 'Parallel Transition'
    
    objNames = ObjectNames(newObjNames)
    
    #Update last step and preceeding transition name if phase class
    if classType == PHASE_CLASS:
        termNames = list(filter(IsTerm, objNames))
        finalTerm = sorted(termNames, reverse = True, key = NewObjLastNum)[0]
        
        lastStep = PrevObject(finalTerm)
        
        #Skip if entire sfc is only one step and one termination
        if PrevObjects(lastStep):
            secToLastTran = PrevObject(lastStep)
            
            newObjNames[lastStep] = stepInitLetter + str(LAST_STEP_NUM)
            newObjNames[secToLastTran] = TRAN_INIT_CHAR + str(LAST_STEP_NUM)
    
    #If only one termination, then update termination name to remove end number
    if termCount == 1:
        for name in objNames:
            if newObjNames[name] == ''.join([TERM_NAME, '1']):
                newObjNames[name] = TERM_NAME
    
    #Updates transitions connecting to end step of loop back branch
    newNames = [newObjNames[name] for name in objNames]
    
    HasDuplicNewNames = lambda obj: newNames.count(newObjNames[obj]) > 1
    loopBackTranToUpdate = [name for name in objNames if HasDuplicNewNames(name) and not IsParalTran(name)]
    
    dupNames = {}
    
    DuplicNewNames = lambda dupNames: list(dupNames.keys())
    
    for name in loopBackTranToUpdate:
        newName = newObjNames[name]
        
        if newName in DuplicNewNames(dupNames):
            dupNames[newName].append(name)
        else:
            dupNames[newName] = [name]
    
    for newName in DuplicNewNames(dupNames):
        existNames = dupNames[newName]
        existNames = sorted(existNames, key = ObjectYPos)
        endChar = 'A'
        newObjNames[existNames.pop(0)] = newName + endChar
        
        existNames = sorted(existNames, key = ObjectXPos)
        
        for existName in existNames:
            endChar = chr(ord(endChar) + 1)
            newObjNames[existName] = newName + endChar
    
    #Updates transitions connecting to end step of parallel branch
    stepsParaBranConn = set(NextObject(name) for name in objNames if IsParalTran(name))
    
    for step in stepsParaBranConn:
        transitions = sorted(PrevObjects(step), key = ObjectXPos)
        stepNum = newObjNames[step][-1 * OBJ_NAME_NUM_OF_NUMER_CHAR:]
        endChar = 'A'
        
        for tran in transitions:
            newObjNames[tran] = TRAN_INIT_CHAR + stepNum + endChar
            endChar = chr(ord(endChar) + 1)
    
    #Remove any step and transition that do not need to be updated
    for name in list(newObjNames.keys()):
        if name == newObjNames[name]:
            del newObjNames[name]
    
    return newObjNames

def BuildObjNamesOfBranch(branchMap, objMap, branchNum, stepInitLetter, objNum=None, newObjNames=None, termCount=0):
    '''
    This recursive function builds object names for a single branch. Then calls this function for all branches stemming from branch.
    '''
    BranchType = lambda branchNum: branchMap[branchNum][TYPE]
    ObjectType = lambda obj: objMap[obj][TYPE]
    IsTran = lambda obj: ObjectType(obj) == TRANSITION
    
    objNum = objNum or INIT_STEP_NUM
    newObjNames = newObjNames or {}
    
    objects = branchMap[branchNum][OBJS]
    branchLocations = branchMap[branchNum]['Branch Locations']
    tranAboveParaConnect = {}
    tpBranches = []
    tpIdx = -1
    
    for idx, obj in enumerate(objects):
        #Call parallel branches if reached transition above branch connection
        if obj in list(tranAboveParaConnect.keys()):
            branches = tranAboveParaConnect[obj]
            
            for branch in branches:
                newObjNames, objNum, termCount = BuildObjNamesOfBranch(branchMap, objMap, branch, stepInitLetter, objNum, newObjNames, termCount)
        
        #Determine first character and increment number if transition (but not last)
        if IsTran(obj):
            initChar = TRAN_INIT_CHAR
            
            if obj != objects[-1]:
                objNum += OBJ_NAME_INCREM
            
        else:
            if (obj == objects[0] and
                branchNum != 1):
                objNum += OBJ_NAME_INCREM
            
            initChar = stepInitLetter
        
        #Build new object name
        if obj == objects[-1] and IsTran(obj):
            branchType = BranchType(branchNum)
            
            #If last transition and loop back, build transition name based on end step
            if 'Loop Back' in branchType:
                newObjName = initChar + ''.join(filter(str.isdigit, newObjNames[branchMap[branchNum]['End Step']]))
            #If last transition and parallel, transition name will be built later
            elif 'Parallel' in branchType:
                newObjName = 'Parallel Transition'
            #If termination, then build name
            else:
                termCount += 1
                
                newObjName = TERM_NAME + str(termCount)
        else:
            newObjNums = OBJ_NAME_NUM_OF_NUMER_CHAR * '0' + str(objNum)
            newObjNums = newObjNums[-1 * OBJ_NAME_NUM_OF_NUMER_CHAR:]
            newObjName = initChar + newObjNums
        
        #Update new object name in dictionary dictionary
        newObjNames[obj] = newObjName
        
        #Check for non-task pointer loop back branches
        if idx + 1 < len(objects):
            for branch in branchLocations[idx]:
                branchType = BranchType(branch)
                
                #Build branch if loop back or termination branch
                if ('Task Pointer' not in branchType and
                    ('Loop Back' in branchType or
                    ('Loop Back' not in branchType and 'Parallel' not in branchType))):
                    newObjNames, objNum, termCount = BuildObjNamesOfBranch(branchMap, objMap, branch, stepInitLetter, objNum, newObjNames, termCount)
                
                #Check if branch is a non-task pointer parallel
                if ('Task Pointer' not in branchType and
                    'Parallel' in branchType):
                    #Build branch if left branch where first object is a transition
                    if ('Left' in branchType and
                        'Transition' in branchType):
                        newObjNames, objNum, termCount = BuildObjNamesOfBranch(branchMap, objMap, branch, stepInitLetter, objNum, newObjNames, termCount)
                    #Save branch if right branch
                    else:
                        endStep = branchMap[branch]['End Step']
                        objAbove = objects[objects.index(endStep) - 1]
                        
                        if objMap[objAbove][TYPE] == STEP:
                            endTran = objects[objects.index(objAbove) + 1]
                        else:
                            endTran = objAbove
                        
                        if endTran in list(tranAboveParaConnect.keys()):
                            tranAboveParaConnect[endTran].append(branch)
                        else:
                            tranAboveParaConnect[endTran] = [branch]
                
                #Save task pointer branch index in branch locations
                if 'Task Pointer' in branchType:
                    tpBranches.append(branch)
    
    #Build object names for task pointer branches
    if tpBranches:
        for branch in tpBranches:
            newObjNames, objNum, termCount = BuildObjNamesOfBranch(branchMap, objMap, branch, stepInitLetter, objNum, newObjNames, termCount)
    
    return newObjNames, objNum, termCount

def BuildNewActionNames(actionMap):
    '''
    Builds new action names and stores in a dictionary.
    '''
    StepsActions = lambda actionMap: list(actionMap.keys())
    Steps = lambda actionsInSteps: list(actionsInSteps.keys())
    
    newActionNames = {}
    actionsInSteps = {}
    
    #Build a dictionary containing actions within each step, to iterate through in next section
    for stepAction in StepsActions(actionMap):
        step = stepAction[:stepAction.index('/')]
        action = stepAction[stepAction.index('/') + 1:]
        
        if step in Steps(actionsInSteps):
            actionsInSteps[step].append(action)
        else:
            actionsInSteps[step] = [action]
    
    #Iterate through all actions and add to action name dictionary if names differ 
    for step in Steps(actionsInSteps):
        ActionLineNum = lambda action: actionMap['/'.join([step, action])]['Line Number']
        actions = sorted(actionsInSteps[step], key = ActionLineNum)
        
        actionNum = ACTION_INIT_NUM
        for action in actions:
            stepAction = '/'.join([step, action])
            
            if actionMap[stepAction]['Qualifier'] == 'N':
                initChar = ACTION_NS_INIT_CHAR
            else:
                initChar = ACTION_INIT_CHAR
            
            newNum = str(actionNum)
            
            if len(newNum) < ACTION_NUM_OF_NUMER_CHAR:
                newNum = (ACTION_NUM_OF_NUMER_CHAR - len(newNum)) * '0' + newNum
            
            newName = initChar + newNum
            
            if newName != action:
                newActionNames[stepAction] = newName
            
            actionNum += ACTION_NUM_INCREM
    
    return newActionNames

'''
These functions update fhx lines.
'''
def IncrementTime(fhxLines, index):
    '''
    Increments time by 1 of component in fhx lines. Index is the first line of the item. 
    Updates fhx lines in-place.
    '''
    timeID = ' time='
    
    timeIdx = index + 1
    
    #Line containing time data
    line = fhxLines[timeIdx]
    
    #Set new time to original time plus one
    time = int(FindString(line, timeID, '/*')) + 1
    
    #Update line with new time
    fhxLines[timeIdx] = ''.join([line[:line.index(timeID) + len(timeID)], str(time), line[line.index('/*'):]])

def UpdateLines(fhxLines, objMap):
    '''
    Updates fhx lines based on object map. Updates lines in-place.
    '''
    rectID = 'RECTANGLE= {'
    posID = 'POSITION= {'
    xID, yID, hID, wID = ' X=', ' Y=', ' H=', ' W='
    endID = ' }'
    
    segmentStartID = ' {'
    segmentIdxID = ' SEGMENT { INDEX='
    orienHorizID, orienVertID = ' ORIENTATION=HORIZONTAL', ' ORIENTATION=VERTICAL'
    ordinateID = ' ORDINATE='
    
    HasSegmentData = lambda obj: 'Segment Orientations' in list(objMap[obj].keys())
    
    objNames = ObjectNames(objMap)
    
    #Update fhx lines with position and size (if applicable) for objects
    for objName in objNames:
        obj = objMap[objName]
        posLineNum = obj[POS_LINE_NUM]
        
        line = fhxLines[posLineNum]
        
        #Update line for rectangle if step
        if obj[TYPE] == STEP:
            numBeginSpaces = line.index(rectID)
            beginSpaces = numBeginSpaces * ' '
            x, y = str(obj[XPOS]), str(obj[YPOS])
            h, w = str(obj[HEIGHT]), str(obj[WIDTH])
            
            line = ''.join([beginSpaces, rectID, xID, x, yID, y, hID, h, wID, w, endID])
        
        #Update line for position if transition
        else:
            numBeginSpaces = line.index(posID)
            beginSpaces = numBeginSpaces * ' '
            x, y = str(obj[XPOS]), str(obj[YPOS])
            
            line = ''.join([beginSpaces, posID, xID, x, yID, y, endID])    
        
        #Update line in fhxlines
        fhxLines[posLineNum] = line
        
    #Update transition segment data if it exists (thus a loop back)
    for tran in filter(HasSegmentData, objNames):
        segLineNum = objMap[tran]['Segment Line Number']
        ordinates = objMap[tran]['Segment Orientations']
        
        line = fhxLines[segLineNum]
        
        tranStepConnect = line[:line.index(segmentStartID)]
        
        #Updates line with segment orientation data
        line = ''.join([tranStepConnect, segmentStartID, 
                        segmentIdxID, '1', orienHorizID, ordinateID, str(ordinates[0]), endID, 
                        segmentIdxID, '2', orienVertID, ordinateID, str(ordinates[1]), endID, 
                        segmentIdxID, '3', orienHorizID, ordinateID, str(ordinates[2]), endID, 
                        endID])
        
        #Update line in fhxlines
        fhxLines[segLineNum] = line

def UpdateTranExp(fhxLines, objMap):
    '''
    Updates transition expressions of function block based on object map. Updates lines in-place.
    '''
    tranExpID = 'EXPRESSION="'
    pendConfID = 'pending confirm'
    pcEqualZero = "/PENDING_CONFIRMS.CV' = 0"
    pcParameter = "PENDING_CONFIRMS"
    
    ObjectType = lambda obj: objMap[obj][TYPE]
    IsTran = lambda obj: ObjectType(obj) == TRANSITION
    IsStep = lambda obj: ObjectType(obj) == STEP
    ObjectLineNum = lambda obj: objMap[obj]['Line Number']
    
    objNames = ObjectNames(objMap)
    tranExpTooManyPC = []
    transitions = sorted(filter(IsTran, objNames), reverse=True, key = ObjectLineNum)
    steps = list(filter(IsStep, objNames))
    
    for tran in transitions:
        #Build expression lines from existing expression
        existExpLines = ConvertCondExpToList(objMap[tran][TRAN_EXP])
        
        #Update transition description to reference in next section
        tranDesc = objMap[tran]['Description'].strip()
        
        for step in steps:
            tranDesc = tranDesc.replace(step + ' ', '')
        
        tranDesc = tranDesc.lower()
        
        expLines = []
        prevSteps = objMap[tran]['Previous Objects']
        skipWrite = False
        
        #Update expression for pending confirms only
        if (tranDesc == pendConfID or tranDesc[:-1] == pendConfID):
            
            expLines.append(''.join(["'", prevSteps.pop(0), pcEqualZero]))
            
            if prevSteps:
                expLines[0] = AddParentheses(expLines[0])
            
            for idx, prevStep in enumerate(prevSteps):
                expLines[idx] += ' AND'
                
                expLines.append(AddParentheses(''.join(["'", prevStep, pcEqualZero])))
        
        #Update expression if a line contains pending confirms parameter
        else:
            isPendConfList = [(pcParameter in expLine) for expLine in existExpLines]
            inParenCount = 0
            
            #Skip if no line contains pending confirms parameter
            if not any(isPendConfList):
                continue
            
            for existExpLine, isPendConfLine in zip(existExpLines, isPendConfList):
                openParenCount = existExpLine.count('(')
                closeParenCount = existExpLine.count(')')
                
                inParenCount += openParenCount - closeParenCount
                
                if isPendConfLine:
                    if prevSteps:
                        line = ''.join(["'", prevSteps.pop(0), pcEqualZero])
                    else:
                        tranExpTooManyPC.append(tran)
                        skipWrite = True
                    
                    if ((openParenCount or closeParenCount) and
                        len(existExpLines) > 1):
                        line = ''.join(['(' * openParenCount, line, ')' * closeParenCount])
                    elif (len(existExpLines) > 1 and 
                          inParenCount == 0):
                        line = AddParentheses(line)
                else:
                    if (openParenCount or closeParenCount or
                        inParenCount > 0):
                        if ' AND' in existExpLine:
                            line = existExpLine[:-4]
                        elif ' OR' in existExpLine:
                            line = existExpLine[:-3]
                        else:
                            line = existExpLine
                    else:
                        if ' AND' in existExpLine:
                            line = AddParentheses(existExpLine[:-4])
                        elif ' OR' in existExpLine:
                            line = AddParentheses(existExpLine[:-3])
                        else:
                            line = AddParentheses(existExpLine)
                
                if ' AND' in existExpLine:
                    line += ' AND'
                elif ' OR' in existExpLine:
                    line += ' OR'
                
                expLines.append(line)
        
        if skipWrite:
            continue
        
        expLineNum = objMap[tran]['Expression Line Number']
        numOfLines = objMap[tran]['Expression Number of Lines']
        
        #Update expression lines to include transition expression parameter and quotes
        firstLine = fhxLines[expLineNum]
        
        expLines[0] = ''.join([firstLine[:firstLine.index(tranExpID)],tranExpID, expLines[0]])
        expLines[-1] += '"'
        
        #Update fhx lines
        WriteExpLines(fhxLines, expLineNum, numOfLines, expLines) 
    
    #Write error message
    if tranExpTooManyPC:
        print(f'\nThe following transition expression(s) were skipped because of redundant pending confirms:')
        for tran in tranExpTooManyPC:
            print(f'   {tran}')
        print('')

def UpdateDelayExp(fhxLines, actionMap):
    '''
    Updates action delay expressions of function block based on action map. Updates lines in-place.
    '''
    delayID, actionDelayExpID = 'DELAY', 'DELAY_EXPRESSION="'
    waitFor = 'Wait for '
    state = "/STATE.CV'"
    actionStatesComplete = "'$sfc_action_states:Complete'"
    
    DelayLineNum = lambda stepAction: actionMap[stepAction]['Delay Line Number']
    
    stepsActions = list(actionMap.keys())
    stepsActions = sorted(stepsActions, reverse = True, key = DelayLineNum)
    
    for stepAction in stepsActions:
        [step, action] = stepAction.split('/')
        
        #Build expression lines from existing expression
        existDelayLines = ConvertCondExpToList(actionMap[stepAction]['Delay Expression'])
        
        #Update action description to reference in next section
        desc = actionMap[stepAction]['Description'].strip()
        desc = desc.upper()
        
        delayLines = []
        
        #Save action referenced in description
        if (desc.startswith(waitFor.upper()) and ',' in desc):
            actionRef = FindString(desc, waitFor.upper(), endChar = ',')
        else:
            actionRef = ''
        
        #Update expression if description contains "Wait for A###,"
        if (actionRef and actionRef in actionMap[stepAction]['Neighboring Actions']):
            delayLines = [''.join(["'", step, '/', actionRef, state, ' = ', actionStatesComplete])]
        
        #Update expression if a line contains actions states complete named set
        else:
            isActStateList = [(actionStatesComplete in delayLine) for delayLine in existDelayLines]
            inParenCount = 0
            
            #Skip if no line contains pending confirms parameter
            if not any(isActStateList):
                continue
            
            for existDelayLine, isActState in zip(existDelayLines, isActStateList):
                openParenCount = existDelayLine.count('(')
                closeParenCount = existDelayLine.count(')')
                
                inParenCount += openParenCount - closeParenCount
                
                if isActState:
                    actionInExp = FindString(existDelayLine, '/', endChar='/')
                    
                    line = ''.join(["'", step, '/', actionInExp, state, ' = ', actionStatesComplete])
                    
                    if ((openParenCount or closeParenCount) and
                        len(existDelayLines) > 1):
                        line = ''.join(['(' * openParenCount, line, ')' * closeParenCount])
                    elif (len(existDelayLines) > 1 and 
                          inParenCount == 0):
                        line = AddParentheses(line)
                else:
                    if (openParenCount or closeParenCount or
                        inParenCount > 0):
                        if ' AND' in existDelayLine:
                            line = existDelayLine[:-4]
                        elif ' OR' in existDelayLine:
                            line = existDelayLine[:-3]
                        else:
                            line = existDelayLine
                    else:
                        if ' AND' in existDelayLine:
                            line = AddParentheses(existDelayLine[:-4])
                        elif ' OR' in existDelayLine:
                            line = AddParentheses(existDelayLine[:-3])
                        else:
                            line = AddParentheses(existDelayLine)
                
                if ' AND' in existDelayLine:
                    line += ' AND'
                elif ' OR' in existDelayLine:
                    line += ' OR'
                
                delayLines.append(line)
                
        delayLineNum = DelayLineNum(stepAction)
        numOfLines = actionMap[stepAction]['Delay Number of Lines']
        
        #Update delay lines to include delay expression parameter and quotes
        firstLine = fhxLines[delayLineNum]
        
        delayLines[0] = ''.join([firstLine[:firstLine.index(delayID)] + actionDelayExpID, delayLines[0]])
        delayLines[-1] += '"'
        
        #Update fhx lines
        WriteExpLines(fhxLines, delayLineNum, numOfLines, delayLines)

def WriteExpLines(fhxLines, lineNum, numOfLines, expLines):
    '''
    Updates single expression in a function block. 
    Updates fhx lines in-place.
    '''
    fhxLines[lineNum] = expLines[0]
    
    if len(expLines) > 1:
        #Add extra lines if needed
        if numOfLines < len(expLines):
            for i in range(len(expLines) - numOfLines):
                fhxLines.insert(lineNum + 1, '')
        
        #Update expression line by line, not including first step
        for idx, expLine in enumerate(expLines[1:]):
            fhxLines[lineNum + idx + 1] = expLine
    
    #Delete extra lines if needed
    if numOfLines > len(expLines):
        del fhxLines[lineNum + len(expLines):lineNum + numOfLines]

def RenameStepsTransitions(fhxLines, newObjNames, objMap, fbLineNum, fbSize):
    '''
    Updates fhx lines to rename steps and transitions based on new names dictionary. 
    Updates lines in-place.
    '''
    stepTranConnID = '\n    STEP_TRANSITION_CONNECTION'
    initStepID = '    INITIAL_STEP="'
    stepID, tranID = 'STEP="', 'TRANSITION="'
    sfcAlgorEndID = '\n  }'
    
    ObjectType = lambda obj: objMap[obj][TYPE]
    IsStep = lambda obj: ObjectType(obj) == STEP
    
    objNames = list(newObjNames.keys())
    connLineNums = dict.fromkeys(objNames)
    fbLines = '\n'.join(fhxLines[fbLineNum: fbLineNum + fbSize])
    
    #Determine which step-tran/tran-step connection rows will be updated per step/tran
    connIdx = fbLines.index(stepTranConnID) + 1
    sfcEndIdx = connIdx + fbLines[connIdx:].index(sfcAlgorEndID)
    connLineNum = fbLineNum + fbLines[:connIdx].count('\n')
    sfcEndLineNum = connLineNum + fbLines[connIdx: sfcEndIdx].count('\n') + 1
    
    for idx, line in enumerate(fhxLines[connLineNum: sfcEndLineNum]):
        step = FindString(line, stepID)
        tran = FindString(line, tranID)
        
        if step in objNames:
            if connLineNums[step]:
                connLineNums[step].append(connLineNum + idx)
            else:
                connLineNums[step] = [connLineNum + idx]
        if tran in objNames:
            if connLineNums[tran]:
                connLineNums[tran].append(connLineNum + idx)
            else:
                connLineNums[tran] = [connLineNum + idx]
    
    #Update initial step name
    initStepLineNum = fbLineNum + fbLines[:fbLines.index(initStepID)].count('\n')
    initStepLine = fhxLines[initStepLineNum]
    initStep = FindString(initStepLine, '"')
    if initStep in objNames:
        fhxLines[initStepLineNum] = ''.join([initStepID, newObjNames[initStep], '"'])
    
    #Iterate through object names to be updated
    for objName in objNames:
        newObjName = newObjNames[objName]
        
        lineNum = objMap[objName]['Line Number']
        size = objMap[objName]['Size']
        
        #Update step/transition name
        nameLine = fhxLines[lineNum]
        fhxLines[lineNum] = ''.join([nameLine[:nameLine.index('"') + 1], newObjName, '"'])
        
        #Update step-transition and transition-step connection names
        for connLineNum in connLineNums[objName]:
            fhxLines[connLineNum] = fhxLines[connLineNum].replace(f'"{objName}"', f'"{newObjName}"')
        
        #If step, then update action expressions and following transitions
        if IsStep(objName):
            linesString = '\n'.join(fhxLines[lineNum: lineNum + size])
            
            #Update action expressions containing step name (format 'STEP/)
            linesString = linesString.replace(f"'{objName}/", f"'{newObjName}/")
            
            #Update fhx lines with new action expressions
            fhxLines[lineNum: lineNum + size] = linesString.split('\n')
            
            #Update following transitions
            for tran in objMap[objName]['Next Objects']:
                lineNum = objMap[tran]['Line Number']
                size = objMap[tran]['Size']
                linesString = '\n'.join(fhxLines[lineNum: lineNum + size])
                
                #Update transition description
                linesString = ReplaceNameInDesc(linesString, objName, newObjName)
                
                #Update transition expression
                linesString = ReplaceNameInExp(linesString, objName, newObjName)
                
                #Updates fhx lines with new transition description and expression
                fhxLines[lineNum: lineNum + size] = linesString.split('\n')

def RenameActions(fhxLines, newActNames, actMap, objMap):
    '''
    Updates fhx lines to rename actions based on new names dictionary. 
    Updates lines in-place.
    '''
    origFhxLines = fhxLines
    
    for stepAction in newActNames.keys():
        [step, action] = stepAction.split('/')
        newName = newActNames[stepAction]
        
        actLineNum = actMap[stepAction]['Line Number']
        
        actNameLine = fhxLines[actLineNum]
        
        #Updates action name
        fhxLines[actLineNum] = actNameLine[:actNameLine.index('"')] + AddQuotes(newName)
        
        neighActions = actMap[stepAction]['Neighboring Actions']
        
        for neighAction in neighActions:
            stepNeighAction = '/'.join([step, neighAction])
            actLineNum = actMap[stepNeighAction]['Line Number']
            actSize = actMap[stepNeighAction]['Size']
            
            existActSection = '\n'.join(origFhxLines[actLineNum: actLineNum + actSize])
            actionSection = '\n'.join(fhxLines[actLineNum: actLineNum + actSize])
            
            #Updates action name in description fields if found
            if (f'"{action} ' in existActSection or
                f' {action} ' in existActSection or
                f' {action},' in existActSection or
                f' {action}"' in existActSection):
                actionSection = ReplaceNameInDesc(actionSection, action, newName)
            
            #Updates action name in expression fields if found
            if f"/{action}/" in existActSection:
                actionSection = ReplaceNameInExp(actionSection, action, newName, isAction=True)
            
            #Update fhx lines
            fhxLines[actLineNum: actLineNum + actSize] = actionSection.split('\n')

def BuildStepIndexActions(fhxLines, objMap):
    '''
    This function builds an action in each step to update step index.
    Updates fhx lines in-place.
    '''
    
    IsStep = lambda obj: objMap[obj][TYPE] == STEP
    
    steps = list(filter(IsStep, objMap.keys()))
    
    for step in steps:
        
    

'''
Functions which find or modify strings.
'''
def FindString(string, ID, endChar = '"', startIdx = 0, isExp=False):
    '''
    Finds and returns substring within fhx lines string.
    '''
    idx = string.index(ID, startIdx) + len(ID)
    
    #If string is an expression
    if isExp:
        endIdx = idx - 2
        
        #Loop until end of expression is found
        while True:
            endIdx = string.index('"\n', endIdx + 2)
            
            if (string[endIdx - 1] != '"' or
                string[endIdx - 2: endIdx] == '""' and string[endIdx - 3] != '"' or
                string[endIdx - 4: endIdx] == '""""'):
                return string[idx:endIdx].replace('""', '"')
    
    #Return string value if not expression
    return string[idx:string.index(endChar, idx)]

def ReplaceNameInDesc(desc, name, newName):
    '''
    Searches fhx string to replace name in description field.
    '''
    desc = desc.replace(f'"{name} ', f'"{newName} ')
    desc = desc.replace(f' {name} ', f' {newName} ')
    desc = desc.replace(f' {name},', f' {newName},')
    desc = desc.replace(f' {name}"', f' {newName}"')
    
    return desc

def ReplaceNameInExp(exp, name, newName, isAction=False):
    '''
    Searches fhx string to replace name in expression field.
    '''
    if isAction:
        exp = exp.replace(f"/{name}/", f"/{newName}/")
    else:
        exp = exp.replace(f"'{name}/", f"'{newName}/")
    
    return exp

def ConvertCondExpToList(exp):
    '''
    Takes a condition expresion and creates a list where every line is a single condition.
    '''
    exp = exp.replace('\n', '').strip()
        
    exp = exp.replace(' and', ' AND').replace(' And', ' AND')
    exp = exp.replace(' AND', ' AND\n')
    exp = exp.replace(' or', ' OR').replace(' Or', ' OR')
    exp = exp.replace(' OR', ' OR\n')
    
    expLines = exp.split('\n')
    expLines = [line.strip() for line in expLines]
    
    return expLines

AddParentheses = lambda string: string.join(['(', ')'])
AddQuotes = lambda string: string.join(['"', '"'])
FindInitStep = lambda lines: FindString(lines, '    INITIAL_STEP="')

'''
Terminal messaging related functions.
'''
def UpdateTerminal(text, msgTotal):
    '''
    Updates terminal messaging so user can see progress.
    Message count is a global variable.
    '''
    global msgCount
    
    msgCount += 1
    pctComplete = round(100 * msgCount / msgTotal, 1)
    
    #Progress for terminal
    print(f'Building {text}: {pctComplete} %', end='\r')
    
    #Reset count and add new line if total reached
    if msgCount == msgTotal:
        msgCount = 0
        print('')
