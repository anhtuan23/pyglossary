# How to build Mdict

## Convert to `mdict html`

### Using `pyglossary`

#### Install `pyglossary`

- install `prompt_toolkit`

  pip install prompt_toolkit

- install `lxml`

  pip install lxml

- install `pyglossary` pre to avoid this issue https://github.com/ilius/pyglossary/issues/307

  pip install pyglossary --upgrade --pre

#### From CC-Cedict

- Download newest cedict from https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz

- Copy `cedict.txt.gz` file to `.\build_mdict\data\cc_cedict_original`

- Convert to `cc_cedict.mdict_html.txt` file

    py main.py .\build_mdict\data\cc_cedict_original\cedict.txt.gz .\build_mdict\data\cc_cedict_original\cc_cedict.mdict_html.txt --read-format=CC-CEDICT --write-format=OctopusMdictSource

- Use either [mdict-utils](#Using-mdict-utils) or [MdxBuilder](#Using-MdxBuilder) to build mdx file

#### From JMdict

- Download newest jmdict file from http://www.edrdg.org/jmdict/j_jmdict.html

- Copy `JMdict_e.gz` file to `.\build_mdict\data\jmdict_original`

- Convert to `jmdict.mdict_html.txt` file

    py main.py .\build_mdict\data\jmdict_original\JMdict_e.gz .\build_mdict\data\jmdict_original\jmdict.mdict_html.txt --read-format=JMDict --write-format=OctopusMdictSource

- Use either [mdict-utils](#Using-mdict-utils) or [MdxBuilder](#Using-MdxBuilder) to build mdx file

#### From generic `Stardict` file

- Using `WordNet_3_1_1` as source Stardict example, run command:

    py main.py build_mdict\data\WordNet_3_1_1_stardict\WordNet_3_1_1.ifo build_mdict\data\WordNet_3_1_1_stardict\WordNet_3_1_1.mdict_html.txt --read-format=Stardict --write-format=OctopusMdictSource

- Use either [mdict-utils](#Using-mdict-utils) or [MdxBuilder](#Using-MdxBuilder) to build mdx file

### Using `DecodeStarDict.class` to convert from `Stardict` to `mdict html`

- Convert `startdict` files to mdict html file

    java DecodeStarDict dict_name.idx dict_name.dict output_file.txt

- Use either [mdict-utils](#Using-mdict-utils) or [MdxBuilder](#Using-MdxBuilder) to build mdx file

---

## Build `mdx` file from `mdict html`

### Using mdict-utils

- Install `mdict-utils`

    pip install mdict-utils

- Create title and description

    echo [title] > title.txt && echo [description] > desc.txt

- Run pack command

    mdict --title title.txt --description desc.txt -a mdict_html.txt dict.mdx

### Using MdxBuilder

> **\*Note**: MdxBuilder version 2 and 3 build mdx file version 1.2, while MdxBuilder version 4 build mdx file version 3. Both are uncompatible with apps that can only read mdx filer version 2\*

- Original format : `Mdict(Html)`
- Encoding : `UTF-8(Unicode)`
- Title : `[Name]`
- Description : `Built on [current_date]`

  <img src="https://github.com/anhtuan23/pyglossary/raw/build_mdict/build_mdict/MdxBuilder_screenshot.png" width="80%"/>