#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2018 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner.py
# @author  Yun-Pang Floetteroed
# @author  Michael Behrisch
# @date    2018-09-03
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
from argparse import ArgumentParser
from optparse import OptionParser

import json
from pprint import pprint


# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
    shapes = os.path.join(os.environ['SUMO_HOME'], 'tools','sumolib', 'shapes')
    sys.path.append(shapes)
    import edgesInDistricts
    from polygon import Polygon
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa

import sumolib
from sumolib.net import readNet, convertXY2LonLat
from sumolib.output import parse

class Area():
    def __init__(self, id, rerouteMap, canNotReachMap, avgContainedMap):
        self.id = id
        self.reroute = rerouteMap
        self.canNotReach = canNotReachMap
        self.averageContained = avgContainedMap

    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)

class AffectedInterval():
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        self.areaData = []
        
    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4) 

class Edge():
    def __init__(self, id,travelTime,density,occupancy,waitingTime,speed):
        self.id = id
        self.travelTime = travelTime
        self.density = density
        self.occupancy = occupancy
        self.waitingTime = waitingTime
        self.speed = speed
        
    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4) 

class Interval():
    def __init__(self, begin, end):
        self.begin = begin
        self.end = end
        self.edgeData = []
        
    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)


class Timestep():
    def __init__(self, time):
        self.timeStep = time
        self.vehicleData = []
        
    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)

class Vehicle():
    def __init__(self, id, x, y, angle, type, speed):
        self.id = id
        self.lon = x
        self.lat = y
        self.angle = angle
        self.type = type
        self.speed = speed
        
    def toJson(self):
        '''
        Serialize the object custom object
        '''
        return json.dumps(self, default=lambda o: o.__dict__, 
                sort_keys=True, indent=4)

def checkWithin(poly,x,y):
    xmin, ymin, xmax, ymax = polygon.getBoundingBox(poly)
    bbPath = mplPath.Path(np.array([[p[0][0], p[0][1]],
                         [p[1][0], p[1][1]],
                         [p[2][0], p[2][1]],
                         [p[3][0], p[3][1]],
                         [p[4][0], p[4][1]]]))

    if bbPath.contains_point((x, y)):
        return True
    else:
        return False

def writeGeneralJsonOutput(options.aggregatedOutput, options.fcdOutput, fSingle):
    # write outputs according to the format in SingleVehicleOutput.avsc
    if fSingle:
        outputfile = 'SingleVehicleOutput_static.json'
        f = open(outputfile, 'w')
        f.close()
        for time in parse(options.fcdOutput, 'timestep'):
            timeObj = Timestep(time.time)
            
            for veh in time.vehicle:
                vObj = Vehicle(veh.id, veh.x, veh.y, veh.angle, veh.type, veh.speed)
                timeObj.vehicleData.append(vObj)

            j = json.loads(timeObj.toJson())
            j = json.dumps(j, sort_keys=True, indent=4)
            f = open(outputfile, 'a+')
            print >> f, j
            f.close()
    
    # write the aggregated SUMO output (edge-based) according to the format in AggregatedOutput.avsc
    outputfile = 'AggregatedOutput_static.json'
    f = open(outputfile, 'w')
    f.close()
    for interval in parse(options.aggregatedOutput, 'interval'):
        intervalObj = Interval(begin, end)
        
        for e in interval.edge:
            eObj = Edge(e.id, e.traveltime, e.density, e.occupancy, e.waitingTime, e.speed)
            intervalObj.edgeData.append(eObj)

        j = json.loads(intervalObj.toJson())
        j = json.dumps(j, sort_keys=True, indent=4)
        f = open(outputfile, 'a+')
        print >> f, j
        f.close()

def writeSingleVehJsonOutput(step, vehSet, fSingle, net):
    # write outputs according to the format in SingleVehicleOutput.avsc
    timeObj = Timestep(step)
    timeList = [timeObj]
    
    for vid in vehSet:
        x, y = traci.vehicle.getPosition(vid)
        angle = traci.vehicle.getAngle(vid)
        type = traci.vehicle.getTypeID(vid)
        speed = traci.vehicle.getSpeed(vid)
        x, y = net.convertXY2LonLat(x, y)
        
        vObj = Vehicle(vid, x, y, angle, type, speed)
        timeObj.vehicleData.append(vObj)

    j = json.loads(timeObj.toJson())
    j = json.dumps(j, sort_keys=True, indent=4)
    f = open(fSingle, 'a+')
    print >> f, j
    f.close()
    
    # todo: send the output to the testbed
    
    # delete data
    timeList.pop()

