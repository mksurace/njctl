import urllib
import sys

trueYearMap = {
    2010: 2009,
    2011: 2010,
    2012: 2011,
    2013: 2012,
    13: 2013,
    14: 2014
    }

def handleInt(s):
    s = s.strip()
    if s == "*":
        s = None
    if s:
        return int(s)
    else:
        return 0

def handleData(s):
    s = s.strip()
    if s == "*":
        s = None
    if s:
        return float(s)/10
    else:
        return 0

SHOULDDOWNLOAD = False

with open("masterfile.txt", 'w') as o:
    o.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
        ("Year",
         "Grade",
         "CDS",
         "CountyName",
         "DistrictName",
         "SchoolName",
         "TotalValidScaleMath",
         "TotalPPMath",
         "TotalPMath",
         "TotalAPMath",
         "TotalMeanScaleMath",
         "TotalValidScaleScience",
         "TotalPPScience",
         "TotalPScience",
         "TotalAPScience",
         "TotalMeanScaleScience",
         "MathRank",
         "ScienceRank",
         "MathPct",
         "SciencePct"
         ))

for yr in [2010, 2011, 2012, 2013, 13, 14]:
    for gr in range(3,9):
        url = "http://www.state.nj.us/education/schools/achievement/%d/njask%d/state_summary.txt" % (yr, gr)
        filename = "%d-%d.txt" % (trueYearMap[yr], gr)
        if SHOULDDOWNLOAD:
            urllib.urlretrieve(url, filename)

        with open(filename) as f:
            schools = []
            for l in f:
                # NJDOE state summaries use fixed width formatting.
                schoolname = l[109:159].strip()
                if schoolname:
                    schoolCDS = l[0:9]
                    countyName = l[9:59].strip()
                    districtName = l[59:109].strip()
                    TotalValidScaleMath = handleInt(l[232:238])
                    TotalPPMath = handleData(l[238:242])
                    TotalPMath = handleData(l[242:246])
                    TotalAPMath = handleData(l[246:250])
                    TotalMeanScaleMath = handleData(l[250:254])

                    TotalValidScaleScience = handleInt(l[278:284])
                    TotalPPScience = handleData(l[284:288])
                    TotalPScience = handleData(l[288:292])
                    TotalAPScience = handleData(l[292:296])
                    TotalMeanScaleScience = handleData(l[296:300])

                    schools.append([schoolCDS, countyName, districtName, schoolname, TotalValidScaleMath,
                                 TotalPPMath,
                                 TotalPMath,
                                 TotalAPMath,
                                 TotalMeanScaleMath,
                                 TotalValidScaleScience,
                                 TotalPPScience,
                                 TotalPScience,
                                 TotalAPScience,
                                 TotalMeanScaleScience])

            schoolScienceRankings = {}
            schoolMathRankings = {}
            schoolMathPct = {}
            schoolSciencePct = {}

            # Sort by total mean scale math
            schools.sort(key=lambda tup: tup[8], reverse=True)

            mathCount = 0
            rank = 1
            curScore = 0
            for school in schools:
                if school[8] > 0:
                    schoolMathRankings[school[0]] = rank

                    if curScore != school[8]:
                        rank = rank + 1
                        curScore = school[8]
                        
                    mathCount = mathCount + 1
                    
                    worseSchoolCount = 0
                    for i in range(mathCount, len(schools)):
                        if schools[i][8] > 0 and schools[i][8] < curScore:
                            worseSchoolCount = worseSchoolCount + 1
                    schoolMathPct[school[0]] = worseSchoolCount
                else:
                    schoolMathRankings[school[0]] = -1
                    schoolMathPct[school[0]] = -1

            # Sort by total mean scale science
            schools.sort(key=lambda tup: tup[13], reverse=True)
            scienceCount = 0
            rank = 1
            curScore = 0
            for school in schools:
                if school[13] > 0:
                    schoolScienceRankings[school[0]] = rank

                    if curScore != school[13]:
                        rank = rank + 1
                        curScore = school[13]
                        
                    scienceCount = scienceCount + 1

                    worseSchoolCount = 0
                    for i in range(scienceCount, len(schools)):
                        if schools[i][13] > 0 and schools[i][13] < curScore:
                            worseSchoolCount = worseSchoolCount + 1
                    schoolSciencePct[school[0]] = worseSchoolCount
                else:
                    schoolScienceRankings[school[0]] = -1
                    schoolSciencePct[school[0]] = -1
                    
            with open("masterfile.txt", 'a') as o:
                for school in schools:
                    mathPct = -1
                    sciencePct = -1
                    if schoolMathPct[school[0]] > 0:
                        mathPct = 100*(1-float(schoolMathPct[school[0]])/mathCount)
                    if schoolSciencePct[school[0]] > 0:
                        sciencePct = 100*(1-float(schoolSciencePct[school[0]])/scienceCount)
                    o.write("%d\t%d\t%s\t%s\t%s\t%s\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%d\t%d\t%0.1f\t%0.1f\n" %
                        (trueYearMap[yr], gr, school[0],
                         school[1],
                         school[2],
                         school[3],
                         school[4],
                         school[5],
                         school[6],
                         school[7],
                         school[8],
                         school[9],
                         school[10],
                         school[11],
                         school[12],
                         school[13],
                         schoolMathRankings[school[0]],
                         schoolScienceRankings[school[0]],
                         mathPct,
                         sciencePct
                         ))
                
