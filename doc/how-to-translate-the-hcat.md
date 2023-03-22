# What is a `po` file?
A `po` file is a file format for software localization defined by the GNU gettext tool. Gettext is an open-source tool designed to simplify the localization process by allowing you to extract translatable strings from your source code into a `po` file for translation. The `po` file contains a list of key-value pairs that define how string keys map to their translations for the target language.

# How can I translate a `po` file?
## Creating a new `po` file
The first step is to create a new `po` file. The file name should be `zh_CN.po`. We have already created the `pot` file for you, which you can use to create a new `po` file. However, we recommend that you create the file using the following command:

```shell
python tools/lang_tool/gen_msg_po.py
```

After entering the language code, the tool will create a new `po` file for you.

## Translating the `po` file
You can use any tool to translate the `po` file, but we recommend using [PoEditor](https://localise.biz/free/poeditor) or [Poedit](https://poedit.net/).

## Compiling the `po` file
After translating the `po` file, you need to compile it into an `mo` file. Use the following command:

```shell
python tools/lang_tool/po2mo.py
```

After entering the language code, the tool will compile the `po` file into an `mo` file.

## Updating the `po` file
If you want to update the `po` file, you can use the `pot` file to update it using the following command:

```shell
python tools/lang_tool/update_po.py
```

# Additional Information
If you want to translate the `po` file, you need to understand the `po` file format. You can read more about the [po file format](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) to learn more.

For further information, see [PO file (Gettext)](https://localizely.com/po-file/).