#!/usr/bin/env python3
#
# fix_techlefB ---
#
# This script adds the missing statement "USEMINSPACING OBS OFF" from
# the technology LEF files for Sky130.
#
# This script also replaces the plate and fringing capacitance values for
# route layers from metal2 to metal5 based on the ReRAM stackup (sky130B).
#
# This script is a filter to be run by setting the name of this script as
# the value to "filter=" for the model install in the sky130 Makefile for
# variant sky130B.

import re
import os
import sys

def filter(inname, outname):

    # Read input
    try:
        with open(inname, 'r') as inFile:
            ltext = inFile.read()
            llines = ltext.splitlines()
    except:
        print('fix_techlefB.py: failed to open ' + inname + ' for reading.', file=sys.stderr)
        return 1

    # These edge capacitance values get modified
    edgevalues =   [['37.759E-6', '32.918E-6'],
		    ['40.989E-6', '37.065E-6'],
		    ['36.676E-6', '34.169E-6'],
		    ['38.851E-6', '36.828E-6']]

    # These plate capacitance values get modified
    platevalues =  [['16.9423E-6', '14.7703E-6'],
		    ['12.3729E-6', '11.1883E-6'],
		    ['8.41537E-6', '7.84019E-6'],
		    ['6.32063E-6', '5.99155E-6']]

    # Process input with regexp

    fixedlines = []
    modified = False

    proprex  = re.compile('[ \t]*MANUFACTURINGGRID')
    edgerex  = re.compile('[ \t]*EDGECAPACITANCE')
    platerex = re.compile('[ \t]*CAPACITANCE[ \t]+CPERSQDIST')

    for line in llines:

        # Check for the MANUFACTURINGGRID statement in the file, and
        # add the USEMINSPACING statement after it.

        pmatch = proprex.match(line)
        if pmatch:
            fixedlines.append(line)
            fixedlines.append('USEMINSPACING OBS OFF ;')
            modified = True
        else:
            ematch = edgerex.match(line)
            pmatch = platerex.match(line)
            if ematch:
                found = False
                for ecap in edgevalues:
                    if ecap[0] in line:
                        fixedlines.append(re.sub(ecap[0], ecap[1], line))
                        modified = True
                        found = True
                        break
                if not found:
                    fixedlines.append(line)
            elif pmatch:
                found = False
                for pcap in platevalues:
                    if pcap[0] in line:
                        fixedlines.append(re.sub(pcap[0], pcap[1], line))
                        modified = True
                        found = True
                        break
                if not found:
                    fixedlines.append(line)
            else:
                fixedlines.append(line)

    # Write output
    if outname == None:
        for i in fixedlines:
            print(i)
    else:
        # If the output is a symbolic link but no modifications have been made,
        # then leave it alone.  If it was modified, then remove the symbolic
        # link before writing.
        if os.path.islink(outname):
            if not modified:
                return 0
            else:
                os.unlink(outname)
        try:
            with open(outname, 'w') as outFile:
                for i in fixedlines:
                    print(i, file=outFile)
        except:
            print('fix_techlef.py: failed to open ' + outname + ' for writing.', file=sys.stderr)
            return 1


if __name__ == '__main__':

    # This script expects to get one or two arguments.  One argument is
    # mandatory and is the input file.  The other argument is optional and
    # is the output file.  The output file and input file may be the same
    # name, in which case the original input is overwritten.

    options = []
    arguments = []
    for item in sys.argv[1:]:
        if item.find('-', 0) == 0:
            options.append(item[1:])
        else:
            arguments.append(item)

    if len(arguments) > 0:
        infilename = arguments[0]

    if len(arguments) > 1:
        outfilename = arguments[1]
    else:
        outfilename = None

    result = filter(infilename, outfilename)
    sys.exit(result)
