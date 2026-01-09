# Mathematical Explanation of Human-Like Mouse Movement Algorithm

This document provides a **complete, step-by-step mathematical and
visual explanation** of how the `move_naturally` function computes
**Bezier curve control points** and moves the mouse in a human-like
manner.

Everything explained here corresponds directly to the code logic.

------------------------------------------------------------------------

## 1. What Problem Are We Solving?

Robotic mouse movement looks like this:

-   Constant speed
-   Straight lines
-   No curvature

Humans move a mouse like this:

-   Accelerate → cruise → decelerate
-   Slight curves
-   Small randomness

The solution used here is a **Cubic Bezier Curve**.

------------------------------------------------------------------------

## 2. XY Coordinate System

We use a standard XY graph:

-   X axis → horizontal
-   Y axis → vertical

Example values used throughout this explanation:

  Point   Meaning   Coordinates
  ------- --------- -------------
  S       Start     (100, 100)
  E       End       (400, 300)

------------------------------------------------------------------------

## 3. Step 1 -- Direction Vector (Straight Line)

From the code:

``` python
dx = x - start_x
dy = y - start_y
```

Calculation:

    dx = 400 - 100 = 300
    dy = 300 - 100 = 200

So the straight-line direction vector is:

    SE = (300, 200)

Distance between points:

    distance = sqrt(dx² + dy²)
             = sqrt(300² + 200²)
             = sqrt(130000)
             ≈ 360.56

------------------------------------------------------------------------

## 4. Step 2 -- Perpendicular Vector (Creates Curvature)

To avoid straight movement, a perpendicular vector is created:

``` python
px = -dy
py = dx
```

Calculation:

    px = -200
    py = 300

This vector points sideways relative to the direct path.

------------------------------------------------------------------------

## 5. Step 3 -- Normalize the Perpendicular Vector

Normalize to length 1:

    length = sqrt(px² + py²)
           = sqrt(200² + 300²)
           = sqrt(130000)
           ≈ 360.56

Normalized vector:

    px = -200 / 360.56 ≈ -0.555
    py =  300 / 360.56 ≈  0.832

------------------------------------------------------------------------

## 6. Step 4 -- Random Arc Offset

From the code:

``` python
arc_scale = random.uniform(-0.2, 0.2)
offset_x = px * distance * arc_scale
offset_y = py * distance * arc_scale
```

Assume:

    arc_scale = 0.1

Then:

    offset_x = -0.555 * 360.56 * 0.1 ≈ -20
    offset_y =  0.832 * 360.56 * 0.1 ≈  30

This offset bends the path.

------------------------------------------------------------------------

## 7. Step 5 -- Compute Bezier Control Points

Control points are placed **along the path** but shifted sideways.

### Control Point C1 (25% of the path)

    C1_x = start_x + 0.25*dx + offset_x
         = 100 + 75 - 20
         = 155

    C1_y = start_y + 0.25*dy + offset_y
         = 100 + 50 + 30
         = 180

    C1 = (155, 180)

------------------------------------------------------------------------

### Control Point C2 (75% of the path)

    C2_x = start_x + 0.75*dx + offset_x
         = 100 + 225 - 20
         = 305

    C2_y = start_y + 0.75*dy + offset_y
         = 100 + 150 + 30
         = 280

    C2 = (305, 280)

------------------------------------------------------------------------

## 8. XY Graph Diagram

![Coordinate System Diagram](chart.png)

*   **Dashed line**: Robotic straight path
*   **Curved line**: Human-like Bezier movement
*   **Start/End**: The mouse journey
*   **C1/C2**: Invisible control points pulling the curve

------------------------------------------------------------------------

## 9. Bezier Curve Mathematical Formula

Cubic Bezier equation:

    B(t) = (1−t)³S
         + 3(1−t)²tC1
         + 3(1−t)t²C2
         + t³E

Where: - `t ∈ [0, 1]` - `B(0) = Start` - `B(1) = End`

------------------------------------------------------------------------

## 10. Example: Bezier Point at t = 0.5

### X coordinate:

    B_x(0.5) =
    (0.5³ * 100)
    + 3*(0.5²*0.5*155)
    + 3*(0.5*0.5²*305)
    + (0.5³ * 400)

    ≈ 235

### Y coordinate:

    B_y(0.5) =
    (0.5³ * 100)
    + 3*(0.5²*0.5*180)
    + 3*(0.5*0.5²*280)
    + (0.5³ * 300)

    ≈ 223

So the midpoint lies at:

    (235, 223)

------------------------------------------------------------------------

## 11. Acceleration (Ease-In-Out)

The function applies an **Ease-In-Out Quadratic** easing to the time variable `t`. This transforms linear time (constant speed) into "perceived" time `alpha` (variable speed).

![Acceleration Graph](chart2.png)

### The Math

We use a piecewise function based on the progress `t` (from 0 to 1):

1. **Acceleration Phase** (Start to Halfway, `t < 0.5`):
   ```math
   alpha = 2 * t^2
   ```
   *   At `t=0`, speed is 0.
   *   Velocity increases linearly.

2. **Deceleration Phase** (Halfway to End, `t >= 0.5`):
   ```math
   alpha = -1 + (4 - 2 * t) * t
   ```
   *   This is an inverted parabola.
   *   Velocity decreases linearly to 0 at the end.

### Why this specific formula?

At the midpoint `t = 0.5`:
*   **Formula 1:** $2 * (0.5)^2 = 0.5$
*   **Formula 2:** $-1 + (4 - 1) * 0.5 = 0.5$

The values match perfectly, and more importantly, the **derivative (speed)** matches, ensuring a perfectly smooth transition with no "jerk" at the halfway point. This mimics the physics of a hand starting a movement, reaching peak speed, and slowing down to stop.

## 12. Why This Looks Human

  Feature                Effect
  ---------------------- ---------------
  Perpendicular offset   Curved motion
  Random arc             No repetition
  Bezier curve           Smooth path
  Ease-in-out            Natural speed

------------------------------------------------------------------------

## 13. Final Result

✔ Natural-looking mouse movement\
✔ Hard to distinguish from real user\
✔ Smooth curves and timing\
✔ No sharp jumps

------------------------------------------------------------------------

### End of Detailed Explanation
