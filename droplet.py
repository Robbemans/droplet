from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox


def pick_image_file():
    root = tk.Tk()
    root.withdraw() 
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="Select an image for contact angle measurement",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
            ("All files", "*.*"),
        ],
    )
    root.destroy()
    return path


def popup_info(title, text):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, text)
    root.destroy()


def popup_error(title, text):
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showerror(title, text)
    root.destroy()


def fit_circle_least_squares(points):
    x = points[:, 0]
    y = points[:, 1]

    A = np.column_stack([x, y, np.ones_like(x)])
    b = x * x + y * y

    p, *_ = np.linalg.lstsq(A, b, rcond=None)
    D, E, F = p

    cx = D / 2.0
    cy = E / 2.0
    r = np.sqrt(max(0.0, cx * cx + cy * cy + F))
    return (cx, cy), r


def contact_angle_deg(cyp, r):
    if not np.isfinite(r) or r <= 0:
        return None
    return float(np.degrees(np.arccos(np.clip(cyp / r, -1.0, 1.0))))

IMAGE_PATH = pick_image_file()
if not IMAGE_PATH:
    popup_error("No image selected", "You didn't select an image. Exiting.")
    raise SystemExit(1)
try:
    img = mpimg.imread(IMAGE_PATH)
except Exception as e:
    popup_error("Failed to load image", f"Could not load:\n{IMAGE_PATH}\n\nError:\n{e}")
    raise SystemExit(1)

h, w = img.shape[:2]


baseline_pts = []  
edge_pts = []       
done = False

fig, ax = plt.subplots(figsize=(10, 7))
ax.set_title("Click 2 baseline points, then many edge points. Right-click to finish/reset.")
ax.imshow(img, origin="upper")
ax.set_xlim(0, w)
ax.set_ylim(h, 0)

status = ax.text(
    0.02, 0.98, "Baseline: 0/2 | Edge: 0 | Right-click = finish/reset",
    transform=ax.transAxes, va="top",
    bbox=dict(boxstyle="round", alpha=0.2)
)

baseline_line, = ax.plot([], [], linewidth=2)
circle_line, = ax.plot([], [], linewidth=2)

def update_status():
    status.set_text(
        f"Baseline: {len(baseline_pts)}/2 | Edge: {len(edge_pts)} | "
        f"{'Right-click = reset' if done else 'Right-click = finish'}"
    )

def reset():
    global baseline_pts, edge_pts, done
    baseline_pts = []
    edge_pts = []
    done = False
    ax.collections.clear()
    baseline_line.set_data([], [])
    circle_line.set_data([], [])
    update_status()
    fig.canvas.draw()

def compute_and_draw():
    global done
    done = True

    if len(baseline_pts) < 2:
        popup_error("Not enough baseline points", "Click 2 baseline points first.")
        done = False
        return

    A_img = np.array(baseline_pts[0], dtype=float)
    B_img = np.array(baseline_pts[1], dtype=float)

    AB = B_img - A_img
    L = np.linalg.norm(AB)
    if L < 1e-9:
        popup_error("Bad baseline", "Your two baseline points are basically the same spot. Try again.")
        done = False
        return

    e1 = AB / L
    e2 = np.array([-e1[1], e1[0]])

    def to_prime(P_img):
        v = P_img - A_img
        return np.array([np.dot(v, e1), np.dot(v, e2)])

    def from_prime(P_p):
        return A_img + P_p[0] * e1 + P_p[1] * e2

    if len(edge_pts) < 5:
        popup_error("Not enough edge points", "Click more points on the droplet edge (higher up), then right-click.")
        done = False
        return

    E_p = np.array([to_prime(np.array(p, dtype=float)) for p in edge_pts])

    dist_from_baseline = np.abs(E_p[:, 1])
    E_p = E_p[dist_from_baseline > 0.02 * L] 

    if E_p.shape[0] < 5:
        popup_error(
            "Edge points too close to baseline",
            "Most of your edge clicks are basically on the baseline.\n"
            "Click higher on the droplet outline (upper contour)."
        )
        done = False
        return

    center_p, r = fit_circle_least_squares(E_p)
    cxp, cyp = center_p

    theta = contact_angle_deg(cyp, r)
    if theta is None:
        popup_error("Bad fit", "Circle fit failed (radius invalid). Try clicking cleaner edge points.")
        done = False
        return
    baseline_line.set_data([A_img[0], B_img[0]], [A_img[1], B_img[1]])

    t = np.linspace(0, 2*np.pi, 600)
    circle_p = np.column_stack([cxp + r*np.cos(t), cyp + r*np.sin(t)])
    circle_img = np.array([from_prime(Pp) for Pp in circle_p])
    circle_line.set_data(circle_img[:, 0], circle_img[:, 1])

    fig.canvas.draw()

    popup_info(
        "Contact angle result",
        f"Contact angle: {theta:.2f}°\n\n"
        f"Circle center (primed): ({cxp:.2f}, {cyp:.2f})\n"
        f"Radius: {r:.2f}\n"
        f"Edge points used: {E_p.shape[0]}"
    )

def onclick(event):
    if event.inaxes != ax or event.xdata is None or event.ydata is None:
        return

    if event.button == 3:
        if not done and len(baseline_pts) == 2 and len(edge_pts) >= 5:
            compute_and_draw()
            update_status()
        else:
            reset()
        return

    x, y = float(event.xdata), float(event.ydata)

    if len(baseline_pts) < 2:
        baseline_pts.append((x, y))
        ax.scatter(x, y, s=90, zorder=5)
        if len(baseline_pts) == 2:
            A, B = baseline_pts
            baseline_line.set_data([A[0], B[0]], [A[1], B[1]])
        update_status()
        fig.canvas.draw()
        return

    if done:
        return 

    edge_pts.append((x, y))
    ax.scatter(x, y, s=45, zorder=5)
    update_status()
    fig.canvas.draw()

update_status()
cid = fig.canvas.mpl_connect("button_press_event", onclick)
plt.show()
