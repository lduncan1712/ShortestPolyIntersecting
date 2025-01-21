

import matplotlib.pyplot as plt
from itertools import combinations, product, permutations
from shapely import Point, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import nearest_points, split,unary_union
import math
import copy
import random

from typing import List, Union, Optional, Tuple

#random.seed(24)  #500,at single scale,24 is good

class cost:

    def __init__(self,lines,visualize=False):

        self.visualize = visualize

        if len(lines) == 1:
            self.cost = None
        elif len(lines) == 2:
            self.cost = self.simple_cost(lines)
        else:
            self.cost = self.complex_cost(lines)

    def get_cost(self):
        return self.cost

    def simple_cost(self,lines):
        
        inter = lines[0].intersection(lines[1])

        if not inter.is_empty:
            return None
        else:
            return LineString(nearest_points(lines[0],lines[1]))
        
    
    def complex_cost(self,lines):

        self.lines = lines

        self.construct_outer_bounds()

        self.split = self.split_polygon(self.lines, self.slimmed)

        self.classify_bounds()

        self.differences = self.get_difference(self.convex_polygon,self.slimmed)

        if not self.differences is None:
            old = self.slimmed
            for pol in self.differences:
                self.slimmed = self.slimmed.difference(pol)
            if self.slimmed.geom_type != "Polygon":
                self.slimmed = old


        self.valid = []
        self.invalid = []
        self.min_valid = None
        self.attempts = []

        

        self.outer_solve()
        

        if self.visualize or self.min_valid is None:

            self.plot_state()
            plt.axis('equal') 
            plt.show()

        return self.min_valid



    def construct_outer_bounds(self):

        #CONVEX HULL
        self.convex_polygon = MultiLineString(self.lines).convex_hull
       
        #SLIMMED
        self.slimmed = copy.deepcopy(self.convex_polygon)
        for line1, line2 in combinations(self.lines,2):
            perspective = self.obtain_perspective_outward(line1,line2)
            self.slimmed = self.slimmed.intersection(perspective)

        #No Solution
        if self.slimmed.is_empty:
            print("NO SOLUTION POSSIBLE")

        #Multiple Parts
        elif self.slimmed.geom_type == "MultiPolygon" or self.slimmed.geom_type == "GeometryCollection":

            largest = []
            for geom in self.slimmed.geoms:
                if geom.geom_type == "Polygon":
                    largest.append(geom)

            if len(largest) == 1:
                self.slimmed = largest[0]
            else:
                print(f"MULTI CASE: {self.slimmed}")
                print(f" MULTI POL: {largest}")
                self.slimmed = Polygon(largest)

    def obtain_perspective_outward(self,line1,line2):
        
        lp = self.get_coords(line1)
        rp = self.get_coords(line2)

        total = old = MultiLineString([line1,line2]).convex_hull

        #First Triangle (Extends From L0 Passes Through R0,R1)
        p1 = self.get_extended(rp[0],lp[0],5000000)
        p2 = self.get_extended(rp[1],lp[0],5000000)

        t1 = Polygon([p1,p2,lp[0]])

        #Second Triangle (Extends From L1 Passes Through R0,R1)
        p1 = self.get_extended(rp[0],lp[1],5000000)
        p2 = self.get_extended(rp[1],lp[1],5000000)

        t2 = Polygon([p1,p2,lp[1]])

        #Third Triangle (Extends From R0 Passes Through L0,L1)
        p1 = self.get_extended(lp[0],rp[0],5000000)
        p2 = self.get_extended(lp[1],rp[0],5000000)

        t3 = Polygon([p1,p2,rp[0]])

        #Second Triangle (Extends From L1 Passes Through R0,R1)
        p1 = self.get_extended(lp[0],rp[1],5000000)
        p2 = self.get_extended(lp[1],rp[1],5000000)

        t4 = Polygon([p1,p2,rp[1]])


        if line1.intersects(line2): ##OR IS VERY CLOSE:
            total = self.convex_polygon
        else:

            left = t1.union(t2)
            right= t3.union(t4)

            total = total.union(left)
            total = total.union(right)

        return total


    def plot_polygon(self, item, color, fill=False,alpha=1,lw=1,text=None):

        if item is None:
            return
        elif isinstance(item,list):
            objects = item
        elif item.geom_type == "MultiPolygon" or item.geom_type == "GeometryCollection":
            objects = [g for g in item.geoms]
        else:
            objects = [item]

        
        for shape in objects:

            if shape.geom_type == "LineString":
                x,y = shape.xy
                plt.plot(x,y,color=color,lw=lw)

            else:
                x,y = shape.exterior.xy

                if fill:
                    plt.fill(x,y,color=color,alpha=alpha)
                else:
                    plt.plot(x,y,color=color,lw=lw)

            if not text is None:
                plt.text(x[0],y[0],s=f"{text}")
                plt.text(x[1],y[1],s=f"{text}")

            




    def plot_state(self):

        self.plot_polygon(self.convex_polygon, "black", True)

        self.plot_polygon(self.slimmed, "grey", True)


        


        self.plot_polygon(self.keys, "green", True, lw=3)

        self.plot_polygon(self.differences, "red", True,alpha=0.2)

        self.plot_polygon(self.lines, "blue")


        # for invalid in self.invalid:
        #     x,y = invalid.xy
        #     plt.plot(x,y,color="yellow")

        # for valid in self.valid:
        #     x,y = valid.xy
        #     plt.plot(x,y,color="orange")

        
        if self.min_valid is None:
            plt.title(f"NO MIN COST FOUND {len(self.lines)}")
        else:
            x,y = self.min_valid.xy
            plt.plot(x,y,color="black")




        

        
    def classify_bounds(self):

        self.convex_edges = self.get_edges(self.convex_polygon)
        self.slimmed_edges = self.get_edges(self.slimmed)

        self.slimmed_exterior = []
        self.slimmed_interior = []

        self.keys = []

        #######hard_lines = set()

        for slimmed_edge in self.slimmed_edges:
            for convex_edge in self.convex_edges:

                #EXTERIOR
                if self.is_intersecting(slimmed_edge,convex_edge):
                    self.slimmed_exterior.append(slimmed_edge)

                    for line in self.lines:
                        #HARD EDGE
                        if self.is_intersecting(slimmed_edge,line):
                            self.keys.append(slimmed_edge)
                            #hard_lines.add(line)
                            break

                    continue

            #INTERIOR
            if slimmed_edge not in self.slimmed_exterior:
                self.slimmed_interior.append(slimmed_edge)
                

        #number = 0
        #print("---------------------------------")
        for partial_polygon in self.split:

            partial_edges = self.get_edges(partial_polygon)

            key_exterior = []
            other_exterior = []

            for partial_edge in partial_edges:


                for exterior_edge in self.slimmed_exterior:

                    if self.is_intersecting(partial_edge,exterior_edge):

                        if exterior_edge in self.keys:
                            key_exterior.append(exterior_edge)
                        else:
                            other_exterior.append(exterior_edge)

            #SOFT
            if len(other_exterior) == 1 or (len(other_exterior) > 1 and self.join_parellel(other_exterior)):

                self.keys.append(partial_polygon)
            #else:
                #print(other_exterior)


        # for line in self.lines:
        #     if not line in hard_lines:
        #         self.keys.append(line)

        

    def join_parellel(self,edges):

        for e1,e2 in combinations(edges,2):

            c1, c2 = self.get_coords(e1)
            c3, c4 = self.get_coords(e2)

            full1 = LineString([c1,c4])
            full2 = LineString([c2,c3])


            if (self.is_intersecting(e1,full1) and self.is_intersecting(e2,full1)) or \
                (self.is_intersecting(e1,full2) and self.is_intersecting(e2,full2)):
                continue
            else:
                return False
        return True
     

    def split_polygon(self,slicer,polygon,allow_linestring=False):

        splits = [polygon]

        for linestring in slicer:

            if linestring.length == 0:
                continue

            coords = self.get_coords(linestring)
            #print(f" COORDS: {coords}")

            far_beyond_c0 = self.get_extended(coords[0],coords[1],100)
            far_beyond_c1 = self.get_extended(coords[1],coords[0],100)

            #print(f" {far_beyond_c0} {far_beyond_c1}")

            infinite_linestring = LineString([far_beyond_c0,coords[0],coords[1],far_beyond_c1])
                
            new_result = []

            for split_pol in splits:
                split_result = split(split_pol, infinite_linestring)
                if allow_linestring:
                    new_result.extend([geom for geom in split_result.geoms if geom.geom_type != "Point"])
                else:
                    new_result.extend([geom for geom in split_result.geoms if geom.geom_type == "Polygon"])
            
            if len(new_result) == 0:

                for sp in splits:
                    if sp.geom_type == "LineString":
                        x,y = sp.xy
                    else:
                        x,y = sp.exterior.xy

                    plt.plot(x,y,color="green")
                
                    x,y = infinite_linestring.xy
                    plt.plot(x,y,color="blue")

                    plt.show()

            splits = new_result
        return splits

    def get_difference(self,outer,inner):


        diff = outer.difference(inner.buffer(1e-10))

        inner_coords = self.get_coords(inner)

        if diff.is_empty or diff.geom_type == "LineString":
            return None
        
        elif diff.geom_type == "Polygon":
            skewed = [diff]
        else:
            skewed = [d for d in diff.geoms]


        good_polygons = []

        for skewed_polygon in skewed:

            convexed = skewed_polygon.convex_hull

            good_coords = []

            for convexed_coord in self.get_coords(convexed):

                done = False

                for compare in inner_coords:

                    if self.is_intersect(convexed_coord,compare):
                        good_coords.append(compare)
                        done = True
                        break
                if not done:
                    good_coords.append(convexed_coord)
            
            good_polygons.append(Polygon(good_coords))

        return good_polygons        



    def get_probable_range(self,pol,pol2):
        p1_coords = self.get_coords(pol)
        p1_lines = []
        for p1_coord in p1_coords:
            p1_lines.append(LineString(nearest_points(p1_coord,pol2)))
        
        p1_new = MultiLineString(p1_lines).convex_hull

        return p1_new
    
    def find_ideal_slope(self,pol1,pol2):

        pr1 = self.get_probable_range(pol1,pol2)
        pr2 = self.get_probable_range(pol1,pol2)

        intersection = pr1.intersection(pr2)

        c1,c2 = nearest_points(pol1,pol2)

        return intersection, (c2.x - c1.x, c2.y - c1.y)

        
    
    def outer_solve(self):


        for pol1,pol2 in combinations(self.keys,2):
            self.inner_solve(pol1,pol2)


        for att in self.attempts:

            if self.is_valid(att):
                self.valid.append(att)

                if self.min_valid is None or self.min_valid.length > att.length:
                    self.min_valid = att
            else:
                self.invalid.append(att)


    def inner_solve(self,pol1,pol2):

        if self.is_intersect(pol1,pol2):
            return None
        else:
            

            intersection, slope = self.find_ideal_slope(pol1,pol2)

            blockers = self.get_difference(intersection, self.slimmed)

            pure = LineString(nearest_points(pol1,pol2))

            if blockers is None:
                #print("   No Blockers")
                self.attempts.append(pure)
            else:
                #print("   Blockers")

                blocker_found = None

                for blocker in blockers:
                    
                    inter = pure.intersection(blocker.buffer(1e-2))
                    #Best Line Is Blocked
                    if not inter.is_empty and inter.geom_type == "LineString" and inter.length > 01e-2:
                        blocker_found = blocker
                        break

                #Best Line Avoids Blocks
                if blocker_found is None:
                    #print(f"   Blockers Can Be Avoided:")
                    self.attempts.append(pure)
                

                #Best Line Contains Blocks
                else:
                    #print(f"  Best Case Scenario Blocked")


                    difference_not_within = None
                    for difference in self.differences:
                        if self.is_intersect(difference, blocker_found):
                            difference_not_within = difference.difference(blocker_found)
                            break


                    blocker_coords = self.get_coords(blocker_found)

                    print(f" BLOCKER COORDS: {blocker_coords}")

                    for blocker_coord in blocker_coords:
                        print(f" BLOCKER COORD TRYING: {blocker_coord}")
                            
                        attempt = LineString([self.get_extended(blocker_coord, Point(blocker_coord.x + slope[0], blocker_coord.y + slope[1]),50),
                                                  self.get_extended(blocker_coord, Point(blocker_coord.x - slope[0], blocker_coord.y - slope[1]),50)])
                            
                        pol1_closest = pol1.intersection(attempt)
                        pol2_closest = pol2.intersection(attempt)

                        if not pol1_closest.is_empty and not pol2_closest.is_empty:

                            attempt = LineString(nearest_points(pol1_closest,pol2_closest))

                        
                        #INTERSECTS ALL
                        if self.is_valid(attempt):
                            print(f"ATTEMPT: {attempt} IS VALID")
                            pass
                        else:
                            print(f" ATEMPT: {attempt} GOING INTO")
                            not_toucing_count = 0
                            not_touching = None

                            for line in self.lines:
                                if not self.is_intersect(line, attempt, dist=1e-2):
                                    not_toucing_count += 1
                                    not_touching = line

                            #IF ONE NOT TOUCHING, ATTEMPT TO EXTEND RANGE TO IT
                            if not_toucing_count == 1:

                                closest_2, __ = nearest_points(not_touching, attempt)

                                attempt = LineString([self.get_extended(closest_2, Point(closest_2.x + slope[0], closest_2.y + slope[1]),50),
                                                  self.get_extended(closest_2, Point(closest_2.x - slope[0], closest_2.y - slope[1]),50)])
                                
                                pol1_closest = pol1.intersection(attempt)
                                pol2_closest = pol2.intersection(attempt)

                                if not pol1_closest.is_empty and not pol2_closest.is_empty:
                                    attempt = LineString(nearest_points(pol1_closest,pol2_closest))

                        self.attempts.append(attempt)


                        #IF ITS NOT VALID, MOVE TO NEAREST LOCATION CONTAINING POINT NOT COVERED 
                            
                    


    

    def get_edges(self, polygon):
        coords = list(polygon.exterior.coords)
        size = len(coords) - 1
        return {LineString([coords[i], coords[i + 1]]) for i in range(size) if LineString([coords[i], coords[i + 1]]).length>1e-3}
    
    def get_coords(self,polygon):

        if polygon.geom_type == "LineString":
            return [Point(p) for p in polygon.coords]
        
        else:
            return [Point(p) for p in polygon.exterior.coords]
    
    def get_extended(self,start,end,length):        
        
        dx = start.x - end.x
        dy = start.y - end.y
        v = math.sqrt(dx*dx + dy*dy)

        if v != 0:
            return Point(length*(dx/v) + start.x, length*(dy/v) + start.y)
        else:
            #print("ERROR: SAME POINT")
            return None

    def is_intersecting(self,line,polygon):
        c1,c2 = self.get_coords(line)
        return self.is_intersect(c1,polygon) and self.is_intersect(c2,polygon)


    def is_intersect(self,polygon1,polygon2,dist=1e-7):
        return (polygon1.intersects(polygon2) or polygon1.distance(polygon2)<dist)

    def is_valid(self,cost:LineString) -> bool:   
        """
        Determine Whether Cost Represents A Valid Cost
        """
        for line in self.lines:
            if not self.is_intersect(cost,line,dist=1e-2):
                return False
        return True




        