def writeAggregationJsonOutput(step, fAgg, net):
    # write outputs according to the format in AggregationOutput.avsc
    IntervalObj = Interval(step)
    intlList = [intervalObj]
    
    for eid in net._id2edge:
        density = traci.edge.getIntervalDensity(eid)     # to be built
        occ = traci.edge.getIntervalOccupancy(eid)   # to be built
        speed = traci.edge.getIntervalSpeed(eid)       # to be built
        tt = traci.edge.getIntervalTravelTime(eid)  # to be built
        wt = traci.edge.getIntervalWaitingTime(eid) # to be built
        
        eObj = Edge(eid, tt, density, occ, wt, speed)
        intervalObj.edgeData.append(eObj)

    j = json.loads(intervalObj.toJson())
    j = json.dumps(j, sort_keys=True, indent=4)
    f = open(fAgg, 'a+')
    print >> f, j
    f.close()
    
    # todo: send the output to the testbed
    
    # delete object/data
    intlList.pop()

def writeAffectTrafficJsonOutput(step, affectedInterval, pid, num_reroute, num_canNotReach, num_avgContained, fAff):
    begin = step - affectedInterval
    affectedIntervalObj = AffectedInterval(begin, step)
    intlList = [affectedIntervalObj]

    areaObj = Area(pid)
    affectedIntervalObj.areaData.append(areaObj)

    for e in interval.edge:
        eObj = Edge(e.id, e.traveltime, e.density, e.occupancy, e.waitingTime, e.speed)
        intervalObj.edgeData.append(eObj)

    j = json.loads(affectedIntervalObj.toJson())
    j = json.dumps(j, sort_keys=True, indent=4)
    f = open(fAff, 'a+')
    print >> f, j
    f.close()

    # todo: send the output to the testbed

    # deletet the object/data
    intlList.pop()

def run(config, area, net, step, affectedInterval, update=None):
    random.seed(42) # make tests reproducible
    """execute the TraCI control loop"""
    
    # initialization 
    num_reroute = {}
    num _canNotReach = {}
    num_avgContained = {}
    start_sim = False
    nextStep = False
    resetTLSProgram = True
    runningVehSet = set()
    arrivedVehSet = set()
    affectVehSet = set()
    fSingle = None
    
    if not os.path.exists('AggregatedOutput.json'):
        fAgg = open('AggregatedOutput.json', 'w')
        fAgg.close()
    if not os.path.exists('AffectedTraffic.json'):
        fAff = open('AffectedTraffic.json', 'w')
        fAff .close()

    if config["singleVehicle"] != -1 and not os.path.exists('SingleVehicleOutput.json'):
        fSingle = open('SingleVehicleOutput.json', 'w')
        fSingle.close()
        
    singleVehInterval = config["singleVehicle"]/1000.
    aggregation = config["aggregation"]/1000.

    if update:
        affectedInterval = update["affectedTraffic"]/1000.
        singleVehInterval = update["singleVehicle"]/1000.

    # if there is vehicle in the simulation
    while traci.simulation.getMinExpectedNumber() > 0:
        # single vehicle data
        if singleVehInterval > 0.:
            for vid in traci.simulation.getDepartedIDList:
                runningVehSet.add(vid)
            for vid in traci.simulation.getArrivedIDList:
                    arrivedVehSet.add(vid)

            runningVehSet -= arrivedVehSer
            
            if step % singleVehInterval == 0:
                writeSingleVehJsonOutput(step, runningVehSet, fSingle, net)   # todo: how to aggregate the output for fcd output via traci? are new functions needed? 

        # mean data
        # todo: new traci functions to get interval-based aggregation data
        if step % aggregation == 0:
            writeAggregationJsonOutput(step, fAgg, net)

        # calculate and write the affected traffic
        if step >= begin:
            resultMap = traci.polygon.getContextSubscriptionResults(pid) # for the affected traffic
            
            if step % affectedInterval == 0:
                writeAffectTrafficJsonOutput(step, affectedInterval, pid, num_reroute, num_canNotReach, num_avgContained, fAff)
                num_reroute = {}
                num_canNotReach = {}
                num_avgContained = {}
            else:
                if resultMap:
                    for veh, valMap in resultMap.items():
                        x, y = valMap[tc.VAR_POSITION]
                        if checkWithin(affectedPoly,x,y):
                            for m in [num_reroute, num_canNotReach, num_avgContained]:
                                if valMap[tc.VAR_VEHICLECLASS] not in m:
                                    m[valMap[tc.VAR_VEHICLECLASS]] = 0.
                                    
                            num_reroute[valMap[tc.VAR_VEHICLECLASS]] += int(valMap[tc.VAR_REROUTE])  # 0 or 1 
                            num_canNotReach[valMap[tc.VAR_VEHICLECLASS]] += int(valMap[tc.VAR_CAN_NOT_REACH])  # 0 or 1
                            num_avgContained[valMap[tc.VAR_VEHICLECLASS]] += int(valMap[tc.VAR_AVERAGE_CONTAINED]) # ? how to compute

        traci.close()
        sys.stdout.flush()
    
