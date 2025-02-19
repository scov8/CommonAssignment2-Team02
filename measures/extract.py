#
# Course: High Performance Computing 2021/2022
#
# Lecturer: Francesco Moscato	fmoscato@unisa.it
#
# Group:
# Rosa Gerardo	    0622701829	g.rosa10@studenti.unisa.it
# Scovotto Luigi    0622701702  l.scovotto1@studenti.unisa.it
# Tortora Francesco 0622701700  f.tortora21@studenti.unisa.it
#
# Copyright (C) 2022 - All Rights Reserved
# This file is part of CommonAssignment2.
#
# Requirements: Parallelize and Evaluate Performances of "COUNTING SORT" Algorithm ,by using MPI.
#
# The previous year's group 02 files proposed by the professor during the course were used for file generation and extraction.
#
# The starting point for the counting sort function was from this video:
# https://www.youtube.com/watch?v=qcOoEjdYSz0
#
# CommonAssignment2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CommonAssignment2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CommonAssignment2.  If not, see <http://www.gnu.org/licenses/>.
#
# You can find the complete project on GitHub:
# https://github.com/scov8/CommonAssignment2-Team02

import os
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
import seaborn as sns
from prettytable import PrettyTable
from prettytable import MARKDOWN
from prettytable import MSWORD_FRIENDLY
import re

config = {
			'seqKey': "NP-01",													#is used to choose which reference to take for the plot
			'filenameRegex': "SIZE-[0-9]+-NP-[0-9]{2}-O[0-6]-?[0-9]*",
			'folderRegex':"SIZE-[0-9]+-O[0-9]",
			"cols":{'generateArray_time':{'jpg':False,'computeSpeedup':False,},
					'countingSort_time':{'jpg':False,'computeSpeedup':False,}, 	#if the 'computeSpeedup' is set to true I make the graphs referring to this
					'elapsed':{'jpg':False,'computeSpeedup':True,} 				#we have decided to take as a reference the elapsed
					},
			"table":{
				"header": ['Version','Processes','GenerateArray','CountingSort','Elapsed','Speedup','Efficiency'],
			},
			"plot":{
				"x_from_table":"Processes",
				"y_from_table":"Speedup",
			},
			"calcComplExpr":""
		}
#same except if on skip file
def _extract(path_to_folder,plot_columns):
	prev = os.getcwd()
	os.chdir(path_to_folder)

	#List diresctory
	filenames =  [f for f in os.listdir('.') if os.path.isfile(f)]
	if not os.path.exists("jpg"):
		os.mkdir("jpg")

	#Remove not csv files
	#"SIZE-[0-9]+-NTH-[0-9]{2}-O[0-9]-?[0-9]*"
	filenames = [f for f in os.listdir('.') if f.endswith(".csv") and re.match(config["filenameRegex"],f) ]
	print(filenames)

	filenames = sorted(filenames)
	means = {}
	
	for filename in filenames:
		file_mean = {}
		print('Processing : ' + filename)
		ds = pd.read_csv(filename)
		for col in plot_columns.keys():
			print('Processing : ' + filename + ", Col : " + col)
			#extract the selected column
			x_data = ds[col]
			#compute gaussian mean
			mean,std=stats.norm.fit(x_data)
			#compute mean as usual, to use when only few measures are taken
			np_mean = np.mean(x_data)

			#68,3% = P{ μ − 1,00 σ < X < μ + 1,00 σ }
			x_data = ds[(ds[col] < (mean + std)) & (ds[col] > (mean - std))][col]
			mean,std=stats.norm.fit(x_data)
			file_mean[col] = mean if np_mean == mean else np_mean
			
			if plot_columns[col]['jpg']:
				sns.histplot(x_data, kde=True)
				plt.savefig("jpg/" + str(col)+ "_" + filename.split('.')[0] + ".jpg")
				plt.close()
			
		means[filename] = file_mean
	os.chdir(prev)
	return means

