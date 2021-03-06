"""Specify path to csv file that contains transfer results"""
CSV_FILE = './Arch/majowka/test_resultNONDUPLEX.csv'

"""Specify separator in csv file"""
SEPARATOR = ';'

"""Specify number of statistical iterations based on config file"""
STATISTICAL_ITERATIONS = 10

"""Check if any error occured during transfer and return it on stdout"""
CHECK_FOR_ERRORS = False

"""Specify the target speed that will be collocated with pattern sizes on charts (also available: 'PC' and 'FPGA')"""
TARGET_SPEED = 'AV'

"""Each combination of parameters on separated chart? (default: no)"""
PARAMETERS_SEPARATED = False

"""Generate LaTeX results chapter? (default: no)"""
GENERATE_RESULTS_CHAPTER = True
RESULTS_CHAPTER_FILE_NAME = 'results_ver2.tex'
FIG_FOLDER = 'src/results/' # Where figures will be sotred in TeX project?


"""Try not to modify this section on your own (except you know exactely what are you doing)!"""

"""Results that need casting to integers"""
INT_VALUES = ['FifoDepth', 'PatternSize', 'BlockSize', 'StatisticalIter', 'Iterations', 'Errors']

"""Results that need casting to floats"""
FLOAT_VALUES = ['PC time(total) [us]', 'PC time(per iteration) [us]',
				'FPGA time(total) [us]', 'CountsInFPGA',
				'FPGA time(per iteration) [us]', 'SpeedPC [B/s]',
				'SpeedFPGA [B/s]']

"""Names of heads after refactoring"""
REFACTORED_HEADS = ['Mode', 'Direction', 'FifoMemoryType', 'FifoDepth', 'PatternSize', 'BlockSize', 'DataPattern', 'SpeedPC', 'u(PC)', 'SpeedFPGA', 'u(FPGA)', 'Average', 'u(av)']

"""Metadata for figure objects"""
FIGURE_METADATA = {
	'xlabel' : 'Pattern size [B]',
	'xscale' : 'log',
	'ylabel_PC' : 'Speed PC [MB/s]',
	'ylabel_FPGA' : 'Speed FPGA [MB/s]',
	'ylabel_AV' : 'Average speed [MB/s]',
	'yticks' : [i for i in range(0, 401, 50)],
	'grid' : True,
	'error' : 'Target ylabel should be defined as PC, FPGA or AV'
}

"""Properties that can be combined with each other"""
BASIC_PROPERTIES = {
	'Mode' : ['nonsym', '32bit', 'duplex'],
	'Direction' : ['read', 'write', 'bidir'],
	'FifoMemoryType' : ['blockram', 'distributedram', 'shiftregister'],
	'FifoDepth': [16, 32, 64, 256, 1024, 2048],
	'BlockSize': [16, 64, 256, 1024],
	'DataPattern' : ['counter_8bit', 'counter_32bit', 'walking_1', 'asic']
}

"""Plotting options mapped to proper names"""
MODES_DICT = {
	'memtype_depth_pattern': 'Patterns',
	'depth_pattern_memtype': 'Memory types',
	'pattern_memtype_depth': 'Depths'
}

"""Combined parameters"""
PLOTTING_OPTIONS = {
	'memtype_depth_pattern' : {
		# 'title' : 'Direction: {}. Fifo memory type: {}. Depth = {}',
		'title' : 'Transfer results for \\textit{{{}}} direction, \\textit{{{}}} FIFO memory type with \\textit{{{}}} depth value.',
		'subsection': 'Patterns',
		'savefig' : '{}_{}_{}_patterns.pdf',
		'valid_modes': ['32bit', 'nonsym'],
		'first_param' : 'FifoMemoryType',
		'second_param' : 'FifoDepth',
		'third_param' : 'DataPattern',
		'legend' : {
			'counter_8bit' : 'ro',
			'counter_32bit' : 'g*',
			'walking_1' : 'b+',
			'asic' : 'mv'
		}
	},
	'depth_pattern_memtype' : {
        # 'title' : 'Direction: {}. Fifo depth: {}. Pattern type = {}',
		'title' : 'Transfer results for \\textit{{{}}} direction, \\textit{{{}}} FIFO depth value and \\textit{{{}}} pattern type.',
		'subsection': 'Memory types',
		'savefig' : '{}_{}_{}_memory_types.pdf',
		'valid_modes': ['32bit', 'nonsym'],
		'first_param' : 'FifoDepth',
		'second_param' : 'DataPattern',
		'third_param' : 'FifoMemoryType',
		'legend' : {
			'blockram' : 'ro',
			'distributedram' : 'g*',
			'shiftregister' : 'b+'
		}
	},
	'pattern_memtype_depth' : {
		# 'title' : 'Direction: {}. Pattern type: {}. Fifo memory type: {}',
		'title' : 'Transfer results for \\textit{{{}}} direction, \\textit{{{}}} pattern type and \\textit{{{}}} FIFO memory type.',
		'subsection': 'Depths',
		'savefig' : '{}_{}_{}_depths.pdf',
		'valid_modes': ['32bit', 'nonsym'],
		'first_param' : 'DataPattern',
		'second_param' : 'FifoMemoryType',
		'third_param' : 'FifoDepth',
		'legend' : {
			16 : 'ro',
			32 : 'y^',
			64 : 'g*',
			256 : 'b+',
			1024 : 'mv',
			2048 : 'r+'
		}
	}
	# 'duplex_memtype_blocksize_pattern': {
	# 	'title': 'Fifo memory type: {}. Block size = {}',
	# 	'savefig': '{}_{}_{}_patterns.png',
	# 	'valid_modes': ['duplex'],
	# 	'first_param': 'FifoMemoryType',
	# 	'second_param': 'BlockSize',
	# 	'third_param': 'DataPattern',
	# 	'legend': {
	# 		'counter_8bit': 'ro',
	# 		'counter_32bit': 'g*',
	# 		'walking_1': 'b+',
	# 		'asic' : 'mv'
	# 	}
	# },
	# 'duplex_blocksize_pattern_memtype': {
	# 	'title' : 'Block size: {}. Pattern type = {}',
	# 	'savefig' : '{}_{}_{}_memory_types.png',
	# 	'valid_modes': ['duplex'],
	# 	'first_param' : 'BlockSize',
	# 	'second_param' : 'DataPattern',
	# 	'third_param' : 'FifoMemoryType',
	# 	'legend' : {
	# 		'blockram' : 'ro',
	# 		'distributedram' : 'g*',
	# 		'shiftregister' : 'b+'
	# 	}
	# },
	# 'duplex_pattern_memtype_blocksize': {
	# 	'title' : 'Pattern type: {}. Fifo memory type: {}',
	# 	'savefig' : '{}_{}_{}_blocksizes.png',
	# 	'valid_modes': ['duplex'],
	# 	'first_param' : 'DataPattern',
	# 	'second_param' : 'FifoMemoryType',
	# 	'third_param' : 'BlockSize',
	# 	'legend' : {
	# 		16 : 'ro',
	# 		64 : 'g*',
	# 		256 : 'b+',
	# 		1024 : 'mv'
	# 	}
	# }
}