def handleAreaData(net, area, config, step):
    affectedIntersectionList = []
    affectedTLSList = []
    affectedEdgeList = []
    
    # currently only consider one polygon for each area
    polyObj = Polygon(area["id"], shape=area["area"]["coordinates"][0][0])
    polygons.append(polyObj)
    
    reader = edgesInDistricts.DistrictEdgeComputer(net)
    optParser = OptionParser()
    edgesInDistricts.fillOptions(optParser)
    edgeOptions, _ = optParser.parse_args([])
    reader.computeWithin(polygons, edgeOptions)
    
    # get the affected edges
    for idx, (district, edges) in enumerate(reader._districtEdges.items()):
        affectedEdgeList = edges  # there is only one district
        
    # get the affected intersections
    if area["trafficLightsBroken"]:
        for n in net._getNodes():
            x, y = n._coord  # check
            for poly in polygons:
                if checkWithin(poly,x,y) and n._type = "traffic_light" and n._id not in affectedIntersectionList:
                    affectedIntersectionList.append(n._id)

        # get the affected TLS
        tlsList = net.getTrafficLights()
        
        for tls in tlsList:
            if tls._id not in affectedTLSList:
                for c in tls.getConnections():
                    for n in (c[0].getEdge()._from(), c[0].getEdge()._to(), c[1].getEdge()._to()):
                        if n._id in affectedIntersectionList:
                            affectedTLSList.append(tls._id)
                            break

    # get the pre-defined conditions of the scenario
    begin = area["begin"]/1000.
    end = area["end"]/1000.
    tlsBroken = area["trafficLightsBroken"]
    restriction = area["restriction"].split()   # white space separated as in sumo
    affectedInterval = config["affectedTraffic"]/1000.   # collect the affected traffic

    if step == begin:
        # switch off the affected traffic lights
        for tlsId in affectedTLSList:
            traci.trafficlight.setProgram(tlsId, "off")
            
        # set the vehicle restriction on each edges
        for edge in affectedEdgeList:
            eObj = net._id2edge[edge]:
            for i in range(0, eObj.getLaneNumber()):
                laneID = edge + '_' + str(i)
                if 'all' in restriction:
                    traci.lane.setDisallowed(laneID, [])   # ? empty list = all vehicles are not allowed?
                else:
                    traci.lane.setDisallowed(laneID, restriction)

        # subscribe variables
        for pObj in polygons: # currently only consider one polygon
            # todo: wait for the new traci-function to get num_reroute, num _canNotReach and num_avgContained
            pid = pObj.id
            affectedPoly = pObj
            traci.polygon.subscribeContext(pid, tc.CMD_GET_VEHICLE_VARIABLE, 10., \
                                          [tc.VAR_VEHICLECLASS, \
                                           tc.VAR_POSITION,      \      # return sumo internal positions
                                           tc.VAR_ROUTE_VALID, \
                                           tc.VAR_REROUTE, \            # to be built
                                           tc.VAR_CAN_NOT_REACH, \      # to be built
                                           tc.VAR_AVERAGE_CONTAINED])   # to be built   ? check hoe to compute
                                           
            # need to recheck whether all retrieved vehicles are really in the polygon (or only in the defined bounding box)

    # reset the TLS programs
    if step == end:
        for tlsId in affectedTLSList:
            tlsObj = net.getTLSSecure(tlsId)
            for p in tlsObj.getPrograms().keys():  # only consider the first program
                traci.trafficlight.setProgram(tlsId, p)
                break

    return begin, end

