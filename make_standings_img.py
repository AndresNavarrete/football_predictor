import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


def ax_logo(ax, team_name):
    club_icon = Image.open(f"img/{team_name}.png")
    ax.imshow(club_icon)
    ax.axis("off")
    return ax


def get_df(standings_path):
    df = pd.read_csv(standings_path)
    df["pos"] = df.reset_index().index + 1
    df.drop(columns=df.columns[0], axis=1, inplace=True)
    df = df[["pos", "team", "matches", "points"]].sort_values(
        by="points", ascending=True
    )
    return df


standings_path = "data/forecast/standings.csv"
table_image_path = "img/standings_forecast.png"

df = get_df(standings_path)
fig = plt.figure(figsize=(7, 10), dpi=300)
ax = plt.subplot()

ncols = len(list(df))
nrows = df.shape[0]

ax.set_xlim(0, ncols + 1)
ax.set_ylim(0, nrows)

positions = [0.25, 2.5, 3.5, 4.5, 5.5]
columns = list(df)


# Add table's main text
for i in range(nrows):
    for j, column in enumerate(columns):
        if j == 0:
            ha = "left"
        else:
            ha = "center"
        ax.annotate(
            text=df[column].iloc[i],
            xy=(positions[j], i + 0.5),
            ha=ha,
            va="center",
        )

# -- Transformation functions
DC_to_FC = ax.transData.transform
FC_to_NFC = fig.transFigure.inverted().transform
# -- Take data coordinates and transform them to normalized figure coordinates
DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
# -- Add nation axes
ax_point_1 = DC_to_NFC([2.25, 0.25])
ax_point_2 = DC_to_NFC([2.75, 0.75])
ax_width = abs(ax_point_1[0] - ax_point_2[0])
ax_height = abs(ax_point_1[1] - ax_point_2[1])
for x in range(0, nrows):
    team_name = s = df["team"].iloc[x]
    ax_coords = DC_to_NFC([1.25, x + 0.25])
    flag_ax = fig.add_axes([ax_coords[0], ax_coords[1], ax_width, ax_height])
    ax_logo(flag_ax, team_name)


# Add column names
column_names = ["Position", "Team", "Matches", "Points"]
for index, c in enumerate(column_names):
    if index == 0:
        ha = "left"
    else:
        ha = "center"
    ax.annotate(
        text=column_names[index],
        xy=(positions[index], nrows),
        ha=ha,
        va="bottom",
        weight="bold",
    )

# Add dividing lines
ax.plot(
    [ax.get_xlim()[0], ax.get_xlim()[1]],
    [nrows, nrows],
    lw=1.5,
    color="black",
    marker="",
    zorder=4,
)
ax.plot(
    [ax.get_xlim()[0], ax.get_xlim()[1]],
    [0, 0],
    lw=1.5,
    color="black",
    marker="",
    zorder=4,
)
for x in range(1, nrows):
    ax.plot(
        [ax.get_xlim()[0], ax.get_xlim()[1]],
        [x, x],
        lw=1.15,
        color="gray",
        ls=":",
        zorder=3,
        marker="",
    )

ax.set_axis_off()
plt.savefig(table_image_path, dpi=600, transparent=False, bbox_inches="tight")
