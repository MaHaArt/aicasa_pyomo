# pyomo

in neuem Conda Environment

    conda install -c conda-forge pyomo

install glpk

    conda install -c conda-forge glpk
    glpsol --version

ipopt

NICHT:
conda install -c conda-forge ipopt

https://github.com/mechmotum/cyipopt/blob/master/docs/source/install.rst

mit MA27

    sudo apt-get install gcc g++ gfortran git patch wget pkg-config liblapack-dev libmetis-dev


    wget https://www.coin-or.org/download/source/Ipopt/Ipopt-3.14.4.tar.gz

    tar -xvf Ipopt-3.14.4.tar.gz

    export IPOPTDIR=~/Ipopt-releases-3.14.4

jetzt HSL

    https://www.hsl.rl.ac.uk/ipopt/

    tar -xvf coinhsl-archive-2021.05.05.tar.gz 

    git clone https://github.com/coin-or-tools/ThirdParty-HSL.git
    cd ThirdParty-HSL

Now unpack the HSL sources archive, move and rename the resulting directory so that it becomes ThirdParty-HSL/coinhsl.
Then, in ThirdParty-HSL, configure, build, and install the HSL sources:

    ./configure
    make
    sudo make install

    ?? Rename the extracted folder to coinhsl and copy it in the HSL folder: Ipopt-3.12.11/ThirdParty/HSL

# Objective function

