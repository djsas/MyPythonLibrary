# -*- coding:utf-8 -*-
"""
cmd:    python 
import: 
input:  
output: 
description: 
"""

import os
import os.path
import sys

class Outputter:
	def __init__(self, outdir="output"):
		self.setOutDir(outdir)
		self.setSeparate("\t")
		self.__io = False
		self.clearStack
	def clearStack(self):
		self.__stack = []
	def close(self):
		self.__io.close()
	def getJoin(self, *nums):
		return self.__separate.join([str(s) for s in nums])
	def getJoinArray(self, a):
		a = [str(x) for x in a]
		return self.__separate.join(a)
	def getJoinStack(self):
		return self.getJoinArray(self.__stack)
	def getOutFilename(self, f):
		return "%s/%s" % (self.__outdir, f)
	def join(self, *nums):
		outstr = self.__separate.join([str(s) for s in nums])
		self.writeIn(outstr)
	def joinArray(self, a):
		self.writeIn(self.getJoinArray(a))
	def lenStack(self):
		return len(self.__stack)
	def open(self, f, authorized="w"):
		if self.__outdir:
			self.__io = open("%s/%s" % (self.__outdir, f), authorized)
		else:
			self.__io = open("%s" % f, authorized)
	def push(self, v):
		self.__stack.append(v)
	def setOutDir(self, outdir):
		self.__outdir = outdir
		if self.__outdir and not os.path.exists(self.__outdir):
			os.makedirs(self.__outdir)
	def setSeparate(self, s):
		self.__separate = s
	def write(self, s):
		self.__check()
		self.__io.write("%s" % s)
	def writeIn(self, s):
		self.__check()
		self.__io.write("%s\n" % s)
	def writeStack(self):
		self.joinArray(self.__stack)
	
	def __check(self):
		"""ファイルへの書き込み処理が実行された際に、書き込み先ファイルのセットがされているか確認。されていなければoutputディレクトリに出力設定する。"""
		if not self.__io:
			tmp = sys.argv[0].split("/")
			self.open(tmp.pop() + ".output")



# D.S.G.