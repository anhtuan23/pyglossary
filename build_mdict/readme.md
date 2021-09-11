# How to build Mdict

## Using `pyglossary`

### Install `pyglossary`

- install `prompt_toolkit`

  pip install prompt_toolkit

- install `lxml`

  pip install lxml

- install `pyglossary` pre to avoid this issue https://github.com/ilius/pyglossary/issues/307

  pip install pyglossary --upgrade --pre

### From CC-Cedict

- Download newest cedict from https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz

- Copy `cedict.txt.gz` file to `.\build_mdict\data\cc_cedict_original`

- Convert to `cc_cedict.mdict_html.txt` file

  py main.py build_mdict\data\cc_cedict_original\cedict.txt.gz build_mdict\data\cc_cedict_original\cc_cedict.mdict_html.txt --read-format=CC-CEDICT --write-format=OctopusMdictSource

- Use MdxBuilder to build `mdx` file. (_Note: MdxBuilder ver 4.0 built file is not compatible with most reader, should use lower version._)

  - Original format == `Mdict(Html)`
  - Encoding == `UTF-8(Unicode)`
  - Title == `CC-Cedict`
  - Description == `Built on [current_date]`

    <img src="https://raw.githubusercontent.com/wiki/ilius/pyglossary/screenshots/40a-gtk-txt-stardict-aryanpour-dark.png" width="50%" height="50%"/>

### From JMdict

- Download newest jmdict file from http://www.edrdg.org/jmdict/j_jmdict.html

- Copy `JMdict_e.gz` file to `.\build_mdict\data\jmdict_original`

- Convert to `jmdict.mdict_html.txt` file

  py main.py build_mdict\data\jmdict_original\JMdict_e.gz build_mdict\data\jmdict_original\jmdict.mdict_html.txt --read-format=JMDict --write-format=OctopusMdictSource

- Use MdxBuilder to build `mdx` file. (_Note: MdxBuilder ver 4.0 built file is not compatible with most reader, should use lower version._)

  - Original format == `Mdict(Html)`
  - Encoding == `UTF-8(Unicode)`
  - Title == `JM-Dict`
  - Description == `Built on [current_date]`

## Using `DecodeStarDict.class`

- Convert `startdict` files to mdict html file

  java DecodeStarDict dict_name.idx dict_name.dict output_file.txt

- Build with MdxBuilder like steps above
