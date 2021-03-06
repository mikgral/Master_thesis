from cfg import * 
import csv
import math
import matplotlib.pyplot as plt
import statistics as stat


class ResultsParser(object):
	"""Transform data from csv file to list of dicts.

	Attributes:
		int_values (list): specifes which values need to be integers.
		float_values (list): specifes which values need to be floats.
		refactored_heads (list): list of headers for refactoring the original data.
		stat_iterations (int): how many iterations were performed for better statistics.
		results_list (list): list of results from csv file.
		headers_list (list): list of headers from csv file.
		list_of_results_dicts (list): list of dicts of original data.
	"""
	def __init__(self, csv_file, delimiter, int_values, float_values, refactored_heads, stat_iterations):
		"""Args:
			csv_file (string): name of csv file that contains data.
			delimiter (char): the character used for separating values in csv file.
			int_values (list): specifes which values need to be integers.
			float_values (list): specifes which values need to be floats.
			refactored_heads (list): list of headers for refactoring the original data.
			stat_iterations (int): how many iterations were performed for better statistics.
		"""
		self.int_values = int_values
		self.float_values = float_values
		self.refactored_heads = refactored_heads
		self.stat_iterations = stat_iterations
		self.results_list, self.headers_list = ResultsParser.results_and_headers_lists_from_file(csv_file, delimiter)
		self.list_of_results_dicts = self.__generate_results_list_of_dicts()

	@staticmethod
	def results_and_headers_lists_from_file(csv_file, delimiter):
		"""Returns list with results and headers list as tuple from csv file"""
		with open(csv_file, mode='r') as results_file:
			results_reader = csv.reader(results_file, delimiter=delimiter)
			headers_list = next(results_reader)
			results_list = list(results_reader)
		return results_list, headers_list

	def __hash_data(self, results_list):
		"""Transform desired numeric data from string to int / float"""
		for row in results_list:
			for int_value in self.int_values:
				row[self.headers_list.index(int_value)] = int(row[self.headers_list.index(int_value)])
			for float_value in self.float_values:
				row[self.headers_list.index(float_value)] = float(row[self.headers_list.index(float_value)])
		return results_list

	def __generate_results_list_of_dicts(self):
		hashed_results_list = self.__hash_data(self.results_list)
		list_of_results_dicts = []
		for row in hashed_results_list:
			results_dicts = {head : row[self.headers_list.index(head)] for head in self.headers_list}
			list_of_results_dicts.append(results_dicts)
		return list_of_results_dicts

	def __transform_row_to_dict(self, row,  params):
		row_dict = {}
		for head in self.refactored_heads:
			if head in self.headers_list:
				row_dict[head] = row[head]
			else:
				row_dict[head] = params.get_refactored_param(head)
		return row_dict

	def get_refactored_list_of_results_dicts(self, in_megabytes=True):
		"""Returns list of dicts of refactored data.
		Args:
			in_megabytes (bool): does speed values need to be perfomed in megabytes
								 instead of bytes? (True by default)
		"""
		refactored_list_of_results_dicts = []
		results_fpga_array = []
		results_pc_array = []
		for row in self.list_of_results_dicts:
			results_fpga_array.append(row['SpeedFPGA [B/s]'])
			results_pc_array.append(row['SpeedPC [B/s]'])
			if row['StatisticalIter'] == self.stat_iterations:
				params = CounterParams(results_fpga_array, results_pc_array, in_megabytes)
				row_dict = self.__transform_row_to_dict(row, params)
				refactored_list_of_results_dicts.append(row_dict)
				results_fpga_array = []
				results_pc_array = []
		return refactored_list_of_results_dicts

	def check_errors(self):
		errors_occurance = 0
		for results_dict in self.list_of_results_dicts:
			errors = results_dict['Errors']
			if errors != 0:
				print(errors, "errors occured in row:\n", results_dict)
				errors_occurance += 1
		if errors_occurance == 0:
			print("No errors detected")

class CounterParams(object):
	def __init__(self, speed_fpga_list, speed_pc_list, in_megabytes):
		if in_megabytes is True:
			self.divider = 1000000
		else:
			self.divider = 1
		self.av_speed_fpga = stat.mean(speed_fpga_list)
		self.av_speed_pc = stat.mean(speed_pc_list)
		self.stdev_speed_fpga = stat.stdev(speed_fpga_list)
		self.stdev_speed_pc = stat.stdev(speed_pc_list)
		self.av_speed = self.__av_speed()
		self.stdev_speed = self.__stdev_speed()

	def __av_speed(self):
		return (self.av_speed_fpga + self.av_speed_pc) / 2

	def __stdev_speed(self):
		fpga_arg = math.pow(self.stdev_speed_fpga/2, 2)
		pc_arg = math.pow(self.stdev_speed_pc/2, 2)
		sum_of_args = fpga_arg + pc_arg
		return math.sqrt(sum_of_args)

	def get_refactored_param(self, head):
		if head == 'SpeedPC':
			return self.av_speed_pc / self.divider
		elif head == 'SpeedFPGA':
			return self.av_speed_fpga / self.divider
		elif head == 'u(PC)':
			return self.stdev_speed_pc / self.divider
		elif head == 'u(FPGA)':
			return self.stdev_speed_fpga / self.divider
		elif head == 'Average':
			return self.av_speed / self.divider
		elif head == 'u(av)':
			return self.stdev_speed / self.divider

