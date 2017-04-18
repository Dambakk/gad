### gad
# A novel approach to graphical app development

This is the bachelor thesis for Einar Johnsen and Christopher Dambakk, University of Agder, spring 2017.

**Tool usage documentation further down**

Motivation
==========

A significant portion of mobile applications (apps) that are being developed are in principle the same app. That is to say that the functionality and the graphical presentation is almost the same in every app, only the application of the functionality varies.

It is therefore rational to believe that systems can be developed that capitalizes on this fact, and indeed there are such efforts. Frameworks and application generators are a dime of dozen. However, they consitute a limiting and partial solution.

Introduction
============

Our solution will - given a idealized image of the graphical user interface (GUI) of an application - be able to create a sematic representation of that image. The generated representation should then be transpiled to an application project for a selected platform and eventually compile to a running application. This should be achieved using a series of tools that are scriptable, chainable and as interchangeable as possible.

Primary goals
=============

-   Create a simple, extendable definition for all common UI elements.

-   Create a command line interface (CLI) tool that reads png images and pairs any app design contained to a structured representation.

-   Create a CLI transpiler to a selected platform. (e.g. iOS, Android, HTML, etc).

-   Write documentation for tool usage.

-   Support different levels of output logging and offer reasonable error messages.


Secondary goals
===============

-   Create a tool that draws a representation of the semantic representation for the sake of manually being able to verify the structure that is being created.

-   Extend the solution to handle more than one target platform and as many UI elements as possible.

-   It should be possible to run the tool chain multiple times without destroying work that has been manually done. It should also be possible for the designer to update the drawings and add/change UI elements and add those to the project in a non destructive manner.

- Code that is generated should follow good naming conventions and avoid uninformative names, like label\_1 or textbox3 etc. This will require some sort of analysis or meta information solution.

Tertiary goals
==============

- Extend the image parser and transpilers to include application navigation flow.

- Extend the image parser to consider meta information. Examples of meta information could be contextual names (e.g. user name, phone number, etc) or composite or custom UI elements.

- Extend the tools to support user defined elements.

- Extend the transpiler to consider meta information such as API endpoints, namespaces and libraries.

- Recommend features and tools that can extend the tool chain.

- Extend the image parser to work directly on the designers sketch, without the designer marking the UI elements.

- Set the tool chain up as a private tap for use with the OS X package manager homebrew. 


### TODO: insert how-to-use instructions, etc

# Tool usage

Color codes and corresponding types
===============

| Color   	| HTML-tag 	| iOS-type 	| Android-type 	|
|---------	|----------	|----------	|--------------	|
| #15aaff 	| div    	| iOS-type 	| Java-type    	|
| #fb0007 	| p      	| iOS-type 	| Java-type    	|
| #ffff00 	| h1     	| iOS-type 	| Java-type    	|
| #008000 	| img    	| iOS-type 	| Java-type    	|

Edit the imageParser/colorTypes.ini file to add your own colors and corresponding elements to be generated.

**NB** There must be at least one white pixel between each element, unless the elements are nested.

The iOS code generator
===============
A short description here...

Running the generator:
-------------
To run the iOSGenerator open a console and enter the following:
`python3 PATH_TO_IOSGEN/iosgenerator.py PATH_TO_JSON PATH_TO_OUTPUT`
where
- `PATH_TO_IOSGEN` is the location of the iosgenerator on your computer.
- `PATH_TO_JSON` is the complete filepath to the JSON file containing the description of the view. This JSON file will typically be the output of the Image Parser-tool. E.g. `/home/username/documents/myFirstView.json`
- `PATH_TO_OUTPUT` is the path to desired place to put the created project or the path to the project to be updated. The last directory will be the folder containing the app and will be the name of the app. E.g. `/home/dev/apps/MyFirstApp` where MyFirstApp is the name of the app.

You can also add one or more of the following flags:
- `-v` for a more verbose output logging to the console.
- `-f` is the force flag to make the script continue even if it may cause unexpected behaviour and results. Without the flag, the program will stop and tell the user to add the flag if it encounter any problems.

The script will ask for input during runtime, such as enter a name for the view, select a view or commit changes using git.
For further help, use `--help` or `-h` when running the tool.