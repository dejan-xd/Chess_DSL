# Chess_DSL
Domain Specific Language (DSL) used for playing chess. <br>
https://test.pypi.org/project/ChessDSL/

## Idea
The idea is to create a DSL with rules for internationalization/localization so that game commands can be adapted to natural language. <br>
Rules for internationalization/localization are interpreted during the game and command parsing is enabled.

The localization rules themselves are configured while playing a game of chess where the user enters commands in the desired language. <br>
This kind of DSL is able to interpret the moves entered through the console based on the configuration and to recognize the specific symbols of the given language. (eg ч, ш, ü, é, etc.).

### Commands
Move commands follow the formula: <b>'figure name' 'to field'</b>. If two or more of the same figures can be moved to the same field, it is necessary to add the <b>'from the field'</b> parameter in between.
Exceptions are handler commands that consist only of the command name.

Example commands:
- pawn e4,
- horse f3,
- rook h1 d1 (for example rook a1 can be moved to field d1),
- cancel,
- new game,
- undo etc.

### The languages implemented in the project are:
- Serbian,
- English,
- Spanish,
- German, and
- French

Regarding the translation of commands and pieces into other languages, Chess Wikipedia is used so that there are as many correct names of pieces as possible. <br>
For other needs, Google Translate has done its part. At least we hope so 🙂.


## Starting Chess_DSL
* open cmd and type the command:
  - pip install -i https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/ ChessDSL
* once the package is installed, launch the game with the command:
  - chess-dsl-cli

*installation of this package is possible on a computer or in a virtual machine
