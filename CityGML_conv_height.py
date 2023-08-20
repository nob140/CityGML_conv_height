import sys
import os
import time
from lxml import etree
import requests
from collections import defaultdict
import uuid

# Utility functions
def error(text):
	print(text)
	sys.exit()

# unused
def conv_Building_height_AboveGround2Geoid(tree):
    # lon=140.08531&lat=36.103543
    url_elev = 'https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?outtype=JSON'
    url_geoid = 'http://vldb.gsi.go.jp/sokuchi/surveycalc/geoid/calcgh/cgi/geoidcalc.pl?outputType=xml'

    bldgs = tree.xpath('//bldg:Building', namespaces={'bldg': 'http://www.opengis.net/citygml/building/2.0'})
    if len(bldgs) == 0:
        error('No Building')

    # update all height of Building
    all_minh = 99999.0
    all_maxh = -99999.0
    for bldg in bldgs:
        print(bldg)

        # calc ground/geoid height of Building
        dict_elevation = defaultdict(lambda: 0)
        bldg_min_groundh = 99999.0

        pos = bldg.xpath('.//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml'})
        if len(pos):
            error('No gml:pos')
        for p in pos:
            coord = p.text.split()
            elevation = dict_elevation[coord[0],coord[1]]

            if elevation == 0:
                # height above Mean Sea Level
                url = url_elev + '&lon=' + coord[0] + '&lat=' + coord[1]
                headerinfo = {"content-type": "application/json"}
                time.sleep(1)
                res = requests.get(url, headers=headerinfo)
                # {"elevation":9,"hsrc":"5m\uff08\u5199\u771f\u6e2c\u91cf\uff09"}
                data = res.json()
                height = float(data['elevation'])
                print('height above Mean Sea Level: ' + str(height))

                # geoid height
                url = url_geoid + '&longitude=' + coord[0] + '&latitude=' + coord[1]
                time.sleep(1)
                res = requests.get(url)
                # <?xml version="1.0" encoding="utf-8"?><ExportData><OutputData><latitude1>33.840955118</latitude1><longitude1>130.486741189</longitude1><geoidHeight>32.3700</geoidHeight></OutputData></ExportData>
                xmltree = etree.fromstring(res.content)
                data = xmltree.xpath('.//geoidHeight')
                if len(data) == 0:
                    error('Not valid response from GEOID API')
                geoidh = float(data[0].text)
                print('geoid height: ' + str(geoidh))

                elevation = height + geoidh
                print('elevation 2: ' + str(elevation))
                dict_elevation[coord[0],coord[1]] = elevation

                if elevation < bldg_min_groundh:
                    bldg_min_groundh = elevation

        print('height ' + str(bldg_min_groundh))
        if bldg_min_groundh > 99990:
            error('No valid coordinates')
        if len(pos):
            for p in pos:
                # update height
                coord = p.text.split()
                height = float(coord[2]) + bldg_min_groundh
                print(coord[2] + '+' + str(bldg_min_groundh) + '=' + str(height))
                p.text = str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(height)
                # print(p.text)

                # remembering min/max height for updating gml:Envelope
                if all_maxh < height:
                    all_maxh = height
                if height < all_minh:
                    all_minh = height

    return all_minh, all_maxh

def conv_Building_height_AboveGround2MSL(tree):
    # lon=140.08531&lat=36.103543
    url_elev = 'https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?outtype=JSON'

    bldgs = tree.xpath('//bldg:Building', namespaces={'bldg': 'http://www.opengis.net/citygml/building/2.0'})
    if len(bldgs) == 0:
        error('No Building')

    # update all height of Building
    all_minh = 99999.0
    all_maxh = -99999.0
    for bldg in bldgs:
        print(bldg)

        # calc ground height of Building
        dict_elevation = defaultdict(lambda: 0)
        bldg_min_groundh = 99999.0

        pos = bldg.xpath('.//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml'})
        if len(pos) == 0:
            error('No gml:pos')
        for p in pos:
            coord = p.text.split()
            elevation = dict_elevation[coord[0],coord[1]]

            if elevation == 0:
                # height above Mean Sea Level
                url = url_elev + '&lon=' + coord[0] + '&lat=' + coord[1]
                headerinfo = {"content-type": "application/json"}
                time.sleep(1)
                res = requests.get(url, headers=headerinfo)
                # {"elevation":9,"hsrc":"5m\uff08\u5199\u771f\u6e2c\u91cf\uff09"}
                data = res.json()
                elevation = float(data['elevation'])
                print('height above Mean Sea Level: ' + str(elevation))

                dict_elevation[coord[0],coord[1]] = elevation

                if elevation < bldg_min_groundh:
                    bldg_min_groundh = elevation

        # update height
        print('height ' + str(bldg_min_groundh))
        if bldg_min_groundh > 99990:
            error('No valid coordinates')
        for p in pos:
            coord = p.text.split()
            height = float(coord[2]) + bldg_min_groundh
            print(coord[2] + '+' + str(bldg_min_groundh) + '=' + str(height))
            p.text = str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(height)
            # print(p.text)

            # remembering min/max height for updating gml:Envelope
            if all_maxh < height:
                all_maxh = height
            if all_minh > height:
                all_minh = height

    return all_minh, all_maxh

