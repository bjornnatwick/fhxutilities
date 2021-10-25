'''
    DeltaV fhx Constants Config File
    Rev: 0.0
    
    This config file contains constants for DeltaV fhx file parsing and updating.
'''

NA, ALPHA_NUM, POS_LINE_NUM = 'N/A', 'Alphabetical Numeric', 'Position Line Number'

CLASSES, NAMED_SETS, FB_DEF, FBS, MODULES = 'Classes', 'Named Sets', 'Function Block Definition', 'Function Block Instances', 'Module Instances'
MODULE_CLASS, EM_CLASS, PHASE_CLASS, UNIT_CLASS, PROCCELL_CLASS, EQUTRN_CLASS = 'Module Class', 'EM Class', 'Phase Class', 'Unit Class', 'Process Cell Class', 'Equlpment Train Class'
CLASS_TYPES = (MODULE_CLASS, EM_CLASS, PHASE_CLASS, UNIT_CLASS, PROCCELL_CLASS, EQUTRN_CLASS)

NAMED_SET = 'Named Set'
RUN, HOLD, RESTART, ABORT, STOP = 'RUN_LOGIC', 'HOLD_LOGIC', 'RESTART_LOGIC', 'ABORT_LOGIC', 'STOP_LOGIC'
PHASE_CMDS = (RUN, HOLD, RESTART, ABORT, STOP)
STEP, ACTION, TRANSITION, VARIABLE, TYPE, NEXT_OBJS, OBJS = 'Step', 'Action', 'Transition', 'Variable', 'Type', 'Next Objects', 'Objects'

INDEX, XPOS, YPOS, HEIGHT, WIDTH = 'Index', 'Xpos', 'Ypos', 'Height', 'Width'
CLASS_NAME, CLASS_DESC, CMD_NAME, COMP_NAME = 'Class Name', 'Class Description', 'Command Name', 'Composite Name'
STEP_TRAN, STEP_TRAN_NAME, STEP_TRAN_DESC, TRAN_EXP = 'Step or Transition', 'Step/Transition Name', 'Step/Transition Description', 'Transition Expression'
ACT_NAME, ACT_DESC, ACT_TYPE, ACT_QUAL = 'Action Name', 'Action Description', 'Action Type', 'Action Qualifier'
ACT_DELAY, ACT_EXP, CFM_EXP, CFM_TMO = 'Action Delay', 'Action Expression', 'Confirm Expression', 'Confirm Timeout'
QUAL_NO_DELAY, QUAL_NO_CFM = ('N', 'R', 'S'), ('N', 'R', 'S', 'L', 'D', 'SD', 'DS', 'SL')

SFC_COL_NAMES = (INDEX,
                CLASS_NAME,
                CLASS_DESC,
                CMD_NAME,
                COMP_NAME,
                STEP_TRAN,
                STEP_TRAN_NAME,
                STEP_TRAN_DESC,
                TRAN_EXP,
                ACT_NAME,
                ACT_DESC,
                ACT_TYPE,
                ACT_QUAL,
                ACT_DELAY,
                ACT_EXP,
                CFM_EXP,
                CFM_TMO)
                
VAR_NAME, VAR_DESC, VAR_TYPE, VAR_VALUE, VAR_GROUP, VAR_CATEGORY = 'Variable Name', 'Variable Description', 'Variable Type', 'Variable Value', 'Variable Group', 'Variable Category'
VAR_COL_NAMES = (CLASS_NAME, 
                 VAR_NAME, 
                 VAR_DESC,
                 VAR_TYPE, 
                 VAR_VALUE, 
                 VAR_GROUP, 
                 VAR_CATEGORY)
                 
NS_NAME, NS_DESC = 'Name', 'Description'
NS_COL_NAMES = (NS_NAME, NS_DESC) + tuple(range(256))

