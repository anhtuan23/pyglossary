# -*- coding: utf-8 -*-
import re
from tempfile import mktemp
import shutil
import os
from os.path import (
	join,
	exists,
	dirname,
	getsize,
)
from typing import (
	Optional,
	Tuple,
	List,
	Dict,
	Callable,
	Any,
)

from .entry_base import BaseEntry, MultiStr, RawEntryType
from .iter_utils import unique_everseen

from pickle import dumps, loads
from zlib import compress, decompress

import logging
log = logging.getLogger("root")


# or Resource?
class DataEntry(BaseEntry):
	def isData(self) -> bool:
		return True

	def __init__(self, fname: str, data: bytes, inTmp: bool = False) -> None:
		assert isinstance(fname, str)
		assert isinstance(data, bytes)
		assert isinstance(inTmp, bool)

		if inTmp:
			tmpPath = mktemp(prefix=fname + "_")
			with open(tmpPath, "wb") as toFile:
				toFile.write(data)
			data = ""
		else:
			tmpPath = None

		self._fname = fname
		self._data = data  # bytes instance
		self._tmpPath = tmpPath

	def getFileName(self) -> str:
		return self._fname

	def getData(self) -> bytes:
		if self._tmpPath:
			with open(self._tmpPath, "rb") as fromFile:
				return fromFile.read()
		else:
			return self._data

	def size(self):
		if self._tmpPath:
			return getsize(self._tmpPath)
		else:
			return len(self._data)

	def save(self, directory: str) -> str:
		fname = self._fname
		# fix filename depending on operating system? FIXME
		fpath = join(directory, fname)
		fdir = dirname(fpath)
		if not exists(fdir):
			os.makedirs(fdir)
		if self._tmpPath:
			shutil.move(self._tmpPath, fpath)
			self._tmpPath = fpath
		else:
			with open(fpath, "wb") as toFile:
				toFile.write(self._data)
		return fpath

	@property
	def word(self) -> str:
		return self._fname

	@property
	def words(self) -> List[str]:
		return [self._fname]

	@property
	def defi(self) -> str:
		return f"File: {self._fname}"

	@property
	def defis(self) -> List[str]:
		return [self.defi]

	def getWord(self) -> str:
		log.error("entry.getWord() is deprecated, use entry.word")
		return self.word

	def getWords(self) -> List[str]:
		log.error("entry.getWords() is deprecated, use entry.words")
		return self.words

	def getDefi(self) -> str:
		log.error("entry.getDefi() is deprecated, use entry.defi")
		return self.defi

	def getDefis(self) -> List[str]:
		log.error("entry.getDefis() is deprecated, use entry.defis")
		return self.defis

	@property
	def defiFormat(self) -> 'Literal["b"]':
		return "b"

	@defiFormat.setter
	def setDefiFormat(self, defiFormat):
		pass

	def detectDefiFormat(self) -> None:
		pass

	def addAlt(self, alt: str) -> None:
		pass

	def editFuncWord(self, func: Callable[[str], str]) -> None:
		pass
		# modify fname?
		# FIXME

	def editFuncDefi(self, func: Callable[[str], str]) -> None:
		pass

	def strip(self) -> None:
		pass

	def replaceInWord(self, source: str, target: str) -> None:
		pass

	def replaceInDefi(self, source: str, target: str) -> None:
		pass

	def replace(self, source: str, target: str) -> None:
		pass

	def removeEmptyAndDuplicateAltWords(self):
		pass

	def getRaw(self, glos: "GlossaryType") -> RawEntryType:
		b_fpath = b""
		if glos.tmpDataDir:
			b_fpath = self.save(glos.tmpDataDir).encode("utf-8")
		tpl = (
			self._fname.encode("utf-8"),
			b_fpath,
			"b",
		)
		if glos._rawEntryCompress:
			return compress(dumps(tpl), level=9)
		return tpl

	@classmethod
	def fromFile(cls, glos, word, fpath):
		entry = DataEntry(word, b"")
		entry._tmpPath = fpath
		return entry


