# Droplet — Contact Angle Measurement Tool

A small Python tool for measuring the **static (sessile-drop) contact angle** of a liquid droplet from a side-on photograph. The user marks the baseline and a set of points along the droplet outline; the tool fits a circle to those points and calculates the contact angle from the fitted circle.

It is intended as a simple, low-cost alternative to a dedicated optical tensiometer. Because the points are placed by hand, the result is a reasonable estimate rather than a laboratory-grade measurement (see **Limitations**).

---

## Requirements

- Python 3.8 or newer
- [NumPy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- Tkinter (used for the file picker and pop-up dialogs)

Tkinter ships with most Python installations. On some Linux distributions it must be installed separately, for example:

```bash
sudo apt-get install python3-tk
```

## Installation

```bash
pip install numpy matplotlib
```

Then save the script (for example as `droplet.py`) and run it.

---

## Usage

1. Run the script:

   ```bash
   python droplet.py
   ```

2. A file dialog opens — select a side-on image of the droplet (`.png`, `.jpg`, `.jpeg`, `.bmp`, `.tif`, `.tiff`).

3. The image opens in a window. Using the mouse:

   1. **Left-click the two baseline points** — the left and right points where the droplet meets the surface. A line is drawn between them.
   2. **Left-click points along the droplet outline** — follow the curved upper edge of the drop. Use at least 5 points; **10 or more, spread across the arc, gives a better fit.**
   3. **Right-click to finish.** The tool fits a circle, draws it on the image, and shows the contact angle in a pop-up.

4. **Right-click again** (or right-click at any time before finishing) to **reset** and start over.

The status text in the top-left corner shows how many baseline and outline points have been placed.

> **Tip:** measure each droplet in triplicate and average the results.

### Controls

| Action | Result |
|---|---|
| Left-click (first 2) | Set the baseline points |
| Left-click (remaining) | Add droplet-outline points |
| Right-click (when ready) | Fit the circle and show the contact angle |
| Right-click (otherwise) | Reset all points |

---

## How it works

1. The two baseline points define the **baseline** (the solid surface).
2. The outline points are transformed into a coordinate frame aligned with the baseline. Points lying very close to the baseline (within 2 % of its length) are discarded automatically, as they are the least reliable.
3. A **circle is fitted to the outline points by least squares**, on the assumption that the droplet profile is approximately a circular arc (a spherical cap).
4. The **contact angle** is taken as the angle between the baseline and the tangent to the fitted circle at the point where the circle meets the baseline. Equivalently:

   ```
   θ = arccos( d / r )
   ```

   where `r` is the fitted radius and `d` is the perpendicular distance from the circle's centre to the baseline (signed: the centre on the far side of the baseline from the droplet gives θ < 90°, on the same side gives θ > 90°).

Because the angle depends only on the ratio `d / r`, the result is **independent of image scale** — no pixel-to-millimetre calibration is required.

## Output

- The **contact angle in degrees** (two decimal places), shown in a pop-up dialog.
- The **fitted circle and baseline** drawn over the image, so the fit can be checked by eye.

---

## Recommendations for good measurements

- Photograph the droplet **from the side, with the camera level** with the surface.
- Use a clean, evenly lit, high-contrast image so the droplet edge is easy to see.
- Place outline points on the **upper curve** of the drop and **spread them out**; avoid clustering them near the contact line.
- Keep the droplet **small** (see Limitations).

## Limitations

- **Operator-dependent.** The baseline and outline points are placed manually, so the result depends somewhat on the user. This is why measurements should be repeated and averaged, and why a dedicated optical tensiometer is preferable for precise work.
- **Spherical-cap assumption.** Fitting a circle assumes gravity does not noticeably distort the droplet. This holds for small drops (below the capillary length, a few millimetres for water); for larger drops the profile flattens and the angle is underestimated.
- **Static angle only.** The tool returns a single static (sessile-drop) contact angle. It does **not** measure advancing or receding angles, or contact-angle hysteresis.
- **Single circle fit.** One circle is fitted to all outline points, so left–right asymmetry (for example from a slightly tilted camera) is absorbed into the fit rather than corrected.

---

## Notes

This tool was developed as part of an internship project on the separation of PVC and LDPE by flotation following surface treatment with ferrate(VI) solution (FerSol®), where it was used to measure how the treatment changed the wettability of the plastics.
