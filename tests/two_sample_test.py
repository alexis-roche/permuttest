import sys
import os
import xlrd
import xlwt

import numpy as np
from scikits.permuttest.two_sample import permutation_test


# data loading
def load_data_from_excel(filename):
    xls = xlrd.open_workbook(filename)

    subjects = []
    effects = []
    covariates = []
    rois = []
    groups = []
    groups_row = []
    groups_n = []
    prev_group = ""

    for s in range(0, xls.nsheets):
        sheet = xls.sheet_by_index(s)
        if sheet.name == "Covariates" :
            for j in range(1, sheet.ncols):
                covariates.append(sheet.cell(0, j).value)
        else:
            effects.append(sheet.name)
            
            # check if the COLUMN HEADERS match across sheets
            if len(rois) == 0 :
                for j in range(1, sheet.ncols):
                    rois.append(sheet.cell(0, j).value)
            else :
                for j in range(1, sheet.ncols):
                    if not sheet.cell(0, j).value == rois[j - 1]:
                        raise ValueError('column headers dont match in sheet %s' % sheet.name)


        # check if the SUBJECT NAMES match across sheets
        for j in range(1, sheet.nrows):
            if s == 0:
                subjects.append(sheet.cell(j, 0).value)

                # extract groups names
                if not prev_group == sheet.cell(j, 0).value:
                    groups.append(sheet.cell(j, 0).value)
                    groups_row.append(j)
                    prev_group = sheet.cell(j, 0).value
            else:
                if not sheet.cell(j, 0).value == subjects[j - 1]:
                    raise ValueError('subject names dont match in sheet %s'\
                                         % sheet.name)

    # Compute the cardinality of each group
    for i in range(0, len(groups) - 1):
        groups_n.append(groups_row[i + 1] - groups_row[i])
    groups_n.append(len(subjects) - groups_row[len(groups) - 1] + 1)

    # print details of the DATA loaded
    print "\n-> Table content:"
    print "\n   * %d subjects divided into %d groups"\
        % (len(subjects), len(groups))
    for i in range(0, len(groups)):
        print "        - '%s' (%d subjects)" % (groups[i], groups_n[i])
    print "\n   * %d rois" % len(rois)
    for i in range(0, len(rois)):
        print "        - '%s'" % rois[i]
    print "\n   * %d effects" % len(effects)
    for i in range(0, len(effects)):
        print "        - '%s'" % effects[i]
    print "\n   * %d covariates" % len(covariates)
    for i in range(0, len(covariates)):
        print "        - '%s'" % covariates[i]

    return xls, subjects, rois, effects, covariates, groups, groups_row, groups_n


# main function
# =============
if len(sys.argv) < 2:
    print('USAGE: %s <data.xls> [permutations] [tails] [use_covariates]' % sys.argv[0])
    sys.exit(0)

if len(sys.argv) < 3:
    nPERMUTATIONS = 10000
else:
    nPERMUTATIONS = int(sys.argv[2])

if len(sys.argv) < 4:
    nTAILS = 1
else:
    nTAILS = int(sys.argv[3])
    if nTAILS != 1 and nTAILS != 2:
        print('USAGE: %s <data.xls> [permutations] [tails] [use_covariates]' % sys.argv[0])
        print('\n       "tails" parameter accepts only 1 or 2')
        sys.exit(0)

if len(sys.argv) < 5:
    use_covariates = 0
else:
    use_covariates = int(sys.argv[4])
    if use_covariates != 0 and use_covariates != 1 :
        print('USAGE: %s <data.xls> [permutations] [tails] [use_covariates]' % sys.argv[0])
        print('\n       "use_covariates" parameter accepts only 0 or 1')
        sys.exit(0)
DATA_basename, DATA_extension = os.path.splitext(sys.argv[1])
xls, subjects, rois, effects, covariates, groups, groups_row, groups_n =\
    load_data_from_excel('%s.xls' % DATA_basename)


# COPY the data to the OUTPUT EXCEL FILE
# ======================================
xls_out = xlwt.Workbook()

