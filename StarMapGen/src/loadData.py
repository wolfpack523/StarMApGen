import re
from StarSystem import StarSystem


def loadData(fName, param, sysList, cList):
    '''loadData opens the file specified by fName and 
    reads in each of the star systems stored in in the file.
    It also requires the parameter object to be passed in (p).
    The function returns a list of StarSystem objects.
    '''
    try:
        f = open(fName, 'r')
    except:
        print("Unable to open file")
        exit(1)

    for line in f:
        # read in system name
        m = re.match('Name:\s*(.*)', line)
        #        l = re.match('Link:\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)\s*(\d+)',line)
        l = re.match('Link: "(.*)" "(.*)"', line)
        if m:
            s = StarSystem(param, generate=False)
            s.name = m.group(1)

            line = f.readline()

            pattern = re.compile(r"(\d+),(\d+),([-]*\d+)")
            match = pattern.search(line)

            s.x = int(match.group(1))
            s.y = int(match.group(2))
            s.z = int(match.group(3))
            s.mapPos = (s.x, s.y)

            line = f.readline()
            match = re.match(r"Number of Stars: (\d+)", line)
            s.nStars = int(match.group(1))

            line = f.readline()
            match = re.match(r"Spectral Types:\s*(.*)", line)
            s.stars = match.group(1).split(", ")

            f.readline()

            sysList.append(s)
        elif (l):
            cList.append((l.group(1), l.group(2)))
        else:
            print("No Match")
    f.close()
    return sysList
