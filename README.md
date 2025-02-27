Text editor for NES imagineering games, texts are compressed with Golomb 4 bits and this tool can handle that. Games mainly used:

- Barbie (USA).nes
- Home Alone 2 - Lost in New York (USA).nes
- Ren & Stimpy Show, The - Buckeroo$! (USA).nes
- Simpsons, The - Bart vs. the Space Mutants (USA).nes
- Simpsons, The - Bart vs. the World (USA).nes
- Simpsons, The - Bartman Meets Radioactive Man (USA).nes

Also the games listed used 2 bytes pointers, this tool formats the list of pointers automatically.

## Usage

Description:

```
Imagineering_golomb.py -d <romFile> <outFile> <tblFile>
Imagineering_golomb.py -c <outFile> <romFile> <tblFile>
Imagineering_golomb.py -v show version.
```

The program doesn't handle many exceptions, so try to provide the correct information to avoid issues. For more information, read the attached readme.txt.

### Instrutions

The attached files and instruccions are for Barbie (USA).nes, but you can change it, I recommend using my settings in file game_config.txt

First copy all files in the same directory of the ROM, use "extract text.bat", it will a file script.bin, Then edit the text and graphics use encode.tbl file. Once you're done, simply open "insert text.bat" and it will automatically insert the text.

## Frecuency Answer Questions

### Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me.
