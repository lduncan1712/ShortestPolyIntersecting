# ShortestPolyIntersecting

## A Mini-Project To Determine The Shortest LineString That Intersects A Set Of Lines In A 2D Plane

### NOTE: Geometrically, there are cases of 3+ lines where no solution is possible, 


#### As The Returned Line Is The Shortest Intersecting Line Possible, Its Endoints Occur Either On One Of The Lines, Or The Intersection Of Multiple Lines


![Example 1](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20213842.png)
![Example 2](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20213843.png)
![Example 3](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20214300.png)



### Algorithm:
-If 1 Line: return None
-If 2 Lines:
  -If they intersect: return point of intersection
  -If not return line bounded by nearest points on either
- Create A Convex Hull Of The Lines ("Outer" Polygon)
- Remove Area From Outer That Any Line Going Through Cannot Geometrically Intersect All Other Lines (Red)
- This Leaves An "Inner" Polygon, All Of Whose Outer Edges Touching The Convexed Polygon Could Contain A Line Intersecting All
- Determine All Polygons That Could Contain Outher EndPoints Of Shortest Line:
    - Any Edges In Inner Overlapping Lines
    - Any Polygons Bounded By "Inner" Polygons Outer Edge, And One Of More Lines
- For All Combinations Of These Possible Endpoint Polygons:
    - Determine The Ideal Slope Of A Line Between Them
    - If This Line Isnt Intersected By Invalid Area (red), use it
    - Otherwise, Move To Each Vertice Of Red, And Extend Slope From It
    - Add Valid Lines Given As Attempts
- Given All Attempts:
    - Return the shortest, if exists



### Setup + Usage:
#### Takes In A List Of Shapely LineStrings, Returns Either A LineString, Point, or None