class ResultsHandler(object):
	def __init__(self, list_of_results_dicts, plot_metadata, target_speed, basic_properties):
		self.list_of_results_dicts = list_of_results_dicts
		self.metadata = plot_metadata
		self.target_speed = target_speed
		self.basic_properties = basic_properties
		self.x_param = []
		self.chapter_file_name = None
		self.fig_folder = None
		self.generate_results_chapter = False

	def enable_results_chapter_generation(self, results_chapter_file_name, fig_folder):
		self.generate_results_chapter = True
		self.chapter_file_name = results_chapter_file_name
		self.fig_folder = fig_folder

	def __iterate_using_params(self, first_param_label, second_param_label, third_param_label, valid_modes):
		list_of_param_dicts = []
		for mode in self.basic_properties['Mode']:
			for direction in self.basic_properties['Direction']:
				for first_param in self.basic_properties[first_param_label]:
					for second_param in self.basic_properties[second_param_label]:
						results_dict = {}
						x_param = []
						for third_param in self.basic_properties[third_param_label]:
							x_param = []
							y_param = []
							yerr_param = []
							for row in self.list_of_results_dicts:
								if ((mode == row['Mode']) and
									(mode in valid_modes) and
									(direction == row['Direction']) and
									(first_param == row[first_param_label]) and
									(second_param == row[second_param_label]) and
									(third_param == row[third_param_label])):
									x_param.append(row['PatternSize'])
									y_param.append(row['Average'])
									yerr_param.append(row['u(av)'])
							if y_param:
								results_dict[third_param] = {
									'x': x_param,
									'y': y_param,
									'yerr': yerr_param
								}
								self.x_param = x_param
						max_third_param_list = []
						for i, x in enumerate(self.x_param):
							max_value = None
							for param in results_dict:
								current_value = results_dict[param]['y'][i]
								if not max_value:
									max_value = current_value
									max_third_param_list.append({param : "{0:.3f}".format(max_value)})
									continue
								elif current_value > max_value:
									max_value = current_value
									max_third_param_list[i] = {param : "{0:.3f}".format(max_value)}

						most_frequent_third_param_dict = {}
						for mtp in max_third_param_list:
							for m in mtp:
								if not m in most_frequent_third_param_dict:
									most_frequent_third_param_dict[m] = 0
								else:
									most_frequent_third_param_dict[m] += 1
						# print(most_frequent_third_param_dict)
						most_frequent_third_param = [par for par in most_frequent_third_param_dict if most_frequent_third_param_dict[par] == max(most_frequent_third_param_dict.values())]

						param_dict = {
							'mode': mode,
							'direction': direction,
							'first_param': first_param,
							'second_param': second_param,
							'max_third_param' : max_third_param_list,
							'most_frequent_third_param' : most_frequent_third_param,
							'third_param': results_dict
						}
						if param_dict['third_param']:
							list_of_param_dicts.append(param_dict)
		return list_of_param_dicts

	def list_of_results_with_parameters(self, plotting_option, option=None):
		first_param_label = plotting_option['first_param']
		second_param_label = plotting_option['second_param']
		third_param_label = plotting_option['third_param']
		valid_modes = plotting_option['valid_modes']
		list_of_param_dicts = self.__iterate_using_params(first_param_label,
														  second_param_label,
														  third_param_label,
														  valid_modes)
		return list_of_param_dicts

	def __append_string_to_chapter_file(self, string_to_append):
		with open(self.chapter_file_name, "a") as fd:
			fd.write(string_to_append)

	def __generate_first_column_for_tab(self, rows, is_max_row_needed=True):
		first_row = '\\textbf{Pattern size [B]} '
		last_row = '\\textbf{Most frequent parameter} '
		rows.append(first_row)
		for size in self.x_param:
			row = '\\multirow{{2}}{{*}}{{\\textbf{{{}}}}}'.format(size)
			rows.append(row)
		if is_max_row_needed:
			rows.append(last_row)

	def __refactor_string_to_latex_standard(self, string_to_refactor):
		string_to_refactor_list = list(string_to_refactor)
		for i, char in enumerate(string_to_refactor_list):
			if char == '_':
				string_to_refactor_list[i] = '\_'
		string_to_refactor = ''.join(string_to_refactor_list)
		return string_to_refactor


	def __append_next_column_to_tab(self, rows, param_dict, column_name=None):
		if column_name:
			second_param = self.__refactor_string_to_latex_standard(str(column_name))
		else:
			second_param = self.__refactor_string_to_latex_standard(str(param_dict['second_param']))
		rows[0] += (' & ' + '\\textbf{{{}}}'.format(second_param))
		for i, x in enumerate(self.x_param):
			try:
				max_third_param_dict = param_dict['max_third_param'][i]
				key = ''.join(str(mtp_key) for mtp_key in max_third_param_dict.keys())
				value = ''.join(max_third_param_dict.values())
				max_third_param = "{} \\break [\\textit{{{}}}]".format(key, value)
				max_third_param = self.__refactor_string_to_latex_standard(max_third_param)
				row = ' & ' + max_third_param
				rows[i+1] += row
			except IndexError:
				break
		most_frequent_third_params = ', '.join(str(mftp) for mftp in param_dict['most_frequent_third_param'])
		most_frequent_third_params = self.__refactor_string_to_latex_standard(most_frequent_third_params)
		rows[len(rows) - 1] += ' & ' + most_frequent_third_params

	def __append_next_column_in_nonsym_memtype_mode_to_tab(self, rows, column_name, read_value_list, write_value_list):
		column_name = self.__refactor_string_to_latex_standard(column_name)
		rows[0] += (' & ' + '\\textbf{{{}}}'.format(column_name))
		for i, x in enumerate(self.x_param):
			try:
				read_value = read_value_list[i]
				write_value = write_value_list[i]
				max_third_params = "{} \\break [\\textit{{{}}}]".format(read_value, write_value)
				max_third_params = self.__refactor_string_to_latex_standard(max_third_params)
				row = ' & ' + max_third_params
				rows[i+1] += row
			except IndexError:
				break

	def __organize_figures(self, fig_names_list):
		fig_init = "\\includegraphics[width=\\textwidth]{{{}}}"
		minipage = '\\begin{{minipage}}{{0.48\\textwidth}}\n\t\\centering\n\t{}\n\t\\caption{{{}}}\n\\end{{minipage}}%\n'
		is_new_line = False
		for fig_name_dict in fig_names_list:
			fig_name = ''.join(fig_name_dict.keys())
			fig_title = ''.join(fig_name_dict.values())
			if not is_new_line:
				fig_declaration = '\\begin{figure}[H]\n\\centering\n'
				fig_declaration += minipage.format(fig_init.format(self.fig_folder + fig_name), fig_title)
				fig_declaration += '\\hspace{0.02\\textwidth}\n'
				is_new_line = True
			else:
				fig_declaration += minipage[:-2].format(fig_init.format(self.fig_folder + fig_name), fig_title)
				fig_declaration += '\n\\end{figure}\n\n'
				self.__append_string_to_chapter_file(fig_declaration)
				is_new_line = False

	def __add_subsection(self, subsection_name):
		subsection_def = '\\subsection{{{}}}\n'.format(subsection_name)
		self.__append_string_to_chapter_file(subsection_def)

	def __add_subsubsection(self, subsubsection_name):
		subsubsection_def = '\t\\subsubsection{{{}}}\n'.format(subsubsection_name)
		self.__append_string_to_chapter_file(subsubsection_def)

	def __add_tab(self, rows, tab_label):
		tab_label = self.__refactor_string_to_latex_standard(tab_label)
		col_numb = len(rows[0].split('&')) - 1
		width_ratio = "{0:.2f}".format(1 / (col_numb+1))
		col_separator = ' | P{{{}\\textwidth-2\\tabcolsep}}'.format(width_ratio) 
		begin_with_tab_label = "\\newpage\n\\begin{{center}}\n\t\\begin{{tab}}\n\t\t{}\n\t\\end{{tab}}\n\t\\footnotesize\n".format(tab_label)
		begin_tabular_with_specified_no_of_columns = "\t\\begin{{tabular}}{{| p{{{}\\textwidth-2\\tabcolsep}}{} |}}\n\\hline\n".format(width_ratio, col_separator * col_numb)
		self.__append_string_to_chapter_file(begin_with_tab_label)
		self.__append_string_to_chapter_file(begin_tabular_with_specified_no_of_columns)
		for i, row in enumerate(rows):
			if i == 0 or i == len(rows) - 2:
				self.__append_string_to_chapter_file(row + '\\\\ \\hline\n')
			else:
				self.__append_string_to_chapter_file(row + '\\\\ \\hline\n')
		ending = '\n\t\\end{tabular}\n\\end{center}\n'
		self.__append_string_to_chapter_file(ending)

	def __generate_subsection_based_on_plot_option(self, ploting_option, list_of_param_dict, all_fig_names):
		nonsym_figs = []
		bit32_figs = []
		duplex_figs = []
		for fig in all_fig_names:
			if 'nonsym' in ''.join(fig.keys()):
				nonsym_figs.append(fig)
			elif '32bit' in ''.join(fig.keys()):
				bit32_figs.append(fig)
			elif 'duplex' in ''.join(fig.keys()):
				duplex.append(fig)


	def handle_results(self, plotting_option, plot_index, separate_third_parameters=False):
		list_of_param_dicts = self.list_of_results_with_parameters(plotting_option)
		figure = Figure(self.metadata, self.target_speed, plotting_option['title'], plotting_option['savefig'])
		fig_names = []

		
		for i, param_dict in enumerate(list_of_param_dicts):
			for j, result in enumerate(param_dict['third_param']):
				x = param_dict['third_param'][result]['x']
				y = param_dict['third_param'][result]['y']
				yerr = param_dict['third_param'][result]['yerr']
				symbol = plotting_option['legend'][result]
				label = result
				figure.plot_fig_with_errorbars(x, y, yerr, symbol, label)
				if separate_third_parameters:
					fig_title = figure.set_title(param_dict['direction'], param_dict['first_param'], param_dict['second_param'])
					fig_title = self.__refactor_string_to_latex_standard(fig_title)
					fig_name = figure.save_fig(str(plot_index) + '_' + str(i) + '_' + str(j), param_dict['mode'], param_dict['direction'])
					fig_names.append({fig_name : fig_title})
			if not separate_third_parameters:
				fig_title = figure.set_title(param_dict['direction'], param_dict['first_param'], param_dict['second_param'])
				fig_title = self.__refactor_string_to_latex_standard(fig_title)
				fig_name = figure.save_fig(str(plot_index) + '_' + str(i), param_dict['mode'], param_dict['direction'])
				fig_names.append({fig_name : fig_title})

		if self.generate_results_chapter:
			self.__generate_subsection_based_on_plot_option(plotting_option, list_of_param_dicts, fig_names)