def conv_Building_height_AboveMSL2Geoid(tree):
    # lon=140.08531&lat=36.103543
    url_geoid = 'http://vldb.gsi.go.jp/sokuchi/surveycalc/geoid/calcgh/cgi/geoidcalc.pl?outputType=xml'

    bldgs = tree.xpath('//bldg:Building', namespaces={'bldg': 'http://www.opengis.net/citygml/building/2.0'})
    if len(bldgs) == 0:
        error('No Building')

    # update all height of Building
    all_minh = 99999.0
    all_maxh = -99999.0
    for bldg in bldgs:
        print(bldg)

        # calc geoid height of Building
        dict_elevation = defaultdict(lambda: 0)
        bldg_min_groundh = 99999.0

        pos = bldg.xpath('.//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml'})
        if len(pos) == 0:
            error('No gml:pos')
        for p in pos:
            coord = p.text.split()
            elevation = dict_elevation[coord[0],coord[1]]

            if elevation == 0:
                # geoid height
                url = url_geoid + '&longitude=' + coord[0] + '&latitude=' + coord[1]
                time.sleep(1)
                res = requests.get(url)
                # <?xml version="1.0" encoding="utf-8"?><ExportData><OutputData><latitude1>33.840955118</latitude1><longitude1>130.486741189</longitude1><geoidHeight>32.3700</geoidHeight></OutputData></ExportData>
                xmltree = etree.fromstring(res.content)
                data = xmltree.xpath('.//geoidHeight')
                if len(data) == 0:
                    error('Not valid response from GEOID API')
                elevation = float(data[0].text)
                print('geoid height: ' + str(elevation))

                dict_elevation[coord[0],coord[1]] = elevation

                if elevation < bldg_min_groundh:
                    bldg_min_groundh = elevation

        print('height ' + str(bldg_min_groundh))
        if bldg_min_groundh > 99990:
            error('No valid coordinates')
        for p in pos:
            # update height
            coord = p.text.split()
            height = float(coord[2]) + bldg_min_groundh
            print(coord[2] + '+' + str(bldg_min_groundh) + '=' + str(height))
            p.text = str(coord[0]) + ' ' + str(coord[1]) + ' ' + str(height)
            # print(p.text)

            # remembering min/max height for updating gml:Envelope
            if all_maxh < height:
                all_maxh = height
            if height < all_minh:
                all_minh = height

    return all_minh, all_maxh

# flip X/Y of coordinates
def flip_XY(tree):
    flip_XY_Envelope(tree)
    flip_XY_pos(tree)

