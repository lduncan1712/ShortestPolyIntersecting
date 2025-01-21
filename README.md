# ShortestPolyIntersecting

## A Mini-Project To Determine The Shortest LineString That Intersects A Set Of Lines In A 2D Plane

### NOTE: Geometrically, there are cases of 3+ lines where no solution is possible, 


#### As The Returned Line (Black) Is The Shortest Intersecting Line Possible, Its Endoints Occur Either On One Of The Lines, Or The Intersection Of Multiple Lines

<img src="https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20213842.png" alt="Example 1" width="500">
<img src="https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20214300.png" alt="Example 2" width="500">


## Setup + Usage:
#### Takes In A List Of Shapely LineStrings, Returns Either A LineString, Point, or None
```
  cost(lines, visualize=False)
```
#### Provides An Optional "Visualize" Argument That Visualizes The Process (Also visualizes when no solution is found) For Cases That Might Appear Confusing
- Orange: Valid Solutions
- Yellow: Invalid Solutions
- Black: Best Solution
- Green: Possible Outer Polygons
- Red: Invalid Outer Polygons

![Example 3](https://github.com/lduncan1712/ShortestPolyIntersecting/blob/main/visuals/Screenshot%202025-01-20%20220801.png)


### FINAL NOTES:
### This was built as part of my "LocEstimation" Repository, and as such was built for cases of 2-8 non infinite linestrings, approximately the same length. 
### It is possible that there are geometric cases of line relative location that I have not yet encountered. Specifically, I suspect cases where a line is fully within the convexed polygon, might cause problems.
### Additionally, shapely is float based, meaning i experienced alot of problems of loss of percision even between shapely operations, for this reason, you will note ive re-implemented several functions relating to intersections