Style_1 = xlwt.easyxf("font: color-index red; align: horiz center",
                      num_format_str='#,###0.000')
Style_2 = xlwt.easyxf("font: color-index black; align: horiz center",
                      num_format_str='#,###0.000')
Style_3 = xlwt.easyxf("font: color-index black; align: horiz center; pattern: pattern solid, fore_color grey25")

nTESTs = len(groups) * (len(groups) - 1) / 2
sheet_out = xls_out.add_sheet("Hotelling Test")
sheet_out.col(0).width = 15 * 256
sheet_out.write(0, 0, "uncorrected", Style_3)
sheet_out.write(0 + nTESTs + 2, 0, "corrected", Style_3)
for r in range(0, len(rois)):
    sheet_out.write(0, r + 1, rois[r], Style_3)
    sheet_out.write(0 + nTESTs + 2, r + 1, rois[r], Style_3)
    sheet_out.col(r + 1).width = 15 * 256


# Permutation tests
# =================

print "\n-> Running pairwise PERMUTATION TESTS:"
print "      - %d tail(s)" % (nTAILS)
print "      - %d permutations\n" % (nPERMUTATIONS)
OUT_row = 1
for i1 in range(0, len(groups)):
    for i2 in range(i1 + 1, len(groups)):
        print "      * '%s' vs '%s'" % (groups[i1], groups[i2])
        sheet_out.write(OUT_row, 0, "%s vs %s"\
                            % (groups[i1], groups[i2]), Style_3)
        sheet_out.write(OUT_row + nTESTs + 2, 0, "%s vs %s"\
                            % (groups[i1], groups[i2]), Style_3)

        # prepare data
        Y1 = np.zeros([groups_n[i1], len(rois), len(effects)])
        Y2 = np.zeros([groups_n[i2], len(rois), len(effects)])
        for e in range(0, len(effects)):
            sheet = xls.sheet_by_name( effects[e] )

            for r in range(0, len(rois)):
                for s in range(0, groups_n[i1]):
                    Y1[s, r, e] = sheet.cell(groups_row[i1] + s, r + 1).value
                for s in range(0, groups_n[i2]):
                    Y2[s, r, e] = sheet.cell(groups_row[i2] + s, r + 1).value

        # run the test
        if len(covariates) == 0 or use_covariates == False :
            t, T, pu, p = permutation_test(Y1, Y2, permutations=nPERMUTATIONS, confounds=None, two_sided=(True if nTAILS == 2 else False))
        else :
            # prepare covariates
            CONFOUNDS = np.zeros([len(covariates), groups_n[i1]+groups_n[i2]])
            sheet = xls.sheet_by_name( "Covariates" )
            for c in range(0, len(covariates)):
                for s in range(0, groups_n[i1]):
                    CONFOUNDS[c,s] = sheet.cell(groups_row[i1] + s, c + 1).value
                for s in range(0, groups_n[i2]):
                    CONFOUNDS[c, groups_n[i1]+s] = sheet.cell(groups_row[i2] + s, c + 1).value

            t, T, pu, p = permutation_test(Y1, Y2, permutations=nPERMUTATIONS, confounds=CONFOUNDS, two_sided=(True if nTAILS == 2 else False))

        # add to the spreadsheet
        for r in range(0, len(rois)):
            if pu[r] <= 0.05:
                sheet_out.write(OUT_row, r + 1, pu[r], Style_1)
            else:
                sheet_out.write(OUT_row, r + 1, pu[r], Style_2)
            if p[r] <= 0.05:
                sheet_out.write(OUT_row + nTESTs + 2, r + 1, p[r], Style_1)
            else:
                sheet_out.write(OUT_row + nTESTs + 2, r + 1, p[r], Style_2)
        OUT_row = OUT_row + 1


# writing results to file
print "\n-> Writing the results to file...",
if len(covariates) == 0 or use_covariates == False :
    xls_out.save("%s__resultsNoCovariates.xls" % DATA_basename)
else:
    xls_out.save("%s__resultsWithCovariates.xls" % DATA_basename)
print " [ OK ]"
