from cProfile import label
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
from matplotlib.backend_bases import MouseButton
from matplotlib.widgets import Slider, Button
import warnings

warnings.filterwarnings('ignore')

def plt1_on_click(event):
    if event.button is MouseButton.LEFT and event.inaxes in axes:
        lbls = event.inaxes.get_xticklabels()
        idx = int(event.xdata.round())
        lbl = lbls[idx]
        global kw
        global wg
        if event.inaxes == axes[0]:
            kw = lbl.get_text()
        elif event.inaxes == axes[1]:
            wg = lbl.get_text()

        if event.inaxes in axes:
            update()
            

def bar_show_val(ax):
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))

    

conString = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=./IETF.accdb;'
conn = pyodbc.connect(conString)

fig, axes = plt.subplots(nrows=1, ncols=4)
kw = ''
wg = ''

start_year = 1969
end_year = 2022
sql1 = '''SELECT [RFC-keyword].keyword, Count(*) AS RFCs
FROM [RFC-keyword] INNER JOIN [RFC-year] ON [RFC-keyword].RFC = [RFC-year].RFC
WHERE [RFC-year].year >= ? AND [RFC-year].year <= ?
GROUP BY [RFC-keyword].keyword
ORDER BY Count(*) DESC'''

sql2 = '''SELECT [RFC-WG].WG, Count(*) AS RFCs
FROM ([RFC-keyword] INNER JOIN [RFC-WG] ON [RFC-keyword].RFC = [RFC-WG].RFC) INNER JOIN [RFC-year] ON [RFC-WG].RFC = [RFC-year].RFC
WHERE ((([RFC-keyword].keyword)= ? )) and [RFC-year].year >= ? and [RFC-year].year <= ?
GROUP BY [RFC-WG].WG
ORDER BY Count(*) DESC'''

sql3 = '''SELECT [RFC-year].Year, Count(*) AS RFCs
FROM [RFC-keyword] INNER JOIN ([RFC-WG] INNER JOIN [RFC-year] ON [RFC-WG].RFC = [RFC-year].RFC) ON [RFC-keyword].RFC = [RFC-WG].RFC
WHERE ((([RFC-WG].WG)=?) AND (([RFC-keyword].keyword)=?) AND (([RFC-year].year)>=? And ([RFC-year].year)<=?))
GROUP BY [RFC-year].Year
ORDER BY [RFC-year].Year'''

sql4 = '''SELECT [RFC-year].Year, Count(*) AS RFCs
FROM [RFC-keyword] INNER JOIN [RFC-year] ON [RFC-keyword].RFC = [RFC-year].RFC
WHERE [RFC-keyword].keyword = ?
GROUP BY [RFC-year].Year
ORDER BY [RFC-year].Year;'''

kw_group = pd.read_sql_query(sql1, conn, params=[start_year, end_year])
kw_group = kw_group.head(10)


axstart = plt.axes([0.3, 0.95, 0.5, 0.02])
start_year_slider = Slider(
    ax = axstart,
    label="Start year",
    valmin = 1969,
    valmax = 2022,
    valinit = 1969,
    valfmt='%0.0f'
)

axend = plt.axes([0.3, 0.9, 0.5, 0.02])
end_year_slide = Slider(
    ax=axend,
    label="End year",
    valmin=1969,
    valmax=2022,
    valinit=2022,
    valfmt='%0.0f'
)

def update():
    kw_group = pd.read_sql_query(sql1, conn, params=[start_year, end_year])
    kw_group = kw_group.head(10)
    axes[0].cla()
    kw_group.plot.bar(x='keyword', y='RFCs', ax=axes[0], title=f'{start_year}~{end_year}')
    bar_show_val(axes[0])

    if kw != '':
        wg_group = pd.read_sql_query(sql2, conn, params=[kw, start_year, end_year])
        wg_group = wg_group.head(10)
        axes[1].cla()
        wg_group.plot.bar(x='WG', y='RFCs', ax=axes[1], title=f'{start_year}~{end_year}   kw:{kw}')
        bar_show_val(axes[1])

        kw_trend = pd.read_sql_query(sql4, conn, params=[kw])
        axes[2].cla()
        kw_trend.plot.line(x='Year', y='RFCs', ax=axes[2], title=f'{start_year}~{end_year}   kw:{kw}', style='o-')

    if kw != '' and wg != '':
        year_group = pd.read_sql_query(sql3, conn, params=[wg, kw, start_year, end_year])
        axes[3].cla()
        year_group.plot.line(x='Year', y='RFCs', ax=axes[3], title=f'kw:{kw}   wg:{wg}', style='o-')
        axes[3].yaxis.set_major_locator(MultipleLocator(1))

    fig.canvas.draw()


def start_change(val):
    if val <= end_year:
        global start_year
        start_year = round(val)
        update()

def end_change(val):
    if val >= start_year:
        global end_year
        end_year = round(val)
        update()
    

start_year_slider.on_changed(start_change)
end_year_slide.on_changed(end_change)


plt.connect('button_press_event', plt1_on_click)
update()
plt.show()