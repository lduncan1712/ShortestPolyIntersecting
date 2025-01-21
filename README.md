# ShortestPolyIntersecting

## A Mini-Project To Determine The Shortest LineString That Intersects A Set Of Lines In A 2D Plane

### NOTE: Geometrically, there are cases of 3+ lines where no solution is possible, 


#### As The Returned Line Is The Shortest Intersecting Line Possible, Its Endoints Occur Either On One Of The Lines, Or The Intersection Of Multiple Lines








### Algorithm:
- Determine All Polygons That Could Contain Outer Edges Of Line (green)
- Determine The Ideal Slope Of Line Between Them
  - If This Line Isnt Broken By Blocker (red): use it
  - Otherwise: move to the vertice of Blocker and extend line from there
- Return Smallest Such Line That Is Confirmed To Intersect All Lines


