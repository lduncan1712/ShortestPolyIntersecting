import matplotlib.pyplot as plt
from itertools import combinations, product, permutations
from shapely import Point, LineString, MultiLineString, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import nearest_points, split,unary_union
import math
import copy
import random
from typing import List, Union, Optional, Tuple

"""
A Class Used To Determine The Shortest LineString That Intersects All Applied LineStrings
Where Solution Is Possible
"""
class cost:

    """
    Create A Cost Object

    Args:
        lines: the lines to attempt to find intersecting line of
        visualize: whether to visualize the problem
    """
    def __init__(self,lines: List[LineString],visualize:bool=False) -> None:

        self.visualize = visualize

        #Single Line: Nothing To Solve
        if len(lines) == 1:
            self.cost = None

        #Multi Lines: Solve Required
        else:

            simple_solution = self.simple_case(lines)

            #If All Lines Converge To A Point
            if not simple_solution is None:
                self.cost = simple_solution

            #2 Non Intersecting Lines
            elif len(lines) == 2:
                self.cost = LineString(nearest_points(lines[0],lines[1]))

            #3+ Non Intersecting Lines
            else:
                self.cost = self.complex_cost(lines)


    """
    Determines Whether All Lines Intersect At A Point (approximately)

    Args:
        lines: the list of lines to determine if intersecting
    
    Returns:
        None if no total intersection, otherwise intersecting point
    """
    def simple_case(self, lines: List[LineString]) -> Optional[Point]:

        inter_list = None

        #For Every Combination
        for line1, line2 in combinations(lines,2):

            #It Needs To Intersect
            if self.is_intersect(line1,line2):
                inter = line1.intersection(line2)

                #First Case
                if inter_list is None:
                    inter_list = inter
                else:
                    #Otherwise This Intersect Needs To Intersect With Previous Intersection
                    if not inter_list.distance(inter) < 1e-10:
                        return None
            else:
                return None
        return inter_list


    """
    A Getter To Return The Final Solution

    Returns:
        The Polygons Representing The Shortest Intersecting
    """
    def get_cost(self) -> Optional[Union[LineString, Point]]:
        print(self.cost)
        return self.cost

            
        
    """
    Returns The Shorest Solution For 3+ LineStrings If Possible

    Args:
        lines: the LineStrings to find intersections for

    Returns:
        The Solution If Exists
    """
    def complex_cost(self,lines: List[LineString]) -> Optional[Union[LineString,Point]]:

        print("INITIALING COMPLEX")
        print("---------------------------------")

        #Storing The Lines
        self.lines = lines

        #Determine The Convex Minus Useless Area Polygon
        if not self.construct_outer_bounds():
            print(" -- Not Possible")
            return None


        #Split The Polygon Into Outer Chunks
        self.split = self.split_polygon(self.lines, [self.slimmed])

        




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


    """
    Determines The Outer Bounds Polygons For Our Shortest LineString;
    The Convex Hull Of The Lines, Subtracting The Area Not Possible To Intersect All Lines

    Returns:
        whether this polygon exists
    """
    def construct_outer_bounds(self) -> bool:

        #CONVEX HULL
        self.convex_polygon = MultiLineString(self.lines).convex_hull
       
        #SLIMMED: Removing Area That Cant Be A Solution
        self.slimmed = copy.deepcopy(self.convex_polygon)
        for line1, line2 in combinations(self.lines,2):
            perspective = self.obtain_perspective_outward(line1,line2)
            self.slimmed = self.slimmed.intersection(perspective)


        #No Solution
        if self.slimmed.is_empty:
            return 0

        #Multiple Parts
        elif self.slimmed.geom_type in ["MultiPolygon", "GeometryCollection"]:

            largest = sorted([geo for geo in self.slimmed.geoms if geo.geom_type == "Polygon" and geo.area>1e-10], 
                                key=lambda polygon: polygon.area, reverse=True)
            
            #CONFLICT CASE 1
            if len(largest) != 1:
                print(f"--MULTI CASE: {largest}")
                self.plot_polygon(self.slimmed, "green", True)
                self.plot_polygon(self.slimmed, "red", False)
                plt.show()
            else:
                self.slimmed = largest[0]
                return 1
        
        #Single Part Normal Case
        else:
            return 1
            
    """
    Given 2 Lines, Determines All Area Within A Radius That Any LineString Passing Through
    Some Points On Both Could Touch

    Args:
        line1: the first line
        line2: the second line

    Returns:
        the polygon representing this area
    """
    def obtain_perspective_outward(self,line1:LineString,line2:LineString) -> Polygon:
        
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

    """
    Given An Object Or List Of Them, Plots Each Using The Applied Parameters

    Args:
        item: the shapely polygon, or list to plot
        color: the color to make it
        fill: whether to plot the filled
        alpha: the darkness of filled plot
        lw: the linewidth for lines
        text: an optional label
    """
    def plot_polygon(self, item: Union[List,Polygon,LineString], color, fill=False,alpha=1,lw=1,text=None) -> None:

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
   
    """
    Plots The State Of Our Solving, Including Various Components
    """
    def plot_state(self) -> None:

        self.plot_polygon(self.convex_polygon, "black", True)

        self.plot_polygon(self.slimmed, "grey", True)

        self.plot_polygon(self.keys, "green", True, lw=3)

        self.plot_polygon(self.differences, "red", True,alpha=0.2)

        self.plot_polygon(self.lines, "blue")


        for invalid in self.invalid:
            x,y = invalid.xy
            plt.plot(x,y,color="yellow")

        for valid in self.valid:
            x,y = valid.xy
            plt.plot(x,y,color="orange")

        
        if self.min_valid is None:
            plt.title(f"NO MIN COST FOUND {len(self.lines)}")
        else:
            x,y = self.min_valid.xy
            plt.plot(x,y,color="black")


    """
    Classifies Key Information About The Polygon
    """
    def classify_bounds(self):

        self.convex_edges = self.get_edges(self.convex_polygon)
        self.slimmed_edges = self.get_edges(self.slimmed)

        self.slimmed_exterior = []
        self.slimmed_interior = []
        self.keys = []
        self.inner_points = []


        #DETERMINING INNER POINTS
        for line in self.lines:
            for p in self.get_coords(line):
                if self.is_intersect(p, self.convex_polygon.boundary):
                    self.inner_points.append(p)


        #DETERMINING HARD EDGES
        for slimmed_edge in self.slimmed_edges:
            for convex_edge in self.convex_edges:

                #EXTERIOR
                if self.is_intersecting(slimmed_edge,convex_edge):
                    self.slimmed_exterior.append(slimmed_edge)

                    # for line in self.lines:
                    #     #HARD EDGE
                    #     if self.is_intersecting(slimmed_edge,line):
                    #         self.keys.append(slimmed_edge)
                    #         break

                    # continue

            #INTERIOR
            if slimmed_edge not in self.slimmed_exterior:
                self.slimmed_interior.append(slimmed_edge)


        #ALL REDUNDANCY
        for line in self.lines:
            self.keys.append(line)
                
        #DETERMINING SOFT EDGES
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

        
    """
    Determines Whether Every Edge Within A List Is Parellel

    Args:
        edges: the linestrings to determine whether parellel

    Returns:
        bool: whether all parellel
    """
    def join_parellel(self,edges:List[LineString]):

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
     

    """
    Splits A Polygon By A Set of Infinite LineStrings

    Args:
        slicer: the lines to split using
        polygon: the polygon to split
        allow_linestring: whether to keep linestring pieces

    Return:
        the list of Polygon pieces
    """
    def split_polygon(self,slicer: List[LineString],polygon:List[Polygon],allow_linestring=False) -> List[Union[LineString,Polygon]]:

        splits = polygon

        for linestring in slicer:

            if linestring.length == 0:
                continue

            coords = self.get_coords(linestring)
            

            far_beyond_c0 = self.get_extended(coords[0],coords[1],100)
            far_beyond_c1 = self.get_extended(coords[1],coords[0],100)

            infinite_linestring = LineString([far_beyond_c0,coords[0],coords[1],far_beyond_c1])
                
            new_result = []

            for split_pol in splits:
                split_result = split(split_pol, infinite_linestring)
                if allow_linestring:
                    new_result.extend([geom for geom in split_result.geoms if geom.geom_type != "Point"])
                else:
                    new_result.extend([geom for geom in split_result.geoms if geom.geom_type == "Polygon"])

            splits = new_result
        return splits


    """
    Determines The Area In Outer Not Within Inner, With Slight Buffer To Accomadate Slight Error

    Args:
        outer: the polygon who different area is kept
        inner: the polygon whose area is removed

    Return:
        a list of the polygons making up the difference
    """
    def get_difference(self,outer:Polygon,inner:Polygon) -> Optional[List[Polygon]]:


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


    """
    A Polygon Defined By The Intersection Of The Polygons Created By Finding The Nearest Points
    On the other polygon, extending from each of their respective vertices

    Args:
        pol1: the first polygon
        pol2: the second polygon

    Returns:
        the Polygon representing the range between them
    """
    def get_probable_range(self,pol:Union[Polygon,LineString],pol2:Union[Polygon,LineString]) -> Polygon:
        p1_coords = self.get_coords(pol)
        p1_lines = []
        for p1_coord in p1_coords:
            p1_lines.append(LineString(nearest_points(p1_coord,pol2)))
        
        p1_new = MultiLineString(p1_lines).convex_hull

        return p1_new
    
    """
    Given 2 Polygons, Find The Shortest Slope For A Line Between Them

    Args:
        pol1: the first polygon
        pol2: the second polygon

    Returns:
        list containing slope of (x,y) dimension
    
    """
    def find_ideal_slope(self,pol1:Union[Polygon,LineString],pol2:Union[Polygon,LineString]) -> List:

        pr1 = self.get_probable_range(pol1,pol2)
        pr2 = self.get_probable_range(pol1,pol2)

        intersection = pr1.intersection(pr2)

        c1,c2 = nearest_points(pol1,pol2)

        return intersection, (c2.x - c1.x, c2.y - c1.y)

    """
    Solves Each Possible Polygon Combination That Could Contain Shortest Endpoints
    """
    def outer_solve(self):

        #Each Combination
        for pol1,pol2 in combinations(self.keys,2):
            self.inner_solve(pol1,pol2)

        #Marks Attempts
        for att in self.attempts:

            if self.is_valid(att):
                self.valid.append(att)

                if self.min_valid is None or self.min_valid.length > att.length:
                    self.min_valid = att
            else:
                self.invalid.append(att)


    "Solves A Combination"
    def inner_solve(self,pol1,pol2):

        #If They Intersect, No Line needed
        if self.is_intersect(pol1,pol2):
            return None
        else:
            
            #Smaller Suggested Polygon + Ideal Slope
            intersection, slope = self.find_ideal_slope(pol1,pol2)

            #Polygons That Might Be In The Way
            blockers = self.get_difference(intersection, self.slimmed)
            
            #The Smallest Possible Attempt
            pure = LineString(nearest_points(pol1,pol2))

            #If No Blockers, Take Attempt
            if blockers is None:
                self.attempts.append(pure)
            
            #OtherWise Need To Check If Blockers Block
            else:
                
                blocker_found = None

                for blocker in blockers:
                    
                    inter = pure.intersection(blocker.buffer(1e-2))
                    #Best Line Is Blocked
                    if not inter.is_empty and inter.geom_type == "LineString" and inter.length > 01e-2:
                        blocker_found = blocker
                        break

                #Best Line Avoids Blocks
                if blocker_found is None:
                    
                    self.attempts.append(pure)
                
                #Best Line Contains Blocks
                else:
                    difference_not_within = None
                    for difference in self.differences:
                        if self.is_intersect(difference, blocker_found):
                            difference_not_within = difference.difference(blocker_found)
                            break


                    blocker_coords = self.get_coords(blocker_found)

                    #Attempt Positioning Slope From Every Blocker Coord
                    for blocker_coord in blocker_coords:
                        
                        attempt = LineString([self.get_extended(blocker_coord, Point(blocker_coord.x + slope[0], blocker_coord.y + slope[1]),50),
                                                  self.get_extended(blocker_coord, Point(blocker_coord.x - slope[0], blocker_coord.y - slope[1]),50)])
                            
                        pol1_closest = pol1.intersection(attempt)
                        pol2_closest = pol2.intersection(attempt)

                        #If Edge Polygon Not Lines: then take the closest point on the polygon
                        if not pol1_closest.is_empty and not pol2_closest.is_empty:

                            attempt = LineString(nearest_points(pol1_closest,pol2_closest))


                        
                        #CASE DEALING WITH INTERIOR LINES

                        
                        # #INTERSECTS ALL
                        # if self.is_valid(attempt):
                        #     pass
                        # else:
                            
                        #     not_toucing_count = 0
                        #     not_touching = None

                        #     for line in self.lines:
                        #         if not self.is_intersect(line, attempt, dist=1e-2):
                        #             not_toucing_count += 1
                        #             not_touching = line

                        #     #IF ONE NOT TOUCHING, ATTEMPT TO EXTEND RANGE TO IT
                        #     if not_toucing_count == 1:

                        #         closest_2, __ = nearest_points(not_touching, attempt)

                        #         attempt = LineString([self.get_extended(closest_2, Point(closest_2.x + slope[0], closest_2.y + slope[1]),50),
                        #                           self.get_extended(closest_2, Point(closest_2.x - slope[0], closest_2.y - slope[1]),50)])
                                
                        #         pol1_closest = pol1.intersection(attempt)
                        #         pol2_closest = pol2.intersection(attempt)

                        #         if not pol1_closest.is_empty and not pol2_closest.is_empty:
                        #             attempt = LineString(nearest_points(pol1_closest,pol2_closest))

                        self.attempts.append(attempt)
                    


    
    """
    Creates A List of Edges Within A Shapely Polygon, Over A Certain Length As Linestrings

    Args:
        polygon: the polygon whose edges to obtain

    Returns:
        the list of LineString edges
    """
    def get_edges(self, polygon:Polygon) -> List[LineString]:
        coords = list(polygon.exterior.coords)
        size = len(coords) - 1
        return {LineString([coords[i], coords[i + 1]]) for i in range(size) if LineString([coords[i], coords[i + 1]]).length>1e-3}
    
    """
    Obtaining Shapely Points Representing Each Coordinate In A Polygon

    Args:
        polygon: the linestring, or polygon to obtain coords of

    Returns:
        list of shapely points for the given polygon
    """
    def get_coords(self,polygon: Union[LineString,Polygon]) -> List[Point]:

        if polygon.geom_type == "LineString":
            return [Point(p) for p in polygon.coords]
        
        else:
            return [Point(p) for p in polygon.exterior.coords]
    
    """
    Extends A Line Defined By 2 Points In The Direction Of The First, By A Set Distance

    Args:
        start: the point to extend from
        end: the point through which the slope is determined
        length: the size of line extention

    Return:
        the new point if start and end arent equal, otherwise None
    """
    def get_extended(self,start:Point,end:Point,length:float) -> Optional[Point]:        
        
        dx = start.x - end.x
        dy = start.y - end.y
        v = math.sqrt(dx*dx + dy*dy)

        if v != 0:
            return Point(length*(dx/v) + start.x, length*(dy/v) + start.y)
        else:
            
            return None

    """
    Returns Whether Both EndPoints Of A LineString Approximately Intersect A Polygon

    Args:
        line: the line to check
        polygon: the polygon it must be touching

    Return:
        whether both points approximately touch
    """
    def is_intersecting(self,line:LineString,polygon:Polygon) -> bool:
        c1,c2 = self.get_coords(line)
        return self.is_intersect(c1,polygon) and self.is_intersect(c2,polygon)

    """
    Returns Whether 2 Polygons Approximately Intersect

    Args:
        polygon1, polygon2: the 2 polygons to check
        dist: the approximate distance required

    Returns:
        whether intersects
    """
    def is_intersect(self,polygon1:Union[Point,LineString,Polygon],polygon2:Union[Point,LineString,Polygon],dist:float=1e-7) -> bool:
        return (polygon1.intersects(polygon2) or polygon1.distance(polygon2)<dist)

    """
    Returns Whether A Given LineString Approximately Intersects All Lines

    Args:
        cost: a linestring

    Returns:
        whether valid
    """
    def is_valid(self,cost:LineString) -> bool:   
        for line in self.lines:
            if not self.is_intersect(cost,line,dist=1e-2):
                return False
        return True




        
