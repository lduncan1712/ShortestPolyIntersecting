# ShortestPolyIntersecting

## A Mini-Project To Determine The Shortest LineString That Intersects A Set Of Lines In A 2D Plane

### NOTE: Geometrically, there are cases of 3+ lines where no solution is possible, 


#### As The Returned Line Is The Shortest Intersecting Line Possible, Its Endoints Occur Either On One Of The Lines, Or The Intersection Of Multiple Lines


![Example 1](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20213842.png)
![Example 3](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20214300.png)



### Algorithm:
- If 1 Line: return None
- If 2 Lines:
  - If they intersect: return point of intersection
  - If not return line bounded by nearest points on either
- Create A Convex Hull Of The Lines ("Outer" Polygon)
- Remove Area From Outer That Any Line Going Through Cannot Geometrically Intersect All Other Lines (Red)
- This Leaves An "Inner" Polygon, All Of Whose Outer Edges Touching The Convexed Polygon Could Contain A Line Intersecting All
- Determine All Polygons That Could Contain Outer EndPoints Of Shortest Line:
    - Any Edges In Inner Overlapping Lines
    - Any Polygons Bounded By "Inner" Polygons Outer Edge, And One Or More Lines
- For All Combinations Of These Possible Endpoint Polygons:
    - Determine The Ideal Slope Of A Line Between Them
    - If This Line Isnt Intersected By Invalid Area (red), use it
    - Otherwise, Move To Each Vertice Of Red, And Extend Slope From It
    - If this line doesnt intersect (1) other line, point to its closest point and extend the slope outwards from it
    - Add Valid Lines Given As Attempts
- Given All Attempts:
    - Return the shortest, if exists



### Setup + Usage:
#### Takes In A List Of Shapely LineStrings, Returns Either A LineString, Point, or None
```
  cost(lines, visualize=False)
```
#### Provides An Optional "Visualize" Argument That Visualizes The Process (Also visualizes when no solution is found) For Cases That Might Appear Confusing

![Example 3](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%2022801.png)


### FINAL NOTES:
### This was built as part of my "LocEstimation" Repository, and as such was built for cases of 2-8 non infinite linestrings, approximately the same length. It is possible that there are geometric cases of line relative location that I have not yet encountered.