minimize (u_i,1 (x_i + y_i ) + u_i_2 Σ AbsoluteDistance - u_i_3 Σ ApproximateArea room i

Bestandteile:

* u_i,1 (x_i + y_i ) - Entfernung Raum i von der oberen linken Ecke - sollte das nicht Eingang sein?
* u_i_2 Σ AbsoluteDistance - aufbauend auf Manhattan Norm jeweils für alle Paare i,j mit i < j:p_i,j( abs(x_i - x_j)  +
  abs(y_i + y_j) )

  hier müssen wir auch noch z berücksichtigen

p_i,j: Kommunikationskosten zwischen Raum i und j , kann negativ sein, für Räume die wir nicht im Zusammenhang haben
wollen

Berechnung Summe i:1 .. N-1, Summe j: i+1 .. N

* u_i_3 Σ ApproximateArea

# Constraints

* Construct dictionaries

  con1 = {'type':'ineq','fun':constraint1}

  con2 = {'type':'ineq','fun':constraint2}

  con3 = {'type':'eq','fun':constraint3}

* Put those dictionaries into a tuple

  cons = (con1,con2,con2)

## Area

für alle i: w_i * h_i > a_i

- h_i + a_i / w_i <= 0
- w_i + a_i / h_i <= 0

## Aspect ratio

alpha_i: ratio w/h a_i: fläche Raum i

* max(lx/ly, ly/lx) < Beta

* upper bounds für weite und höhe h-up_i, w-up_i h-up_i = w-up_i --> alpha_i * ai_i >= sqr(w_i)

## non overlap

Instead of a binary variable δ ∈ {0,1} use a continuous variable δ ∈ [0,1] and add the constraint δ(1-δ)=0. Typically
will get stuck ...

f_or = - xy (x and y <0), xy otherwise, x und y sind die Terme der Ungleichung zum Überlapp

# descriptions

## 1st floor

* all the spaces of the first floor are adjacent to the corridor with 1 meter minimum for contact length,
* the kitchen and the living room are adjacent with 1 meter minimum for contact length,
* the kitchen is on the south wall or on the north wall of the building contour,
* the kitchen and the Toilet/Shower-unit are adjacent,
* the living room is on the south wall of the building contour,

# Methode

## scipy

https://scipy-lectures.org/advanced/mathematical_optimization/#choosing-a-method

In general, prefer BFGS or L-BFGS, even if you have to approximate numerically gradients. These are also the default if
you omit the parameter method - depending if the problem has constraints or bounds On well-conditioned problems, Powell
and Nelder-Mead, both gradient-free methods, work well in high dimension, but they collapse for ill-conditioned
problems.

## Deep Learning

Surprisingly, I found a relatively ok solution using an optimizer from for a deep learning framework, Tensorflow, using
basic gradient descent (actually RMSProp, gradient descent with momentum) after I changed the cost function to include
the inequality constraint and the bounding constraints as penalties (I suppose this is same as lagrange method). It
trains super fast and converges quickly with proper lambda parameters on the constraint penalties. I didn't even have to
rewrite the jacobians as TF takes care of that without much speed impact apparently.

Before that, I managed to get NLOPT to work and it is much faster than scipy/SLSQP but still slow on higher dimensions.

## Constraints

* Equality ist immer gleich 0
* Inequality ist >= 0

# Postprocessing

* Removal of holes During the initial generation stage, the rooms are described as rectangles which can introduce the
  empty spaces
  (holes) between them. The removal of holes is done by adding their surface to adjacent rooms (see exam- ple on Figure
  6). The hole can take the shape of an orthogonal polygon with an even number of sides, greater than or equal to 4 -
  the simplest form is a rectangle. In case of a higher degree of complexity (Ueckerdt, 2011), there is a need to divide
  such polygons into basic constituent shapes - rectangles. To obtain optimal rectilinear decomposition of polygons, the
  authors used an algorithm based on bipartite match- ing algorithm (Suk, Höschl and Flusser, 2012) based on the [3]
  implementation. The algorithm returns a list of rectangles that decompose surface of a poly- gon to the smallest
  number of non-overlapping rect- angles. After simplification of hole shapes, the rect- angle surfaces are assigned to
  adjacent rooms.

* Simplification of the layout boundary. The second type of post processing operation is designed to re- duce the
  complexity of the floor outline making it more regular and takes place at the user’s request
  (see an example on Figure 7). The algorithm focus on combining the neighbouring, parallel edges of the layout boundary
  polygon. --> Die Aussenhülle begradigen!

# Criteria

* Solar: To place the rooms in the optimum place and orientation in relation to the sun. Objective: To assure natural
  illumination to the largest amount of rooms of long stay. Unit: vector.
* Views: To place the spaces in the optimum place and orientation in relation to the views. Objective: To assure the
  best views of the landscape or the surroundings to the long-stay rooms. Unit: vector.
* Accessibility: Referred to the distance between the main street (or street of access) and the entrance of the
  building. Objective: To minimize the distance to access the building. Unit: m (meters).
* Related Functions: Some functions of the Space Program are more related to each other than others. Objective: To
  establish which rooms are highly, fairly or scarcely related, and which room should be away from the rest. Unit:
  factor.
* Minimum distance: The objective is to establish the minimum distance between rooms to optimize the circulation spaces.
  Unit: m (meters).
* Efficiency (Circulation/Usable Ratio - Circulation): The result of comparing the circulation surface with the usable
  surface. Objective: To keep most of the surface for use and little surface for circulation. Unit:
  percentage.
* Efficiency (Volume/Usable): The result of comparing the volume of each space with the usable volume of it. Objective:
  To keep most of the volume for use and less unusable volume. Other aspects such as the sun and the ventilation could
  have an influence on this variable. Unit: Percentage.
* Size: The size of the room (width x length x height) refers to some size pattern or standards based on the building
  type (hotels, schools, housing).

General

* Geometric Composition: The rooms must be inside a larger geometric form (square, circle, arc, rectangles, etc.), sized
  and grouped following aesthetic intentions.

* The Divine Proportion/Golden Ratio: The wall distribution follows the sides of a rectangle, and the lengths of both
  sides of the rectangle follow a fixed numerical relationship (1.6180339887). It is possible to measure it.

* 3d Shape to Fill: Ching (1979) defines the possible configurations of space distributions as: Linear, Central, Yard, U
  Shape, L Shape, Organic Shape, Religious Shapes.

* Sustainable Criteria: The space distribution should be optimum regarding sustainable criteria such as minimal surface
  in perimeter walls, energy consumption, solar gain in surfaces, material quantification, room light load, etc.

* Others: Economical, structural and spiritual meanings (FengShui, Mapuches); construction techniques.

# Objekte

## Räume

* Hall
* Corridor
* Kitchen
* LivingRoom
* WC
* Bathroom
* DiningRoom
* Pantry (Speisekammer)
* DoubleBedroom
* SingleBedroom
* DoubleGarage
* SingleGarage
* Staircase

## Zonen

Zuordnung Räume zu Zonen

* DayZone
* NightZone
* Communication
* Utility

# Speedup

## numba

https://numba.readthedocs.io/en/stable/user/installing.html
