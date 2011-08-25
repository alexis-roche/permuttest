import sys
import os
import xlrd
import xlwt

import numpy as np
from scikits.permuttest.two_sample import permutation_test


# data loading
def load_data_from_excel(filename):
    XLS = xlrd.open_workbook(filename)

    SUBJECTs = []
    EFFECTs = []
    ROIs = []
    GROUPs = []
    GROUPs_row = []
    GROUPs_n = []
    prevGROUP = ""

    for s in range(0, XLS.nsheets):
        SHEET = XLS.sheet_by_index(s)
        EFFECTs.append(SHEET.name)

        # check if the COLUMN HEADERS match across sheets
        for j in range(1, SHEET.ncols):
            if s == 0:
                ROIs.append(SHEET.cell(0, j).value)
            else:
                if not SHEET.cell(0, j).value == ROIs[j - 1]:
                    raise ValueError('column headers dont match in sheet %s'\
                                         % SHEET.name)

        # check if the SUBJECT NAMES match across sheets
        for j in range(1, SHEET.nrows):
            if s == 0:
                SUBJECTs.append(SHEET.cell(j, 0).value)

                # extract groups names
                if not prevGROUP == SHEET.cell(j, 0).value:
                    GROUPs.append(SHEET.cell(j, 0).value)
                    GROUPs_row.append(j)
                    prevGROUP = SHEET.cell(j, 0).value
            else:
                if not SHEET.cell(j, 0).value == SUBJECTs[j - 1]:
                    raise ValueError('subject names dont match in sheet %s'\
                                         % SHEET.name)

    # Compute the cardinality of each group
    for i in range(0, len(GROUPs) - 1):
        GROUPs_n.append(GROUPs_row[i + 1] - GROUPs_row[i])
    GROUPs_n.append(len(SUBJECTs) - GROUPs_row[len(GROUPs) - 1] + 1)

    # print details of the DATA loaded
    print "\n-> Table content:"
    print "\n   * %d subjects divided into %d groups:" % (len(SUBJECTs), len(GROUPs))
    for i in range(0,len(GROUPs)):
        print "        - '%s' (%d subjects)" % (GROUPs[i], GROUPs_n[i])
    print "\n   * %d ROIs:" % len(ROIs)
    for i in range(0,len(ROIs)):
        print "        - '%s'" % ROIs[i]
    print "\n   * %d effects:" % len(EFFECTs)
    for i in range(0,len(EFFECTs)):
        print "        - '%s'" % EFFECTs[i]

    return XLS, SUBJECTs, ROIs, EFFECTs, GROUPs, GROUPs_row, GROUPs_n



# main
if (len(sys.argv) < 2):
    print('USAGE: %s <data.xls> [permutations]' % sys.argv[0])
    sys.exit(0)

if (len(sys.argv) < 3):
    nPERMUTATIONS = 10000
else:
    nPERMUTATIONS = int(sys.argv[2])

DATA_basename, DATA_extension = os.path.splitext(sys.argv[1])
XLS, SUBJECTs, ROIs, EFFECTs, GROUPs, GROUPs_row, GROUPs_n = load_data_from_excel('%s.xls' % DATA_basename)

XLS_out = xlwt.Workbook()

Style_1 = xlwt.easyxf("font: color-index red; align: horiz center",   num_format_str='#,###0.000')
Style_2 = xlwt.easyxf("font: color-index black; align: horiz center", num_format_str='#,###0.000')
Style_3 = xlwt.easyxf("font: color-index black; align: horiz center; pattern: pattern solid, fore_color grey25")

nTESTs    = len(GROUPs) * (len(GROUPs) - 1) / 2
SHEET_out = XLS_out.add_sheet("Hotelling Test")
SHEET_out.col(0).width = 15*256
SHEET_out.write(0, 0,        "uncorrected", Style_3)
SHEET_out.write(0+nTESTs+2, 0, "corrected",   Style_3)
for r in range(0, len(ROIs)):
    SHEET_out.write(0, r+1,      ROIs[r], Style_3)
    SHEET_out.write(0+nTESTs+2, r+1, ROIs[r], Style_3)
    SHEET_out.col(r+1).width = 15*256

print "\n-> Running pairwise PERMUTATION TESTS:\n"
OUT_row = 1
for i1 in range(0,len(GROUPs)):
    for i2 in range(i1+1,len(GROUPs)):
        print "      * '%s' vs '%s'" % (GROUPs[i1], GROUPs[i2])
        SHEET_out.write(OUT_row, 0, "%s vs %s" % (GROUPs[i1], GROUPs[i2]), Style_3)
        SHEET_out.write(OUT_row+nTESTs+2, 0, "%s vs %s" % (GROUPs[i1], GROUPs[i2]), Style_3)

        # prepare data
        Y1 = np.zeros([GROUPs_n[i1], len(ROIs), len(EFFECTs)])
        Y2 = np.zeros([GROUPs_n[i2], len(ROIs), len(EFFECTs)])
        for e in range(0, len(EFFECTs)):
            SHEET = XLS.sheet_by_index(e)

            for r in range(0, len(ROIs)):
                for s in range(0,GROUPs_n[i1]):
                    Y1[ s, r, e ] = SHEET.cell(GROUPs_row[i1]+s,r+1).value
                for s in range(0,GROUPs_n[i2]):
                    Y2[ s, r, e ] = SHEET.cell(GROUPs_row[i2]+s,r+1).value

        # run the test
        t, T, pu, p = permutation_test(Y1, Y2, permutations=nPERMUTATIONS)

        # add to the spreadsheet
        for r in range(0, len(ROIs)):
            if pu[r] <= 0.05:
                SHEET_out.write(OUT_row, r+1, pu[r], Style_1)
            else:
                SHEET_out.write(OUT_row, r+1, pu[r], Style_2)
            if p[r] <= 0.05:
                SHEET_out.write(OUT_row+nTESTs+2, r+1, p[r], Style_1)
            else:
                SHEET_out.write(OUT_row+nTESTs+2, r+1, p[r], Style_2)
        OUT_row = OUT_row + 1


# writing results to file
print "\n-> writing results to file...",
XLS_out.save("%s__results.xls" % DATA_basename)
print " [ OK ]"
