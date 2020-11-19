
from os.path import join, isfile
import json
from pyglossary.core import cacheDir

statusDir = join(cacheDir, "status")

class Status(object):
	@classmethod
	def load(cls, inputFilename: str, outputFilename: str) -> "Optional[Status]":
		_hash = hash(inputFilename, outputFilename)
		fpath = join(statusDir, f"{_hash}.json")
		if not isfile(fpath):
			return
		with open(fpath, mode="r", encoding="utf-8") as _file:
			data = json.load(_file)
		for key in (
			"inputFilename",
			"outputFilename",
			# TODO
		):
			if key not in data:
				log.error(f"invalid status file {fpath!r}: missing key {key!r}")
				return
		if data["inputFilename"] != inputFilename:
			log.error(f"invalid status file {fpath!r}: mismatch inputFilename")
			return
		if data["outputFilename"] != outputFilename:
			log.error(f"invalid status file {fpath!r}: mismatch outputFilename")
			return
		return cls(**data)

	def __init__(
		self,
		inputFilename: str,
		outputFilename: str,
		**kwargs
	):
		self.inputFilename = inputFilename
		self.outputFilename = outputFilename
		# TODO

	def save(self):
		# TODO