class Entry(BaseEntry):
	sep = "|"
	htmlPattern = re.compile(
		".*(?:" + "|".join([
			r"<font[ >]",
			r"<br\s*/?\s*>",
			r"<i[ >]",
			r"<b[ >]",
			r"<p[ >]",
			r"<hr\s*/?\s*>",
			r"<a href=",
			r"<div[ >]",
			r"<span[ >]",
			r"<img[ >]",
			r"<table[ >]",
			r"<sup[ >]",
			r"<u[ >]",
			r"<ul[ >]",
			r"<ol[ >]",
			r"<li[ >]",
		]) + ")",
		re.S,
	)

	def isData(self) -> bool:
		return False

	def _join(self, parts: List[str]) -> str:
		return self.sep.join([
			part.replace(self.sep, "\\" + self.sep)
			for part in parts
		])

	@staticmethod
	def defaultSortKey(b_word: bytes) -> Any:
		return b_word.lower()

	@staticmethod
	def getEntrySortKey(
		key: Optional[Callable[[bytes], Any]] = None,
	) -> Callable[[BaseEntry], Any]:
		if key is None:
			key = Entry.defaultSortKey
		return lambda entry: key(entry.words[0].encode("utf-8"))

	@staticmethod
	def getRawEntrySortKey(
		key: Optional[Callable[[bytes], Any]] = None,
	) -> Callable[[Tuple], Any]:
		# here `x` is raw entity, meaning a tuple of form (word, defi) or
		# (word, defi, defiFormat)
		# so x[0] is word(s) in bytes, that can be a str (one word),
		# or a list or tuple (one word with or more alternaties)
		if key is None:
			key = Entry.defaultSortKey
		return lambda x: key(loads(decompress(x))[0])

	def __init__(
		self,
		word: MultiStr,
		defi: MultiStr,
		defiFormat: str = "m",
		byteProgress: Optional[Tuple[int, int]] = None,
	) -> None:
		"""
			word: string or a list of strings (including alternate words)
			defi: string or a list of strings (including alternate definitions)
			defiFormat (optional): definition format:
				"m": plain text
				"h": html
				"x": xdxf
		"""

		# memory optimization:
		if isinstance(word, list):
			if len(word) == 1:
				word = word[0]
		elif not isinstance(word, str):
			raise TypeError(f"invalid word type {type(word)}")

		if isinstance(defi, list):
			if len(defi) == 1:
				defi = defi[0]
		elif not isinstance(defi, str):
			raise TypeError(f"invalid defi type {type(defi)}")

		if defiFormat not in ("m", "h", "x"):
			raise ValueError(f"invalid defiFormat {defiFormat!r}")

		self._word = word
		self._defi = defi
		self._defiFormat = defiFormat
		self._byteProgress = byteProgress  # Optional[Tuple[int, int]]


	@property
	def word(self):
		"""
			returns string of word,
				and all the alternate words
				seperated by "|"
		"""
		if isinstance(self._word, str):
			return self._word
		else:
			return self._join(self._word)

	@property
	def words(self) -> List[str]:
		"""
			returns list of the word and all the alternate words
		"""
		if isinstance(self._word, str):
			return [self._word]
		else:
			return self._word

	@property
	def defi(self) -> str:
		"""
			returns string of definition,
				and all the alternate definitions
				seperated by "|"
		"""
		if isinstance(self._defi, str):
			return self._defi
		else:
			return self._join(self._defi)

	@property
	def defis(self) -> List[str]:
		"""
			returns list of the definition and all the alternate definitions
		"""
		if isinstance(self._defi, str):
			return [self._defi]
		else:
			return self._defi

	def getWord(self) -> str:
		log.error("entry.getWord() is deprecated, use entry.word")
		return self.word

	def getWords(self) -> List[str]:
		log.error("entry.getWords() is deprecated, use entry.words")
		return self.words

	def getDefi(self) -> str:
		log.error("entry.getDefi() is deprecated, use entry.defi")
		return self.defi

	def getDefis(self) -> List[str]:
		log.error("entry.getDefis() is deprecated, use entry.defis")
		return self.defis

	@property
	def defiFormat(self) -> str:
		"""
			returns definition format:
				"m": plain text
				"h": html
				"x": xdxf
		"""
		# TODO: type: Literal["m", "h", "x"]
		return self._defiFormat

	@defiFormat.setter
	def setDefiFormat(self, defiFormat) -> str:
		"""
			defiFormat:
				"m": plain text
				"h": html
				"x": xdxf
		"""
		self._defiFormat = defiFormat

	def detectDefiFormat(self) -> None:
		if self._defiFormat != "m":
			return
		defi = self.defi.lower()
		if self.htmlPattern.match(defi):
			self._defiFormat = "h"

	def byteProgress(self):
		return self._byteProgress

	def addAlt(self, alt: str) -> None:
		words = self.words
		words.append(alt)
		self._word = words

	def editFuncWord(self, func: Callable[[str], str]) -> None:
		"""
			run function `func` on all the words
			`func` must accept only one string as argument
			and return the modified string
		"""
		if isinstance(self._word, str):
			self._word = func(self._word)
		else:
			self._word = tuple(
				func(st) for st in self._word
			)

	def editFuncDefi(self, func: Callable[[str], str]) -> None:
		"""
			run function `func` on all the definitions
			`func` must accept only one string as argument
			and return the modified string
		"""
		if isinstance(self._defi, str):
			self._defi = func(self._defi)
		else:
			self._defi = tuple(
				func(st) for st in self._defi
			)

	def _stripTrailingBR(self, s: str) -> str:
		while s.endswith('<BR>') or s.endswith('<br>'):
			s = s[:-4]
		return s

	def strip(self) -> None:
		"""
			strip whitespaces from all words and definitions
		"""
		self.editFuncWord(str.strip)
		self.editFuncDefi(str.strip)
		self.editFuncDefi(self._stripTrailingBR)

	def replaceInWord(self, source: str, target: str) -> None:
		"""
			replace string `source` with `target` in all words
		"""
		if isinstance(self._word, str):
			self._word = self._word.replace(source, target)
		else:
			self._word = tuple(
				st.replace(source, target) for st in self._word
			)

	def replaceInDefi(self, source: str, target: str) -> None:
		"""
			replace string `source` with `target` in all definitions
		"""
		if isinstance(self._defi, str):
			self._defi = self._defi.replace(source, target)
		else:
			self._defi = tuple(
				st.replace(source, target) for st in self._defi
			)

	def replace(self, source: str, target: str) -> None:
		"""
			replace string `source` with `target` in all words and definitions
		"""
		self.replaceInWord(source, target)
		self.replaceInDefi(source, target)

	def removeEmptyAndDuplicateAltWords(self):
		words = self.words
		if len(words) == 1:
			return
		words = [word for word in words if word]
		words = list(unique_everseen(words))
		self._word = words

	def getRaw(
		self,
		glos: "GlossaryType",
	) -> RawEntryType:
		"""
			returns a tuple (word, defi) or (word, defi, defiFormat)
			where both word and defi might be string or list of strings
		"""
		if self._defiFormat and self._defiFormat != glos.getDefaultDefiFormat():
			tpl = (
				self.word.encode("utf-8"),
				self.defi.encode("utf-8"),
				self._defiFormat,
			)
		else:
			tpl = (
				self.word.encode("utf-8"),
				self.defi.encode("utf-8"),
			)

		if glos._rawEntryCompress:
			return compress(dumps(tpl), level=9)

		return tpl

	@classmethod
	def fromRaw(
		cls,
		glos: "GlossaryType",
		rawEntry: RawEntryType,
		defaultDefiFormat: str = "m",
	):
		"""
			rawEntry can be (word, defi) or (word, defi, defiFormat)
			where both word and defi can be string or list of strings
			if defiFormat is missing, defaultDefiFormat will be used

			creates and return an Entry object from `rawEntry` tuple
		"""
		if isinstance(rawEntry, bytes):
			rawEntry = loads(decompress(rawEntry))
		word = rawEntry[0].decode("utf-8")
		defi = rawEntry[1].decode("utf-8")
		if len(rawEntry) > 2:
			defiFormat = rawEntry[2]
			if defiFormat == "b":
				return DataEntry.fromFile(glos, word, defi)
		else:
			defiFormat = defaultDefiFormat

		if glos.getPref("enable_alts", True):
			word = word.split(cls.sep)
			defi = defi.split(cls.sep)

		return cls(
			word,
			defi,
			defiFormat=defiFormat,
		)
