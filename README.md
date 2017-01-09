### gad
# A novel approach to graphical app development

This is the bachelor thesis for Einar Johnsen and Christopher Dambakk, University of Agder, spring 2017.

Motivation
==========

A significant portion of mobile applications (apps) that are being developed are in principle the same app. That is to say that the functionality and the graphical presentation is almost the same in every app, only the application of the functionality varies.

It is therefore rational to believe that systems can be developed that capitalizes on this fact, and indeed there are such efforts. Frameworks and application generators are a dime of dozen. However, they consitute a limiting and partial solution.

Introduction
============

Our solution will - given a idealized image of the graphical user interface (GUI) of an application - be able to create a sematic representation of that image. The generated representation should then be transpiled to an application project for a selected platform and eventually compile to a running application. This should be achieved using a series of tools that are scriptable, chainable and as interchangeable as possible.

Primary goals
=============

-   Create a detailed project schedule with deliverables and demos.

-   Create a simple, extendable semantics for all common UI elements (e.g. a JSON structure)

-   Create a CLI (command line interface) tool that reads png images and pares any app design contained to a semantic representation.

-   Create a CLI transpiler to a selected platform. (e.g. iOs, Android, HTML, etc)

-   Write documentation for tool usage.

Each tool should offer different levels of logging output (silent, default, verbose) and offer reasonable error messages.

Code that is generated should follow good naming conventions and avoud uninformative names, like *label\_1* or *textbox3* etc. This will require some sort of analysis or meta information solution.

The tools must work primarly on OS X and Linux. Windows and other operating systems are not a priority.

Secondary goals
===============

-   Create a tool that draws a representation of the semantic representation for the sake of manually being able to verify the structure that is being created.

-   Extend the solution to handle more than one target platform and as many UI elements as possible.

-   The tool chain should be possible to run multiple times without destroying work that has been manually done. It should also be possible for the designer to update the drawings and add/change UI elements and add those to the project in a non destructive manner.

Tertiary goals
==============

-   Extend the image parser and transpilers to include application navigation flow.

-   Extend the image parser to consider meta information. Examples of meta information could be contextual names (e.g. user name, phone number, etc) or composite or custom UI elements.

-   Extend the transpiler to consider meta information such as API endpoints, namespaces and libraries.

-   Recommend features and tools that can extend the tool chain.

-   Extend the image parser to work directly on the designers sketch, without the designer marking the UI elements.

-   Set the tool chain up as a private tap for use with the OS X package manager homebrew.


### TODO: insert how-to-use instructions, etc