def get_options():
    argParser = ArgumentParser()
    argParser.add_argument("--affected-area", dest="area",
                     default="AffectedArea.json", help="affected area definition", metavar="FILE")
    argParser.add_argument("--aggregated-output", dest="aggregatedOutput",
                     default="edgesOutput.xml", help="the file name of the edge-based output generated by SUMO", metavar="FILE")
    argParser.add_argument("--configuration", dest="config",
                     default="Configuration.json", help="configuration definition", metavar="FILE")
    argParser.add_argument("--fcd-output", dest="fcdOutput",
                     default="fcd.output", help=" the file name of the fcd output generated by SUMO", metavar="FILE")
    argParser.add_argument("--network-file", dest="netfile",
                     default="acosta_buslanes.net.xml", help="network file name", metavar="FILE")
    argParser.add_argument("--static-jsonOutput",  action="store_true", dest="staticJsonOutput",
                     default=False, help="write SUMO's static outputs in JSON format", metavar="FILE")
    argParser.add_argument("--update-configuration", dest="update",
                     default="UpdateConfiguration.json", help="configuration update definition", metavar="FILE")
    argParser.add_argument("--nogui", action="store_true",
                         default=False, help="run the command-line version of sumo")
    argParser.add_argument("--duration-statistics", action="store_true",          # ?: how to send this to the server?
                         default=False, help="enable statistics on vehicle trips")
    argParser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                     default=False, help="tell me what you are doing")
    options, args = argParser.parse_args()
    return options


# this is the main entry point of this script
if __name__ == "__main__":

    options = get_options()
    update = None
    # todo: set up the connection to the testbed and get the input files
    # todo: get the time from the testbed
    # todo: wait for the "config" message from the testbed
    
    while message from testbed:
        if message is "config":
            with open(options.config) as f:   # replace "options.config" with the string message 
                config = json.load(f)   # todo: read the string from the testbed  --> replace "f"
            f.close()
            step = 0
            
            # this script has been called from the command line. It will start sumo as a
            # server, then connect and run
            if options.nogui:
                sumoBinary = checkBinary('sumo')
            else:
                sumoBinary = checkBinary('sumo-gui')
            
            # this is the normal way of using traci. sumo is started as a
            # subprocess and then the python script connects and runs
            traci.start([sumoBinary, "-c", config["configFile"],
                                     "-b", str(config["begin"]),
                                     "-e", str(config["end"]),
                                     "--aggregation", str(config["aggregation"]),
                                     "--fcd-output",options.fcdOutput, 
                                     "--device.fcd.period",str(config["singleVehicle"]),  # todo: add an option for the period
                                     ])

            # get network
            #todo: get input file from the testbed
            for file in parse(config["configFile"], 'net-file'):
                netfile = file.value
                print (netfile)
            net = readNet(netfile)
            
        elif message is "area":
            # todo: replace "options.area" with the string message 
            with open(options.area) as f:
                area = json.load(f)
            f.close()
            
            # get the scenario data
            begin, end = handleAreaData(net, area, config, step)
        
        elif message is "update":
            # todo: replace "options.update" with the string message  
            with open(options.update) as f:
                update = json.load(f)

        elif message is "time":
            traci.simulationStep()
            step += 1

            # run the simulation by step, retrieve and calculate data as well as send data back to the testbed
            run(config, area, net, step, update)

    # write sumo outputs in json format
    if staticJsonOutput:
        writeGeneralJsonOutput(options.aggregatedOutput, options.fcdOutput, fSingle)
