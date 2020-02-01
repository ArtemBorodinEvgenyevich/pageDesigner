# PageDesigner
Simple application for editing one page documents.

## Features
- Printing to *.pdf files or to external divices
- Adding images
- Scalable frames with different pen styles
- Snap to grid tool
- **Rich Text** support for text edit 
- Simple Code editor for code snippets 


You will see a tutorial on a start up. Please read through carefully. 
Here is a rough introduction.


## Usage
App working area is a rectangle which represents an A4 format paper. A grey outline is presented to specify the ident from
the paper border. Notice, that it will not be rendered in a final image when printing.

When click on graphics, item you will see item properties in a Property widget. Youl see grid properties if snap to grid enabled.

## Graphics elements:

##### Text:
A text element. Don nott place a whole text in there. The main purpose of it is to provide a small text snippet.
Text editor also allows you to create tables, data stamps, super/subscript text. 
You can use text or regex patterns to find text. 
Double click for editing.

##### Box:
A frame element with different drawing styles. Use it to make a frame for text element.

##### Image:
A pixmap item. Supports popular formats like: **.bmp**, **.jpg**, **.png**.

#### Working pipeline :
1. Place graphics elements: frames, images and text elements around the working area
2. Save
3. Print
4. Enjoy


## BUGS
1. Broken grid snapping if start new project if grid enabled.
2. Frame item is out of QGraphicsItem bounding box at line size 5. Causes display artifacts when dragging element.


## License
Licensed under GNU General Public License v2.0
