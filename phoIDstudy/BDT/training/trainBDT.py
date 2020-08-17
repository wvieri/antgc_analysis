#!/usr/bin/env python3

####################################################################
# Photon ID BDT for aNTGC search in Z(->nu nu) + Gamma channel     #
# Mohammad Abrar Wadud (BD), 04/02/2020                            #
####################################################################

import numpy as np

# configure options
from argparse import ArgumentParser
parser = ArgumentParser(
	description='Photon ID BDT Training for CMS aNTGC search in Z(->nu nu) + gamma channel')
parser.add_argument('--inFilePath', type=str, help='Input root file',
					default='/hdfs/cms/user/wadud/anTGC/BDTdata/mergedSamplesShuffled.root', action='store')
parser.add_argument('--saveDir', type=str, default='/local/cms/user/wadud/aNTGCmet/aNTGC_analysis/phoIDstudy/BDT/data/training/',
					help='Save directory', action='store')
parser.add_argument('--inTreeName', type=str, default='fullEB_Tree',
					help='Input tree name', action='store')
parser.add_argument('--chunksize', default=10000,
					type=int, help='Chunk size', action='store')
parser.add_argument('--outTreeName', default='fullEB_BDT_Tree',
					type=str, help='Out tree name', action='store')

args = parser.parse_args()

from os import system
try:
	system('mkdir -p %s' % args.saveDir)
except OSError:
	print("\nCreation of results directory %s failed" % args.saveDir)
else:
	print("\nSuccessfully created directory %s " % args.saveDir)


import datetime
now = datetime.datetime.now()
logFileName = args.saveDir + '/trainWithTune_' + now.strftime("%Y_%m_%d_%H_%M_%S") + ".log"


import sys


class Logger(object):

	def __init__(self):
		self.terminal = sys.stdout
		self.log = open("%s" % logFileName, "a")

	def write(self, message):
		self.terminal.write(message)
		self.log.write(message)

	def flush(self):
		pass

sys.stdout = Logger()


print("************************************************************************************************************************************************\n")
now = datetime.datetime.now()
chunksize = args.chunksize
print(now.strftime("%Y-%m-%d %H:%M:%S"))
print("Starting photon ID training BDT\n")
print("inFilePath\t=\t" + args.inFilePath)
print("saveDir\t\t=\t" + args.saveDir)
print("inTreeName\t=\t" + args.inTreeName)
print("splitFile\t=\t" + args.splitFile)
print("chunksize\t=\t" + str(args.chunksize))
print("logFile\t\t=\t" + logFileName)


# using root_pandas - thanks to https://github.com/scikit-hep/root_pandas
from root_pandas_build.readwrite import read_root, to_root
import pandas as pd
from random import shuffle
import xgboost as xg
from random import randint
import random
import pickle
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib as mpl
from matplotlib import rcParams
from matplotlib import rc
import matplotlib.pyplot as plt
from custom_auc import aucW, sampleStats
from progressbar import ProgressBar

BDTfeats = ["phoR9Full5x5", "phoS4Full5x5", "phoEmaxOESCrFull5x5", "phoE2ndOESCrFull5x5", "phoE2ndOEmaxFull5x5", "phoE1x3OESCrFull5x5", "phoE2x5OESCrFull5x5", "phoE5x5OESCrFull5x5",
			"phoEmaxOE3x3Full5x5", "phoE2ndOE3x3Full5x5", "phoSigmaIEtaIEta", "phoSigmaIEtaIPhi", "phoSigmaIPhiIPhi", "phoSieieOSipipFull5x5", "phoEtaWidth", "phoPhiWidth", "phoEtaWOPhiWFull5x5"]
BDTfeats.sort()

params = {
			'objective': 'binary:logistic',
			'eta': 0.1,
			'eval_metric': 'auc',
			'booster': 'gbtree',
			'verbosity': 1,
			'nthread': -1,
			'gamma': 0.05,
			'max_depth': 22,
			'min_child_weight': 1.8,
			'subsample': 1.0,
			'colsample_bytree': 0.8,
			'alpha' : 0.0,
			'sampling_method': 'uniform',
			'tree_method': 'exact',
			'predictor': 'cpu_predictor'
		  }

print("Training with params:" + str(params))

phoModelIterated = None

pbar = ProgressBar()

iChunk = int(0)

