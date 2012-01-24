# -*- coding: utf-8 -*-
# $Id$

import commands
import os
import os.path
import random
import re
import sgmllib
import string
import zenhan

class PreProcessor:
	def __init__(self, tmpdir="tmp", cabochapath="cabocha", chasenrc=""):
		"""コンストラクタ
		@param string tmpdir NKFやCaboChaの実行時に、一時ファイルを作成するディレクトリ"""
		self.tmpdir = tmpdir
		self.__cabochapath = cabochapath
		self.__chasenrc = chasenrc
	def cabocha(self, text):
		"""引数に渡されたテキストを解析し、その係り受け解析結果(CaboChaの出力結果)を返す。
		@param string text 係り受け解析を実行するテキスト。UTF-8にしてあること。
		@param string tmpdir 解析対象の文字列を一時ファイルに格納するために、そのファイルを生成するディレクトリ
		@return string 解析結果"""
		tmpfile1 = "%s/cabocha1.%s.txt" % (self.tmpdir, self.__randstr(25))
		tmpfile2 = "%s/cabocha2.%s.txt" % (self.tmpdir, self.__randstr(25))
		io = open(tmpfile1, "w")
		io.write(text)
		io.close()
		
		os.system("nkf -e --overwrite " + tmpfile1)
		if self.__chasenrc:
			os.system("%s -f1 -c %s %s > %s" % (self.__cabochapath, self.__chasenrc, tmpfile1, tmpfile2))
		else:
			os.system("%s -f1 %s > %s" % (self.__cabochapath, tmpfile1, tmpfile2))
		os.system("nkf -w --overwrite " + tmpfile2)
		
		io = open(tmpfile2)
		text = io.read()
		io.close()
		
		os.remove(tmpfile1)
		os.remove(tmpfile2)
		
		return text

		#tmpfile = "%s/cabocha.txt" % self.tmpdir
		#io = open(tmpfile, "w")
		#io.write(self.conv(text, "euc-jp"))
		#io.close()
		#text = commands.getoutput("cabocha -f1 %s" % tmpfile)
		#return self.conv(text, "utf-8")
	def guess_charset(self, data):
		"""文字列の文字コードを自動取得する。
		@param string data 文字コードを取得したい文字列
		@return string 文字コード"""
		f = lambda d, enc: d.decode(enc) and enc
		lookup = ('utf_8', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'shift_jis', 'shift_jis_2004','shift_jisx0213', 'iso2022jp', 'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_3', 'iso2022_jp_ext','latin_1', 'ascii')
		for e in lookup:
			try: return f(data, e)
			except: pass
		return None
	def conv(self, data, encoding="utf-8"):
		"""文字列の文字コードを変換する。
		@param string data 変換対象の文字列
		@param string encoding 変換後の文字コード(デフォルト値はUTF-8)
		@return string 変換後の文字列"""
		charset = self.guess_charset(data)
		u = data.decode(charset)
		return u.encode(encoding)
	def h2z(self, text):
		"""文字列中の半角文字を全て全角文字に変換する。
		@param string text 変換対象の文字列
		@return string 変換結果"""
		return zenhan.h2z(unicode(text, "utf-8")).encode("utf-8")  #convert hankaku into zenkaku
	def nkf(self, text, opt="-w"):
		"""LinuxコマンドのNKFを呼び出して、文字コードを変換する。
		@param string text 文字コード変換を実行するテキスト
		@param string opt NKFコマンドの文字コード指定に関するオプション
		@param string tmpdir 変換対象の文字列を一時ファイルに格納するために、そのファイルを生成するディレクトリ
		@return string 変換結果"""
		tmpfile = "%s/nkf.%s.txt" % (self.tmpdir, self.__randstr(25))
		io = open(tmpfile, "w")
		io.write(text)
		io.close()
		res = commands.getoutput("nkf %s %s" % (opt, tmpfile))
		os.remove(tmpfile)
		return res
	def reviseHTML(self, text):
		"""HTMLソースを解析し、適切な箇所に改行を挿入しなおすと共にHTMLタグを除去する。
		@param string text HTMLソース
		@return string 修正結果の文字列"""
		
		#step1: 改行、タブを全て除去する
		text = re.sub("\t", "", text)
		text = re.sub("\r\n", "", text)
		text = re.sub("\r", "", text)
		text = re.sub("\n", "", text)

		#step2: <title><tr><td><div><p><h1>～<h6>の終端と、<br>タグの次の位置に改行を挿入
		ptn = re.compile("<\/title>", re.IGNORECASE)
		text = ptn.sub("</title>\n", text)
		ptn = re.compile("<\/tr>", re.IGNORECASE)
		text = ptn.sub("</tr>\n", text)
		ptn = re.compile("<\/td>", re.IGNORECASE)
		text = ptn.sub("</td>\n", text)
		ptn = re.compile("<\/div>", re.IGNORECASE)
		text = ptn.sub("</div>\n", text)
		ptn = re.compile("<\/p>", re.IGNORECASE)
		text = ptn.sub("</p>\n", text)
		ptn = re.compile("<\/h1>", re.IGNORECASE)
		text = ptn.sub("</h1>\n", text)
		ptn = re.compile("<\/h2>", re.IGNORECASE)
		text = ptn.sub("</h2>\n", text)
		ptn = re.compile("<\/h3>", re.IGNORECASE)
		text = ptn.sub("</h3>\n", text)
		ptn = re.compile("<\/h4>", re.IGNORECASE)
		text = ptn.sub("</h4>\n", text)
		ptn = re.compile("<\/h5>", re.IGNORECASE)
		text = ptn.sub("</h5>\n", text)
		ptn = re.compile("<\/h6>", re.IGNORECASE)
		text = ptn.sub("</h6>\n", text)

		#step3: htmlタグを全て除去
		htmltag = re.compile(r'<.*?>', re.I | re.S)
		text = htmltag.sub('', text)
		#step4: 全角空白を半角空白にする
		text = re.sub("　", " ", text)  
		#step5: 2つ以上連続する半角空白を1つにする
		text = re.sub(" +", " ", text)  
		#step7: 2つ以上連続する半角ピリオドを全角ピリオド1つに置換する
		text = re.sub("\.{2,}", "．", text)
		#step8: 非英数字の直後の半角ピリオドを全角ピリオドに置換する
		ptn = re.compile("(?<![0-9])\.")
		text = ptn.sub("．", text)
		#step9: 句点および全角ピリオドの直後に、改行を挿入する
		text = re.sub("。", "。\n", text)
		text = re.sub("．", "．\n", text) 
		#step6: 2つ以上連続する改行を1つにする
		text = re.sub("\n+", "\n", text)  

		return text
	def sanitize(self, str):
		"""文字列中のヌルバイトを標準的な半角スペースに置換する。
		@param string str サニタイズしたい文字列
		@return string サニタイズした結果"""
		return re.sub(chr(0), " ", str)
	
	def __randstr(self, n):
		"""ランダムな文字配列の文字列を生成する。
		@param int n 文字列の長さ
		@return string 生成された文字列"""
		alphabets = string.digits + string.letters
		return ''.join(random.choice(alphabets) for i in xrange(n))
		


class Stripper(sgmllib.SGMLParser):
	def __init__(self):
		sgmllib.SGMLParser.__init__(self)
	def strip(self, some_html):
		self.theString = ""
		self.feed(some_html)
		self.close()
		return self.theString
	def handle_data(self, data):
		self.theString += data

