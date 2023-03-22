# What is the `po` file?
>PO (an acronym for “portable object”) is a file format for [software localization](https://localizely.com/localization-workflow/) defined by the [GNU gettext](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) tool. Gettext is an open-source tool designed to simplify the localization process. It allows you to extract translatable strings from your source code into a PO file for translation. 
>The PO file contains a list of key-value pairs that define how string keys map to their translations for the target language.

# How can I translate the `po` file?
## Create a new `po` file
The first thing you need to do is to create a new `po` file. The file name should be `zh_CN.po`.
We already create the `pot` file for you. You can use the `pot` file to create a new `po` file.
But I recommend you create the file by the tool.

Create a new `po` file by the tool:
```shell
python tools/lang_tool/gen_msg_po.py
```
After you enter the language code, the tool will create a new `po` file for you.

## Translate the `po` file
You can use any tool to translate the `po` file. I recommend you use [this tool](https://localise.biz/free/poeditor).

And...`Github Copilot` recommend you use [Poedit](https://poedit.net/).(XD)

## Compile the `po` file
After you translate the `po` file, you need to compile the `po` file to `mo` file.
```shell
python tools/lang_tool/po2mo.py
```
After you enter the language code, the tool will compile the `po` file to `mo` file.

## How can I update the `po` file?
If you want to update the `po` file, you can use the `pot` file to update the `po` file.
```shell
python tools/lang_tool/update_po.py
```

# Information
>**Note:** If you want to translate the `po` file, you need to know the `po` file format. You can read the [po file format](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) to learn more.

- [PO file (Gettext)](https://localizely.com/po-file/)