def flip_XY_Envelope(tree):
    envelopes = tree.xpath('//gml:Envelope', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(envelopes) == 0:
        error('No gml:Envelope')
    envelope = envelopes[0]

    lowerCorner = envelope.xpath('.//gml:lowerCorner', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(lowerCorner) == 0:
        error('No gml:lowerCorner')
    # print(lowerCorner[0].text)
    coord = lowerCorner[0].text.split()
    lowerCorner[0].text = coord[1] + ' ' + coord[0] + ' ' + coord[2]
    # print(lowerCorner[0].text)

    upperCorner = envelope.xpath('.//gml:upperCorner', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(upperCorner) == 0:
        error('No gml:upperCorner')
    # print(upperCorner[0].text)
    coord = upperCorner[0].text.split()
    upperCorner[0].text = coord[1] + ' ' + coord[0] + ' ' + coord[2]
    # print(upperCorner[0].text)

def flip_XY_pos(tree):
    pos = tree.xpath('//gml:pos', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(pos) == 0:
        error('No gml:pos')
    for p in pos:
        coord = p.text.split()
        p.text = coord[1] + ' ' + coord[0] + ' ' + coord[2]

# update gml:Envelope srsName
def update_Envelope_srsName(tree, srsName):
    envelopes = tree.xpath('//gml:Envelope', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(envelopes) == 0:
        error('No gml:Envelope')

    envelope = envelopes[0]
    envelope.set('srsName', srsName)
    envelope.set('srsDimension', '3')

# update gml:Envelope height
def update_Envelope_height(tree, minh, maxh):
    envelopes = tree.xpath('//gml:Envelope', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(envelopes) == 0:
        error('No gml:Envelope')

    envelope = envelopes[0]
    lowerCorner = envelope.xpath('.//gml:lowerCorner', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(lowerCorner) == 0:
        error('No gml:lowerCorner')
    coord = lowerCorner[0].text.split()
    lowerCorner[0].text = coord[0] + ' ' + coord[1] + ' ' + str(minh)
    print(lowerCorner[0].text)

    upperCorner = envelope.xpath('.//gml:upperCorner', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(upperCorner) == 0:
        error('No gml:upperCorner')
    coord = upperCorner[0].text.split()
    upperCorner[0].text = coord[0] + ' ' + coord[1] + ' ' + str(maxh)
    print(upperCorner[0].text)

# update Building gml:id with UUID, and delete other gml:id such as Polygon's
def update_gmlid_UUID(tree):
    # delete gml:id of gml:Polygon
    polygons = tree.xpath('//gml:Polygon[@gml:id]', namespaces={'gml': 'http://www.opengis.net/gml'})
    if len(polygons) == 0:
        error('No gml:Polygon')
    for polygon in polygons:
        # print(polygon)
        
        # replace gml:id with UUID
        # newid = 'poly-' + str(uuid.uuid1())
        # polygon.set('{http://www.opengis.net/gml}id', newid)
        
        # delete gml:id attribute from gml:Polygon
        del polygon.attrib['{http://www.opengis.net/gml}id']

        # print(polygon.get('{http://www.opengis.net/gml}id'))

    # add gml:id to bldg:Building
    bldgs = tree.xpath('//bldg:Building', namespaces={'bldg': 'http://www.opengis.net/citygml/building/2.0'})
    if len(bldgs) == 0:
        error('No bldg:Building.')
    for bldg in bldgs:
        print(bldg)
        newid = 'bldg-' + str(uuid.uuid1())
        bldg.set('{http://www.opengis.net/gml}id', newid)
        print(bldg.get('{http://www.opengis.net/gml}id'))

# update height above ground to both MSL and Geoid, with updating srsName and gml:id
# height calculated based on the lowest point of each Building using GSI's API
def update_height_gmlid(inputfile):
    file_name = os.path.basename(inputfile)
    file_path = os.path.dirname(inputfile)

    # JGD2011, flip X/Y and update gml:Envelope
    outputdir = file_path + '_JGD2011'
    os.makedirs(outputdir, exist_ok=True)
    outputfile = outputdir + '/' + file_name
    print('Process started: ' + inputfile + ', ' + outputfile)

    try:
        tree = etree.parse(inputfile)
    except ET.ParseError as e:
        print(f"XML data is not valid: {str(e)}")

    minh, maxh = conv_Building_height_AboveGround2MSL(tree)
    update_Envelope_height(tree, minh, maxh)
    update_Envelope_srsName(tree, 'http://www.opengis.net/def/crs/EPSG/0/6697')
    update_gmlid_UUID(tree)
    flip_XY(tree)

    tree.write(
        outputfile,
        pretty_print = True,
        xml_declaration = True,
        encoding = "utf-8" )
    print('Process finished: ' + inputfile + ', ' + outputfile)

    # WGS84, convert ground height to above GEOID
    outputdir = file_path + '_WGS84'
    os.makedirs(outputdir, exist_ok=True)
    outputfile = outputdir + '/' + file_name
    print('Process started: ' + inputfile + ', ' + outputfile)

    flip_XY(tree)
    minh, maxh = conv_Building_height_AboveMSL2Geoid(tree)
    update_Envelope_height(tree, minh, maxh)
    update_Envelope_srsName(tree, 'WGS84')
    
    tree.write(
        outputfile,
        pretty_print = True,
        xml_declaration = True,
        encoding = "utf-8" )
    print('Process finished: ' + inputfile + ', ' + outputfile)

# main
# convert all files under the INPUT_PATH or Current directory
if __name__ == '__main__':
    usage = 'Usage: python {} [INPUT_PATH]'.format(os.path.basename(__file__))
    
    arguments = sys.argv
    if len(arguments) == 1:
        input_dir = os.getcwd()
    elif len(arguments) == 2:
        input_dir = arguments[1]
        if os.path.isdir(input_dir) == False:
            error(input_dir + ' is not dir.\n' + usage)
        if input_dir.endswith('/'):
            input_dir = input_dir[:-1]
    else:
        error('Parameter is not valid.\n' + usage)

    print('input_dir: ' + input_dir)
    files = os.listdir(input_dir)
    print(files)
    for filename in files:
        filepath = input_dir + '/' + filename
        if os.path.isfile(filepath) == True:
            if filepath.endswith('.gml') == True or filepath.endswith('.xml') == True:
                update_height_gmlid(filepath)
