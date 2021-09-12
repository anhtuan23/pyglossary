import re
import os
from .pinyin import convert
from .summarize import summarize
from pyglossary.plugins.formats_common import pip, log

line_reg = re.compile(r"^([^ ]+) ([^ ]+) \[([^\]]+)\] /(.+)/$")

script_dir = os.path.dirname(__file__)

COLORS = {
	"": "black",
	"1": "red",
	"2": "orange",
	"3": "green",
	"4": "blue",
	"5": "black",
}

# Use this to resolve mismatch between syllable length and tone length
CUSTOM_TONES = {
	"21三体综合症": ['4', '1', '1', '3', '1', '2', '4'],
	"21三體綜合症": ['4', '1', '1', '3', '1', '2', '4'],
	"PO": ['1', '1'],
	"PO文": ['1', '1', '2'],
	"TA": ['1', '1'],
	"美国51区": ['3', '2', '3', '1', '1'],
	"美國51區": ['3', '2', '3', '1', '1'],
}


def parse_line(line):
	line = line.strip()
	match = line_reg.match(line)
	if match is None:
		return None
	trad, simp, pinyin, eng = match.groups()
	pinyin = pinyin.replace("u:", "v")
	eng = eng.split("/")
	return trad, simp, pinyin, eng


def make_entry(trad, simp, pinyin, eng):
	eng_names = list(map(summarize, eng))
	names = [simp, trad, pinyin] + eng_names
	article = render_article(trad, simp, pinyin, eng)
	return names, article


def colorize(hf, syllables, tones):
    # try to fix mismatch length between syllable and tone with CUSTOM_TONES
	if len(syllables) != len(tones):
		tones = CUSTOM_TONES.get(syllables, tones)
  
	if len(syllables) != len(tones):
		log.warn(f"unmatched tones: syllables={syllables!r}, tones={tones}")
		with hf.element("div", style="display: inline-block"):
			for syllable in syllables:
				with hf.element("font", color=""):
					hf.write(syllable)
		return

	with hf.element("div", style="display: inline-block"):
		for syllable, tone in zip(syllables, tones):
			with hf.element("font", color=COLORS[tone]):
				hf.write(f'{syllable} ')


def render_article(trad, simp, pinyin, eng):
	from lxml import etree as ET
	from io import BytesIO

	# pinyin_tones = [convert(syl) for syl in pinyin.split()]
	pinyin_list = []
	tones = []
	for syllable in pinyin.split():
		nice_syllable, tone = convert(syllable)
		pinyin_list.append(nice_syllable)
		tones.append(tone)

	f = BytesIO()
	with ET.htmlfile(f, encoding="utf-8") as hf:
		with hf.element("div", style="border: 1px solid; padding: 5px"):
			with hf.element("div"):
				with hf.element("big"):
					colorize(hf, simp, tones)
				if trad != simp:
					hf.write("\xa0/\xa0")  # "\xa0" --> "&#160;" == "&nbsp;"
					colorize(hf, trad, tones)
				hf.write(ET.Element("br"))
				with hf.element("big"):
					colorize(hf, pinyin_list, tones)

			with hf.element("div"):
				with hf.element("ul"):
					for defn in eng:
						with hf.element("li"):
							hf.write(defn)

	article = f.getvalue().decode("utf-8")
	return article