for totalData in  pbar(read_root(paths=args.inFilePath, key=args.inTreeName, columns=(BDTfeats + ['PtEtaRwBG', 'xSecW', 'isSignal', 'isTrain', 'isValidation']), chunksize=chunksize)):
	print(str(len(totalData.index)) + "    " + len(dfSplit.index))

	print("\nTotal data:")
	totalData['bdtWeight'] = totalData['xSecW'] * totalData['PtEtaRwBG']
	sampleStats(totalData)

	print("\nTraining data:")
	trainDF = totalData[(totalData.isTrain == 1) & (totalData.isValidation == 0)]
	sampleStats(trainDF)

	print("\nValidation data:")
	validationDF = totalData[(totalData.isTrain == 1) & (totalData.isValidation == 1)]
	sampleStats(validationDF)

	print("\nTest data:")
	testDF = totalData[(totalData.isTrain == 0)]
	sampleStats(testDF)

	trainPho = xg.DMatrix(trainDF[BDTfeats].values, label=trainDF['isSignal'].values, weight=trainDF['bdtWeight'].values, feature_names=BDTfeats, nthread=-1)
	validationPho = xg.DMatrix(validationDF[BDTfeats].values, label=validationDF['isSignal'].values, weight=validationDF['bdtWeight'].values, feature_names=BDTfeats, nthread=-1)

	evallist = [(validationPho, 'validation'), (trainPho, 'train'), (testPho, 'test')]

	phoModel = xg.train(params, dtrain=trainPho, evals=[(validationPho, "validation")], evals_result=evallist, early_stopping_rounds=10, verbose_eval=True, num_boost_round=100000, xgb_model=phoModelIterated)

	del trainDF
	del validationDF
	del trainPho
	del validationPho

	trainDF = totalData[(totalData.isTrain == 1)]
	trainPho = xg.DMatrix(trainDF[BDTfeats].values, label=trainDF['isSignal'].values, weight=trainDF['bdtWeight'].values, feature_names=BDTfeats, nthread=-1)

	evallist = [(trainPho, 'train'), (testPho, 'test')]

	phoModelIterated = xg.train(params, dtrain=trainPho, evals_result=evallist,	num_boost_round=phoModel.best_iteration + 1, xgb_model=phoModelIterated)

	print('Chunk ' + str(iChunk) + 'processed!')

	if(iChunk == 1):
		break

	iChunk+=1


now = datetime.datetime.now()
print('\nTraining complete @ ' + now.strftime("%Y-%m-%d %H:%M:%S") + "\n")

pickle.dump(phoModelIterated, open('%s/aNTGC_photon_BDT.pkl' % args.saveDir, "wb"))
phoModelIterated.save_model('%s/aNTGC_photon_BDT.model' % args.saveDir)
phoModelIterated.dump_model(fout='%s/modelDump.txt' % args.saveDir)

print now.strftime("%Y-%m-%d %H:%M:%S") + '\nModel saved as %s/aNTGC_photon_BDT.(pkl/model/txt)' % args.saveDir

print "\nFeature importances (" + str(len(phoModel.get_fscore())) + " features) :"
# print phoModel.get_fscore().iteritems()
featImpDumpFile = open("%s/featImps.txt" % args.saveDir, "w")
fScoreList = phoModel.get_fscore()
fScoreList = sorted(fScoreList.items(), key=lambda item: item[1], reverse=True)
usedFeatures = list()

for iFeat in fScoreList:
	print "\t\t" + iFeat[0] + "\t->\t" + str(iFeat[1])
	featImpDumpFile.write(str(iFeat[0]) + ' , ' + str(iFeat[1]) + '\n')
	usedFeatures = usedFeatures + [str(iFeat[0])]


zeroImpFeats = list([str(x) for x in BDTfeats if x not in usedFeatures])
zeroImpFeats.sort()


for iFeat in zeroImpFeats:
	if iFeat is None:
		continue
	print "\t\t" + iFeat + "\t->\t0"
	featImpDumpFile.write(iFeat + ' , 0' + '\n')

featImpDumpFile.close()

print('\nGetting predictions @ ' + now.strftime("%Y-%m-%d %H:%M:%S") + "\n")

iChunk = int(0)

for totalData in  pbar(read_root(paths=args.inFilePath, key=args.inTreeName, columns=(BDTfeats + ['PtEtaRwBG', 'xSecW', 'isSignal', 'isTrain', 'isValidation', 'splitRand']), chunksize=chunksize)):
	print(str(len(totalData.index)) + "    " + len(dfSplit.index))

	print("\nTotal data:")
	totalData['bdtWeight'] = totalData['xSecW'] * totalData['PtEtaRwBG']
	sampleStats(totalData)

	allPho = xg.DMatrix(totalData[BDTfeats].values, label=totalData['isSignal'].values, weight=totalData['bdtWeight'].values, feature_names=BDTfeats, nthread=-1)

	saveDF = pd.DataFrame()
	saveDF['bdtScore'] = = phoModel.predict(allPho)

	saveDF['isSignalF'] = totalData['isSignal']
	saveDF['isTrainF'] = totalData['isTrain']
	saveDF['isValidationF'] = totalData['isValidation']
	saveDF['splitRand'] = totalData['splitRand']

	outFileName = args.saveDir + '/' + 'BDTresults_' + str(iChunk) + '.root'
	totalData.to_root('%s' % outFileName, key=args.outTreeName)
	print ('Data frame saved in %s)' % outFileName)

	if(iChunk == 1):
		break

	iChunk+=1


print("\n************************************************************************************************************************************************")
now = datetime.datetime.now()
print("Done @ " + now.strftime("%Y-%m-%d %H:%M:%S"))
print("************************************************************************************************************************************************")
