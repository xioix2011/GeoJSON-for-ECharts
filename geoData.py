#--*-- coding:utf-8 --*--
import urllib2
import json
from urllib import urlencode


def saveToJSON(name,data):
    file = open(name+'.json','w')
    print json.dumps(data).encode('utf-8')
    file.write(json.dumps(data).encode('utf-8'))
    file.close()




def parse_str_to_json(dataStr):
    str1 = '('
    pos = dataStr.index(str1)

    if pos < 0:
        print("返回的数据格式不正确 示例为: jsonp_xxxxx_({...})  {...}内为json格式 ")
        return

    newJsonStr = dataStr[pos+1:-1]
    return json.loads(newJsonStr)




def parse_json_to_geo(jsonData, citycode):
    geojson = {}
    coordinates = []
    id = ''
    name = ''
    count = 0
    print len(jsonData['districts'])
    for district in jsonData['districts']:
        id = district['adcode']
        name = district['name']
        code = district['citycode']
        print code
        if code != citycode:
            print name + ' - (' + id + ') '+code+' IS NOT '+citycode
            continue
        polylineArrStr = district['polyline']
        polylineArr = polylineArrStr.split('|')
        count = len(polylineArr)
        if count > 1:
            coordinategroup = []
            for polyline in polylineArr:
                pointStrArr = polyline.split(';')

                cordinate = []
                for pointStr in pointStrArr:
                    pointArr = pointStr.split(',')
                    lng = float(pointArr[0])
                    lat = float(pointArr[1])
                    coordArr = [lng,lat]
                    cordinate.append(coordArr)
        
                coordinategroup.append(cordinate)
            coordinates.append(coordinategroup)
        else:
            for polyline in polylineArr:
                pointStrArr = polyline.split(';')

                cordinate = []
                for pointStr in pointStrArr:
                    pointArr = pointStr.split(',')
                    lng = float(pointArr[0])
                    lat = float(pointArr[1])
                    coordArr = [lng,lat]
                    cordinate.append(coordArr)
        
                coordinates.append(cordinate)

    geojson['type'] = 'Feature'
    geojson['id'] = id
    geojson['properties'] = {}
    geojson['properties']['name'] = name
    geojson['geometry'] = {}
    geojson['geometry']['type'] =  'MultiPolygon' if count > 1 else 'Polygon'
    geojson['geometry']['coordinates'] = coordinates
    print geojson
    return geojson


def get_str_from_amap(key):
    encodeUrl = urlencode({ 'subdistrict':'1',
                            'level':'district',
                            'extensions':'all',
                            'key':'608d75903d29ad471362f8c58c550daf',
                            's':'rsv3',
                            'output':'json',
                            'keywords':key,
                            'callback':'jsonp_146292_',
                            'platform':'JS',
                            'logversion':'2.0',
                            'sdkversion':'1.3',
                            'appname':'http://webapi.amap.com/demos/district/list.html',
                            'csid':'E3061005-C39B-4516-A1BD-F2B806AAA31C'})
    print encodeUrl
    request = urllib2.Request('http://restapi.amap.com/v3/config/district?'+encodeUrl)

    request.add_header('Accept','*/*')
    request.add_header('Accept-Encoding','gzip, deflate, sdch')
    request.add_header('Accept-Language','zh-CN,zh;q=0.8')
    request.add_header('Connection','keep-alive')
    request.add_header('Host','restapi.amap.com')
    request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36 QQBrowser/4.0.4035.400')
    request.add_header('Cookie','guid=d381-2b57-c9cd-5ba1; cna=RlNpDpKjqW4CAToxXZ58kU9u; _ga=GA1.2.1602103404.1446220048; uaid=294076c642e84d149a03306713455023; l=Am1tOsOnv7wn9qRkFSjOL9ir/QPmVqG5; isg=AjU14En9jm8Ya-rTHGjf3DlpUbck-OnE4qLHErdbbazejlaAaAOlkBmMruVD; key=608d75903d29ad471362f8c58c550daf')
    request.add_header('Referer','http://webapi.amap.com/demos/district/list.html')

    response = urllib2.urlopen(request)
    return response.read()
    

def getdata(disList,citycode):
    for name in disList:
        print '开始下载 '+name+' 数据'
        dataStr = get_str_from_amap(name)

        print '开始处理 '+name+' 数据'
        jsonData = parse_str_to_json(dataStr)
        geoData = parse_json_to_geo(jsonData,citycode)

        print '开始保存 '+name+' 数据'
        saveToJSON(name,geoData)

def merageDataToEcharts(cityname,disList):
    data = {}
    data['type'] = 'FeatureCollection'
    data['features'] = []
    for name in disList:
        with open(name+'.json') as data_file:  
            print '读取'+ name +'数据'  
            featureData = json.load(data_file)
            data['features'].append(featureData)
    with open(cityname+'.json','w') as data_file:  
        print '保存武汉市行政区'  
        json.dump(data,data_file)

list1 = ['江汉区','江岸区','硚口区','汉阳区','武昌区','青山区','洪山区','东西湖区','汉南区','蔡甸区','江夏区','黄陂区','新洲区']
# list = ['青山区']
getdata(list1,'027')

merageDataToEcharts('武汉市',list1)