#same
def _compute_speedup(t,tp,nt,psize):
	speedup = t/tp
	efficiency = t/(tp*float(nt))
	return speedup,efficiency

#same
def _make_table(header,rows,print_table=False,save=True,name=""):
	if save and not name:
		raise Exception("No filename to save file")
	x = PrettyTable()
	x.field_names = header
	x.add_rows(rows)
	if save:
		_save_table(x,name)
	if print_table:
		print(x)
	return x
	
#same
def _save_table(table,filename):
	with open(filename,"w") as table_file:
		#table.set_style(MARKDOWN)
		table.set_style(MSWORD_FRIENDLY)
		data = table.get_string()
		table_file.write(data)

#same
def _plot_from_table(header,rows,save=True,name="",show_plot=False):
	if save and not name:
		raise Exception("No filename to save file")

	x = [0]
	y = [0]
	try:
		x_from_table = config["plot"]["x_from_table"]
		y_from_table = config["plot"]["y_from_table"]
		speedup_pos = config["table"]["header"].index(y_from_table) #header.index("Speedup")
		thread_pos = config["table"]["header"].index(x_from_table) #header.index("Threads")
	except Exception as e:
		print("config table or plot error")

	for row in rows[0:]: #to start from the row 0
		x.append(row[thread_pos])
		y.append(row[speedup_pos])

	x_th = np.array(x)
	fig, ax = plt.subplots(figsize=(12, 8))
	ax.plot(x_th, y, 'ro-', label='Experimental')
	ax.plot(x_th, x_th, color='blue', label='Ideal')
	#same as y_th, bisection
	plt.style.use('seaborn-whitegrid')

	plt.autoscale(enable=True, axis='x', tight=True)
	plt.autoscale(enable=True, axis='y', tight=True)	

	plt.legend()
	plt.xlabel(x_from_table)
	plt.ylabel(y_from_table)
	if show_plot:
		plt.show()
	if save:
		plt.savefig(name)
	plt.close()

#same
def extraction(root=os.path.join(os.path.dirname(os.path.realpath(__file__)),"measure/"), cols=config["cols"], threads=[0,1,2,4,8]):
	print("Listing folder for problem size")
	folders =  [f for f in os.listdir(root) if (os.path.isdir(os.path.join(root,f)) and re.match(config['folderRegex'],f))]
	print(f"Found folders : {folders}")

	for folder in folders:
		print(f"Folder : {folder}")
		joined_path = os.path.join(root,folder)
		means = _extract(joined_path,cols)
		header = {'values':config["table"]["header"]}
		cells = {'values':[]}
		nt = -1
		for filename_key in means:
			cell = []
			splitted_filename = filename_key.split("-")
			if config["seqKey"] in filename_key:
				seq = means[filename_key]['elapsed'] #we must specify who we are plotting
				print("la media:      ",seq)
				nt = 1
				cell.append('Parallel')
				cell.append(nt)
			else:
				nt = int(splitted_filename[3])
				cell.append('Parallel')
				cell.append(nt)

			for col in cols:
				cell.append(means[filename_key][col])
				if cols[col]['computeSpeedup']:
					psize = splitted_filename[1]
					speedup,efficiency = _compute_speedup(seq,means[filename_key][col],nt,psize)
					cell.append(speedup)
					cell.append(efficiency)
			cells['values'].append(cell)
		
		splitted_folder = folder.split("-")
		size = splitted_folder[1]
		opt = splitted_folder[2]
		table_filename = joined_path + "/psize-" + size + "-" + str(opt) + "-table.csv"
		plot_filename = joined_path + "/speedup-" + str(size) + "-" + str(opt) +  ".jpg"

		table = _make_table(header['values'],cells['values'],name=table_filename)
		_plot_from_table(header["values"],cells["values"],name=plot_filename)
#same
if __name__ == "__main__":
	extraction()
