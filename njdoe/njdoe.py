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
    o.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" %
        ("Year",
         "Grade",
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
         "ScienceRank"
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
                    TotalValidScaleMath = handleData(l[232:238])
                    TotalPPMath = handleData(l[238:242])
                    TotalPMath = handleData(l[242:246])
                    TotalAPMath = handleData(l[246:250])
                    TotalMeanScaleMath = handleData(l[250:254])

                    TotalValidScaleScience = handleData(l[278:284])
                    TotalPPScience = handleData(l[284:288])
                    TotalPScience = handleData(l[288:292])
                    TotalAPScience = handleData(l[292:296])
                    TotalMeanScaleScience = handleData(l[296:300])

                    schools.append([schoolname, TotalValidScaleMath,
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

            # Sort by total mean scale math
            schools.sort(key=lambda tup: tup[5], reverse=True)

            rank = 0
            for school in schools:
                if school[5] > 0:
                    schoolMathRankings[school[0]] = rank
                    rank = rank + 1
                else:
                    schoolMathRankings[school[0]] = -1

            # Sort by total mean scale science
            schools.sort(key=lambda tup: tup[10], reverse=True)
            rank = 0
            for school in schools:
                if school[10] > 0:
                    schoolScienceRankings[school[0]] = rank
                    rank = rank + 1
                else:
                    schoolScienceRankings[school[0]] = -1
                    
            with open("masterfile.txt", 'a') as o:
                for school in schools:
                    o.write("%d\t%d\t%s\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%0.1f\t%d\t%d\n" %
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
                         schoolMathRankings[school[0]],
                         schoolScienceRankings[school[0]]
                         ))
                
