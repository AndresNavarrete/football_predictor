import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image


class TableCreator:
    def __init__(self):
        self.con = duckdb.connect()
        self.current_standings_path = "./data/forecast/current_standings.csv"
        self.standings_path = "./data/forecast/standings.csv"
        self.table_image_path = "./img/out/standings_forecast.png"
        self.positions = [0.3, 1.25, 3.5, 4.5, 5.5]
        self.current_standings = None
        self.df = None
        self.fig = None
        self.ax = None

    def execute(self):
        self.set_df()
        self.set_figure()
        self.add_main_text()
        self.add_team_logos()
        self.add_columns_names()
        self.add_lines()
        self.save_img()

    def set_df(self):
        prediction = self.get_df(self.standings_path)
        current = self.get_df(self.current_standings_path)

        query = """
        SELECT
            p.pos,
            c.pos AS current_pos,
            p.team,
            p.points 
        FROM
            prediction p 
        LEFT JOIN
            current c USING(team)
        """
        self.df = self.con.execute(query).df()

    def get_df(self, standings_path):
        df = pd.read_csv(standings_path)
        df["pos"] = df.reset_index().index + 1
        df.drop(columns=df.columns[0], axis=1, inplace=True)
        df = df[["pos", "team", "matches", "points"]].sort_values(
            by="points", ascending=True
        )
        return df

    def set_figure(self):
        self.fig = plt.figure(figsize=(7, 10), dpi=300)
        self.ax = plt.subplot()

        self.columns = list(self.df)
        self.ncols = len(list(self.df))
        self.nrows = self.df.shape[0]

        self.ax.set_xlim(0, self.ncols + 1)
        self.ax.set_ylim(0, self.nrows)

    def add_main_text(self):
        for i in range(self.nrows):
            for j, column in enumerate(self.columns):
                ha = "center"
                self.ax.annotate(
                    text=self.df[column].iloc[i],
                    xy=(self.positions[j], i + 0.5),
                    ha=ha,
                    va="center",
                )

    def add_team_logos(self):
        DC_to_FC = self.ax.transData.transform
        FC_to_NFC = self.fig.transFigure.inverted().transform
        DC_to_NFC = lambda x: FC_to_NFC(DC_to_FC(x))
        ax_point_1 = DC_to_NFC([2.2, 0.2])
        ax_point_2 = DC_to_NFC([2.9, 0.8])
        ax_width = abs(ax_point_1[0] - ax_point_2[0])
        ax_height = abs(ax_point_1[1] - ax_point_2[1])
        for x in range(0, self.nrows):
            team_name = self.df["team"].iloc[x]
            ax_coords = DC_to_NFC([2.15, x + 0.25])
            flag_ax = self.fig.add_axes(
                [ax_coords[0], ax_coords[1], ax_width, ax_height]
            )
            self.ax_logo(flag_ax, team_name)

    def ax_logo(self, flag_ax, team_name):
        club_icon = Image.open(f"img/{team_name}.png")
        flag_ax.imshow(club_icon)
        flag_ax.axis("off")
        return flag_ax

    def add_columns_names(self):
        column_names = ["Forecast", "Current", "Team", "Points"]
        for index, col in enumerate(column_names):
            ha = "center"
            self.ax.annotate(
                text=col,
                xy=(self.positions[index], self.nrows),
                ha=ha,
                va="bottom",
                weight="bold",
            )

    def add_lines(self):
        self.ax.plot(
            [self.ax.get_xlim()[0], self.ax.get_xlim()[1]],
            [self.nrows, self.nrows],
            lw=1.5,
            color="black",
            marker="",
            zorder=4,
        )
        self.ax.plot(
            [self.ax.get_xlim()[0], self.ax.get_xlim()[1]],
            [0, 0],
            lw=1.5,
            color="black",
            marker="",
            zorder=4,
        )
        for x in range(1, self.nrows):
            self.ax.plot(
                [self.ax.get_xlim()[0], self.ax.get_xlim()[1]],
                [x, x],
                lw=1.15,
                color="gray",
                ls=":",
                zorder=3,
                marker="",
            )

    def save_img(self):
        self.ax.set_axis_off()
        plt.savefig(
            self.table_image_path,
            dpi=600,
            transparent=False,
            bbox_inches="tight",
        )


if __name__ == "__main__":
    foo = TableCreator()
    foo.execute()
