#!/usr/bin/env python3

OUTPUT_MODE_BUFFER = 0
OUTPUT_MODE_STDOUT = 1
OUTPUT_MODE_FILE = 2

class HtmlOutput:
        
    def __init__(self, fieldOrder):
        self.outputMode = None
        self.outputFile = None
        self.fieldOrder = fieldOrder
        self.writeHtmlShell = True
        self.headerWritten = False
        self.lines = []
        
    def setFile(self, outputFile):
        self.outputFile = outputFile
        self.outputMode = OUTPUT_MODE_FILE
        self.writeHtmlShell = True
        self.headerWritten = False
        self.lines = []

    def writeLine(self, line, indent=0):
        line = ' ' * 4 * indent + line
        if self.outputMode == OUTPUT_MODE_BUFFER:
            self.lines.append(line)
        elif self.outputMode == OUTPUT_MODE_FILE:
            self.outputFile.write("%s\n" % line)
        else:
            print(line)
            
    def writeRow(self, row, isHeader=False):
        
        self.writeLine('<tr>')

        for key in self.fieldOrder:
            if isHeader:
                self.writeLine('<th>%s</th>' % key, 1)
            else:
                self.writeLine('<td>%s</td>' % str(row.get(key, None)), 1)
            
        self.writeLine('</tr>')

    def writeHeader(self):
        if self.writeHtmlShell:
            self.writeLine('<html>')
            self.writeLine('<body>')
        self.writeLine('<table border="2">')
        self.writeRow(self.fieldOrder, True)
        
    def write(self, record):
        if not self.headerWritten:
            self.writeHeader()
            self.headerWritten = True
        self.writeRow(record)
        
    def finish(self):
        self.writeLine('</table>')
        if self.writeHtmlShell:
            self.writeLine('</body>')
            self.writeLine('</html>')