VAR_TYPE_TXT = {'UNICODE_STRING':'String', 'ENUMERATION_VALUE':'Named Set', 'EVENT': 'Alarm', 'MODE':'Mode', 'SCALING': 'Scaling', 'FLOAT_ARRAY': 'Floating Point Array',
                'INTERNAL_REFERENCE':'Internal Reference', 'DYNAMIC_REFERENCE': 'Dynamic Reference', 'EXTERNAL_REFERENCE': 'External Reference',
                'FLOAT': 'Floating Point', 'FLOAT_WITH_STATUS': 'Floating Point with Status', 'BOOLEAN':'Boolean', 'BOOLEAN_WITH_STATUS': 'Boolean with Status',
                'DISCRETE_WITH_STATUS': 'Discrete with Status', 'UINT8':'Unsigned 8-bit Integer', 'UINT16':'Unsigned 16-bit Integer', 'UINT32':'Unsigned 32-bit Integer',
                'INT8': 'Signed 8-bit Integer', 'INT16': 'Signed 16-bit Integer', 'INT32': 'Signed 32-bit Integer', 'UINT32_WITH_STATUS': 'Unsigned 32-bit Integer with Status'}
                
VAR_TYPE_TXT_BAT = {'ENUMERATION_VALUE':{'INPUT': 'Batch Input - Named Set', 'OUTPUT': 'Batch Report - Named Set'}, 'UNICODE_STRING': {'INPUT':'Batch Input - String', 'OUTPUT': 'Batch Report - String'},
                    'BATCH_PARAMETER_INTEGER':{'INPUT': 'Batch Input - Integer', 'OUTPUT': 'Batch Input - Integer'}, 'BATCH_REPORT_INTEGER':{'INPUT': 'Batch Report - Integer', 'OUTPUT': 'Batch Report - Integer'}, 
                    'BATCH_PARAMETER_REAL':{'INPUT': 'Batch Input - Real', 'OUTPUT': 'Batch Report - Real'}, 'BATCH_REPORT_REAL':{'INPUT': 'Batch Report - Real', 'OUTPUT': 'Batch Report - Real'}}

VAR_VALUE_TXT = {'F':'False', 'T':'True'}

BRANCHES, PREV_BRANCH = 'Branches', 'Previous Branches'

FBS_TO_SKIP = ['__DEFAULT_PHASE_SFC__']

'''
Constants for sfc overhaul tool
'''
    #Step and transition position and size
STEP_SIZE = {HEIGHT:40, WIDTH:120}
TRAN_SIZE = {HEIGHT:20, WIDTH:20} #DO NOT CHANGE
STEP_TRAN_X_DIFF = int((STEP_SIZE[WIDTH] - TRAN_SIZE[WIDTH]) / 2) #DO NOT CHANGE
INIT_STEP_POS = (200, 120)
STEP_TRAN_VERT_DIST = 75
TRAN_STEP_VERT_DIST = 55
BRANCH_DIST = 80 + STEP_SIZE[WIDTH]
TP_BRANCH_DIST = 100 + BRANCH_DIST
TASK_PTR_PARAM_NAME = "'^/P_TASK_POINTER"
SEGMENT_DIST_BELOW_TRAN = 30
SEGMENT_DIST_ABOVE_STEP = 20
SEGMENT_DIST_LEFT_OF_TRAN = 15 + int(STEP_SIZE[WIDTH] / 2 - TRAN_SIZE[WIDTH] / 2)
SEGMENT_DIST_RIGHT_OF_TRAN = 15 + int(STEP_SIZE[WIDTH] / 2 + TRAN_SIZE[WIDTH] / 2)
SEGMENT_TP_X_DIST = 30
SEGMENT_SPACING = 7
    #Step, action, and transition renaming
INIT_STEP_NUM = 0
OBJ_NAME_INCREM = 10
TERM_NAME = 'END'
OBJ_NAME_NUM_OF_NUMER_CHAR = 4 #Number of numeric characters in step and transition names
TRAN_INIT_CHAR = 'T'
LAST_STEP_NUM = 9900
ACTION_INIT_NUM = 10
ACTION_NUM_INCREM = 10
ACTION_INIT_CHAR = 'A'
ACTION_NS_INIT_CHAR = 'NS' #Initial character(s) for non-stored actions
ACTION_NUM_OF_NUMER_CHAR = 1 #Number of numeric characters in action names