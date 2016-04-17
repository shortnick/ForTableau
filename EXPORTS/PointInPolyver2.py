"""
WKT ?PointInPolygon? script for Tableau

"""
import os
import csv
from osgeo import ogr



#----------------------------------------------------------------------

# WKT Storage Objects (see Working Data Dictionaries)

class StateObj(object):
    """
    Returns object with attributes identity, state label, and coordinates (expected format:WKT), 
    """
    def __init__(self, ident, state, coords):
        self.ident = ident
        self.state = state
        self.coords = coords
        self.realGeom = ogr.CreateGeometryFromWkt(coords)

        
class PointObj(object):
    """
    Returns object with attributes identity state, coords (expected format:WKT). State initializes as "..."
    """
    def __init__(self, ident, coords):
        self.ident = ident
        self.state = "..."
        self.coords = coords
        self.realGeom = ogr.CreateGeometryFromWkt(coords)

#----------------------------------------------------------------------

#File I/O and Input Verification 
def state_reader(file_obj):
    """
    Takes CSV and appends each line to statesDict as a StateObj. 
    """
    reader = csv.DictReader(file_obj, delimiter='|')
    for line in reader:
        statesList.append(StateObj(line["id"], line["state"],line["geometry"]))


def point_reader(file_obj):
    """
    Takes CSV and appends each line to pointsDict as a PointObj. 
    """
    reader = csv.DictReader(file_obj, delimiter='|')
    for line in reader:
        #testObj = ogr.CreateGeometryFromWkt(line["geometry"])
        
        if ogr.CreateGeometryFromWkt(line["geometry"]).GetGeometryName()[0:5] == "POINT":
            pointsList.append(PointObj(line["id"],line["geometry"]))
        else:
            print "Unexpected format ", line

def poly_valid(statesList):
    """
    Writes bad WKT polygons to an OUTERRORS.csv via logfile[] and appends ER to state.state

    """
    for state in statesList:
        if not state.realGeom.IsValid():
            logfile.append("BAD POLY"+"|"+state.ident+"|"+state.coords+"|"+state.state)
            state.ident = str(state.ident)+"ER"
    print "polys:error_writer(logfile, OUTERRORS)"

def point_valid(pointsList):
    """
    Writes bad WKT points to an OUTERRORS.csv via logfile[].
    """
    for item in pointsList:
        if not item.realGeom.IsValid(): 
            logfile.append("BAD POINT|"+item.ident+"|"+item.coords)
            item.state = "ER"
    print "points:error_writer(logfile, OUTERRORS)"
        
def take_file_inputs(inPointsCSV,inStatesCSV):
    """
    Takes 2 CSVs and runs a specific CSV reader, respectively - point_reader() and state_reader(), on each.

    Writes invalid geometries to an OUTERRORS.csv via logfile[].
    """
        
#check file type: https://docs.python.org/2/library/mimetypes.html
        #print "Ingesting CSV files"
        
    with open(WORKDIR+INSTATESCSV) as file:
        state_reader(file)
        #print "States complete"
    poly_valid(statesList)

    with open(WORKDIR+INPOINTSCSV) as file:
        point_reader(file)
        #print "Points complete"
    point_valid(pointsList)

def points_writer(pointsDict, path):
    """
    Writes pointsDict's PointObj to CSV. Default delimiter is '|' .
    """
    with open(path, 'w') as csvfile:
        fieldnames = ['id', 'state', 'geometry']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        # there's a stray \n character at ?end of line? in here
        writer.writeheader()
        for point in pointsDict:
               writer.writerow({fieldnames[0]: point.ident, fieldnames[1]: point.state, fieldnames[2]:point.coords})
"""
def error_writer(logfile, path):
    
    Writes pointsDict's PointObj to CSV. Default delimiter is '|' .
    
    with open(path, 'w') as csvfile:
        fieldnames = ['type', 'WKT', 'poly label']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
fix this still
        writer.writeheader()
        for point in pointsDict:
               writer.writerow({fieldnames[0]: point.ident, fieldnames[1]: point.state, fieldnames[2]:point.coords})

"""

#----------------------------------------------------------------------

#Analysis
def pointInPolyTest(pointsList, statesList):
    '''
    Checks pointsDict against statesDict, using ogr.Intersects. 

    Transfers .state for matching point/state tests. 
    Point.state NA for non-intersections

    '''

    ### Move validity tests into take_files_input function as sub-functions
    ### that way we can 1) log bad things initially, 2) remove bad things from Lists
	### 3) complete testing, even with dirty data. 
    #tests validity of polygon geometry

    #actual 'point in poly' comparison
    for testPoint in pointsList:

        for statePoly in statesList:
              
            if testPoint.realGeom.Intersects(statePoly.realGeom):
                testPoint.state = statePoly.state
                #print "Point changed to "+pointsDict[item].state
            #this catches points not in any polygons
            elif testPoint.state=="...":
                testPoint.state = "NA"
            #print "Point out of area"



#=======================================================
"""
Processing/Workflow below
"""

if __name__ == '__main__': 
    '''
    Assumes all files are in current working directory
    '''
    WORKDIR = os.getcwd()+"\\"
    INPOINTSCSV= "zip.csv"
    INSTATESCSV= "states.csv"
    OUTFILE = "someFile.csv"
#add a 'gettime' function to denote runs
    OUTERRORS = "errors.csv"
        
    statesList=[]
    pointsList=[]
    logfile=[]

    take_file_inputs(INPOINTSCSV,INSTATESCSV)

    pointInPolyTest(pointsList, statesList)

    points_writer(pointsList, OUTFILE)

    print "Processing complete"