class Figure(object):
	def __init__(self, metadata, target_ylabel, fig_title, fig_name):
		self.__fig, self.__ax = plt.subplots()
		self.__metadata = metadata
		self.__target = target_ylabel
		self.__fig_title = fig_title
		self.__fig_name = fig_name

	def __set_metadata(self):
		self.__ax.set_xlabel(self.__metadata['xlabel'])
		self.__ax.set_xscale(self.__metadata['xscale'])
		self.__ax.set_ylabel(self.__target_ylabel())
		self.__ax.set_yticks(self.__metadata['yticks'])
		self.__ax.grid(self.__metadata['grid'])

	def __target_ylabel(self):
		if self.__target == 'PC':
			return self.__metadata['ylabel_PC']
		elif self.__target == 'FPGA':
			return self.__metadata['ylabel_FPGA']
		elif self.__target == 'AV':
			return self.__metadata['ylabel_AV']
		else:
			raise ValueError(self.__metadata['error'])

	def plot_fig_with_errorbars(self, x, y, yerr, symbol, label):
		self.__ax.errorbar(x, y, yerr=yerr, fmt=symbol, label=label)

	def set_title(self, *args):
		if args:
			fig_title = self.__fig_title.format(*args)
			if SET_TITLES_IN_FIGS:
				self.__ax.set_title(fig_title)
		else:
			fig_title = self.__fig_title
			if SET_TITLES_IN_FIGS:
				self.__ax.title(fig_title)
		return fig_title

	def save_fig(self, *args):
		self.__set_metadata()
		self.__ax.legend(loc='upper left')
		if args:
			fig_name = self.__fig_name.format(*args)
			self.__fig.savefig(fig_name)
		else:
			fig_name = self.__fig_name
			self.__fig.savefig(fig_name)
		self.__ax.clear()
		return fig_name


if __name__ == "__main__":
	results = ResultsParser(CSV_FILE, SEPARATOR, INT_VALUES, FLOAT_VALUES, REFACTORED_HEADS, STATISTICAL_ITERATIONS)
	if CHECK_FOR_ERRORS:
		results.check_errors()

	parsed_list_of_results_dicts = results.get_refactored_list_of_results_dicts()
	if GENERATE_RESULTS_CHAPTER:
		rh.enable_results_chapter_generation(RESULTS_CHAPTER_FILE_NAME, FIG_FOLDER)
	for i, plot_option in enumerate(PLOTTING_OPTIONS):
		rh.handle_results(PLOTTING_OPTIONS[plot_option], i, PARAMETERS_SEPARATED)
	# rh.save_to_figs(PLOTTING_OPTIONS['memtype_depth_pattern'], 0, PARAMETERS_SEPARATED)
	# rh.handle_results(PLOTTING_OPTIONS['memtype_depth_pattern'], 0, PARAMETERS_SEPARATED)
